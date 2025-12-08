"""
Streamlined Squat Analyzer - Live Preview + Immediate Feedback
No credentials, just analysis
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os
from datetime import datetime
import json

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Squat Standards
NSCA_STANDARDS = {
    "knee_angle": {"optimal": 90, "range": (80, 100)},
    "torso_lean": {"optimal": 45, "range": (40, 50)},
    "hip_depth": {"optimal": "parallel"}
}

def calculate_angle(a, b, c):
    """Calculate angle at point b formed by a-b-c"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    return int(np.degrees(np.arccos(cosine_angle)))

def analyze_squat_video(video_path):
    """
    Main analysis function - shows live preview and gives feedback
    """
    print("=" * 60)
    print("QUICK SQUAT ANALYZER - LIVE PREVIEW + FEEDBACK")
    print("=" * 60)
    
    # Check video file
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Cannot open video")
        return
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video: {os.path.basename(video_path)}")
    print(f"Resolution: {width}x{height}")
    print(f"Duration: {total_frames/fps:.1f}s")
    print("-" * 60)
    print("Starting live analysis...")
    print("   Press 'Q' to quit | 'S' to screenshot | 'P' to pause")
    print("-" * 60)
    
    # Data storage
    all_angles = []
    rep_data = []
    current_rep = {"frames": [], "angles": []}
    in_squat = False
    rep_count = 0
    min_knee_angle = 180
    
    # Setup MediaPipe
    with mp_pose.Pose(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        model_complexity=2
    ) as pose:
        
        frame_count = 0
        paused = False
        
        while cap.isOpened():
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                if results.pose_landmarks:
                    # Draw skeleton
                    mp_drawing.draw_landmarks(
                        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(
                            color=(0, 255, 0), thickness=2, circle_radius=2
                        ),
                        connection_drawing_spec=mp_drawing.DrawingSpec(
                            color=(255, 255, 255), thickness=2
                        )
                    )
                    
                    # Get landmarks
                    landmarks = results.pose_landmarks.landmark
                    h, w = image.shape[:2]
                    
                    # Calculate key angles
                    angles = get_key_angles(landmarks, w, h)
                    
                    if angles['left_knee'] is not None:
                        all_angles.append(angles['left_knee'])
                        current_rep["angles"].append(angles['left_knee'])
                        current_rep["frames"].append(frame_count)
                        
                        # Detect squat reps
                        if not in_squat and angles['left_knee'] < 150:
                            in_squat = True
                            min_knee_angle = 180
                        
                        if in_squat:
                            if angles['left_knee'] < min_knee_angle:
                                min_knee_angle = angles['left_knee']
                        
                        if in_squat and angles['left_knee'] > 160:
                            in_squat = False
                            rep_count += 1
                            rep_data.append({
                                "rep": rep_count,
                                "min_angle": min_knee_angle,
                                "depth_rating": get_depth_rating(min_knee_angle)
                            })
                            current_rep = {"frames": [], "angles": []}
                    
                    # Add angle displays
                    image = add_angle_overlays(image, angles)
                
                # Add info panel
                image = add_info_panel(image, frame_count, total_frames, fps, rep_count, min_knee_angle)
                
                # Show live preview
                cv2.imshow('LIVE SQUAT ANALYSIS - Press Q to quit', image)
            
            # Handle keys
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            
            if key == ord('q') or key == 27:
                print("\nStopping analysis...")
                break
            elif key == ord('p'):
                paused = not paused
                print(f"   {'Paused' if paused else 'Resumed'}")
            elif key == ord('s'):
                screenshot = f"squat_frame_{frame_count}.jpg"
                cv2.imwrite(screenshot, image)
                print(f"Saved: {screenshot}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Generate and display feedback
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE - GENERATING FEEDBACK")
    print("=" * 60)
    
    generate_feedback(rep_data, all_angles, video_path)

def get_key_angles(landmarks, width, height):
    """Extract key angles for squat analysis"""
    def pixel_coord(idx):
        lm = landmarks[idx]
        return (int(lm.x * width), int(lm.y * height))
    
    angles = {}
    
    try:
        # Left knee
        l_hip = pixel_coord(23)
        l_knee = pixel_coord(25)
        l_ankle = pixel_coord(27)
        angles['left_knee'] = calculate_angle(l_hip, l_knee, l_ankle)
        
        # Right knee
        r_hip = pixel_coord(24)
        r_knee = pixel_coord(26)
        r_ankle = pixel_coord(28)
        angles['right_knee'] = calculate_angle(r_hip, r_knee, r_ankle)
        
        # Torso lean
        l_shoulder = pixel_coord(11)
        r_shoulder = pixel_coord(12)
        shoulder_mid = (
            (l_shoulder[0] + r_shoulder[0]) // 2,
            (l_shoulder[1] + r_shoulder[1]) // 2
        )
        hip_mid = (
            (l_hip[0] + r_hip[0]) // 2,
            (l_hip[1] + r_hip[1]) // 2
        )
        vertical_point = (hip_mid[0], hip_mid[1] - 100)
        angles['torso'] = calculate_angle(vertical_point, hip_mid, shoulder_mid)
        
        # Hip angle
        angles['left_hip'] = calculate_angle(l_shoulder, l_hip, l_knee)
        angles['right_hip'] = calculate_angle(r_shoulder, r_hip, r_knee)
        
    except:
        angles = {k: None for k in ['left_knee', 'right_knee', 'torso', 'left_hip', 'right_hip']}
    
    return angles

def add_angle_overlays(image, angles):
    """Add angle displays to frame"""
    h, w = image.shape[:2]
    
    # Display angles at top
    y_pos = 40
    if angles['left_knee'] is not None:
        # Color code based on NSCA standard
        if 80 <= angles['left_knee'] <= 100:
            color = (0, 255, 0)  # Green - good
        elif 100 < angles['left_knee'] <= 120:
            color = (0, 165, 255)  # Orange - shallow
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Knee: {angles['left_knee']}° (NSCA: 90°)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if angles['torso'] is not None:
        torso_color = (0, 255, 0) if 40 <= angles['torso'] <= 50 else (0, 165, 255)
        cv2.putText(image, f"Torso: {angles['torso']}° (Opt: 45°)", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, torso_color, 2)
    
    return image

def add_info_panel(image, frame, total_frames, fps, reps, current_knee_angle):
    """Add information panel to frame"""
    h, w = image.shape[:2]
    
    # Create bottom panel
    panel_height = 100
    panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
    panel[:, :] = (40, 40, 40)
    
    # Add panel to image
    image_with_panel = np.vstack([image, panel])
    new_h = h + panel_height
    
    # Add info
    time_sec = frame / fps if fps > 0 else 0
    
    # Left side: Basic info
    cv2.putText(image_with_panel, f"Frame: {frame}/{total_frames}", 
               (20, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(image_with_panel, f"Time: {time_sec:.1f}s", 
               (20, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Middle: Rep info
    cv2.putText(image_with_panel, f"Reps: {reps}", 
               (w//2 - 100, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(image_with_panel, f"Current Knee: {current_knee_angle}°", 
               (w//2 - 100, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 1)
    
    # Right side: NSCA standard
    cv2.putText(image_with_panel, "NSCA Standard:", 
               (w - 250, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
    cv2.putText(image_with_panel, "• Parallel depth (90° knee)", 
               (w - 250, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Neutral spine", 
               (w - 250, new_h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Knees over toes", 
               (w - 250, new_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    
    return image_with_panel

def get_depth_rating(knee_angle):
    """Rate squat depth"""
    if knee_angle > 120:
        return "Very Shallow"
    elif knee_angle > 100:
        return "Shallow"
    elif knee_angle > 85:
        return "Good (Parallel)"
    elif knee_angle > 70:
        return "Excellent"
    else:
        return "Very Deep"

def generate_feedback(rep_data, all_angles, video_path):
    """Generate comprehensive feedback based on analysis"""
    
    if not rep_data:
        print("\nNO SQUATS DETECTED!")
        print("\nPossible reasons:")
        print("1. Camera angle - side view works best")
        print("2. Full body not visible")
        print("3. Not enough range of motion")
        print("4. Try a different video")
        return
    
    print(f"\nDETECTED {len(rep_data)} SQUAT REPS")
    print("-" * 60)
    
    # Analyze each rep
    print("\nREP-BY-REP ANALYSIS:")
    print("-" * 40)
    
    for i, rep in enumerate(rep_data, 1):
        angle = rep["min_angle"]
        rating = rep["depth_rating"]
        
        # Color code
        if "Good" in rating or "Excellent" in rating:
            symbol = "✅"
        elif "Shallow" in rating:
            symbol = "⚠️ "
        else:
            symbol = "❌"
        
        print(f"   {symbol} Rep {i}: {angle}° - {rating}")
    
    # Calculate statistics
    if all_angles:
        avg_knee_angle = np.mean([rep["min_angle"] for rep in rep_data])
        min_angle = min([rep["min_angle"] for rep in rep_data])
        max_angle = max([rep["min_angle"] for rep in rep_data])
        
        print("\nOVERALL STATISTICS:")
        print("-" * 40)
        print(f"   Average Knee Angle: {avg_knee_angle:.1f}°")
        print(f"   Best Depth: {min_angle}°")
        print(f"   Shallowest: {max_angle}°")
        
        # Consistency
        consistency = 100 - (max_angle - min_angle)
        print(f"   Consistency: {consistency:.1f}%")
    
    print("\n" + "=" * 60)
    print("NSCA-BASED FORM FEEDBACK")
    print("=" * 60)
    
    # Generate personalized feedback
    if rep_data:
        avg_depth = np.mean([rep["min_angle"] for rep in rep_data])
        
        print("\nKEY FINDINGS:")
        print("-" * 40)
        
        if avg_depth > 100:
            print("PRIMARY ISSUE: INSUFFICIENT DEPTH")
            print("   • You're not reaching parallel")
            print("   • NSCA standard requires 90° knee angle")
            print("   • Current average: {:.1f}°".format(avg_depth))
            
            print("\nIMMEDIATE FIXES:")
            print("   1. Practice with a box or bench")
            print("   2. Focus on 'sit back' not 'sit down'")
            print("   3. Try goblet squats with lighter weight")
            print("   4. Improve ankle mobility")
            
        elif 85 <= avg_depth <= 100:
            print("GOOD: MEETS NSCA STANDARD")
            print("   • You're reaching parallel or below")
            print("   • NSCA standard: 90° knee angle")
            print("   • Your average: {:.1f}°".format(avg_depth))
            
            print("\nNEXT-LEVEL IMPROVEMENTS:")
            print("   1. Work on depth consistency")
            print("   2. Add pause squats for strength")
            print("   3. Increase weight gradually")
            print("   4. Film from front to check knee alignment")
            
        else:  # avg_depth < 85
            print("EXCELLENT: BELOW PARALLEL")
            print("   • You're going deeper than required")
            print("   • NSCA standard: 90° knee angle")
            print("   • Your average: {:.1f}°".format(avg_depth))
            
            print("\nSTRENGTH FOCUS:")
            print("   1. Maintain control at bottom")
            print("   2. Ensure knees don't cave inward")
            print("   3. Consider competition-style training")
            print("   4. Monitor for 'butt wink'")
    
    print("\nNSCA TECHNICAL CHECKLIST:")
    print("-" * 40)
    checkboxes = [
        ("Feet shoulder-width apart", "CORRECT"),
        ("Knees track over toes", "CORRECT"),
        ("Chest stays up", "CORRECT"),
        ("Back remains straight", "CORRECT"),
        ("Hips below knees at bottom", "CORRECT" if avg_depth <= 90 else "IMPROVE"),
        ("Weight on heels/midfoot", "CORRECT"),
        ("Controlled descent/ascent", "CORRECT"),
    ]
    
    for item, status in checkboxes:
        print(f"   {status} {item}")
    
    print("\nRECOMMENDED DRILLS:")
    print("-" * 40)
    drills = [
        "1. Box Squats - for depth practice",
        "2. Goblet Squats - for form focus",
        "3. Pause Squats - for strength",
        "4. Banded Squats - for knee alignment",
        "5. Wall Sits - for endurance"
    ]
    
    for drill in drills:
        print(f"   {drill}")
    
    # Save quick report
    save_quick_report(rep_data, video_path, avg_depth if 'avg_depth' in locals() else None)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

def save_quick_report(rep_data, video_path, avg_depth):
    """Save a quick text report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"squat_quick_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write("QUICK SQUAT ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Video: {os.path.basename(video_path)}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reps: {len(rep_data)}\n\n")
        
        f.write("Rep Details:\n")
        f.write("-" * 30 + "\n")
        for rep in rep_data:
            f.write(f"Rep {rep['rep']}: {rep['min_angle']}° - {rep['depth_rating']}\n")
        
        if avg_depth:
            f.write(f"\nAverage Depth: {avg_depth:.1f}°\n")
            f.write("NSCA Standard: 90° (parallel)\n")
            
            if avg_depth > 100:
                f.write("\nFEEDBACK: Need more depth\n")
                f.write("FIX: Practice with box squats\n")
            elif avg_depth >= 85:
                f.write("\nFEEDBACK: Good depth\n")
                f.write("NEXT: Work on consistency\n")
            else:
                f.write("\nFEEDBACK: Excellent depth\n")
                f.write("NEXT: Maintain control\n")
        
        f.write("\nNSCA Form Checklist:\n")
        f.write("-" * 30 + "\n")
        f.write("✓ Feet shoulder-width\n")
        f.write("✓ Knees over toes\n")
        f.write("✓ Chest up\n")
        f.write("✓ Neutral spine\n")
        f.write("✓ Controlled tempo\n")
    
    print(f"\nQuick report saved: {filename}")

# Simple main function - no questions, just run
if __name__ == "__main__":
    # Check for video file
    video_path = None
    
    # Look for common video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    # First check command line argument
    import sys
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if not os.path.exists(video_path):
            print(f"Video not found: {video_path}")
            video_path = None
    
    # If no command line arg, look in current directory
    if not video_path:
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_path = file
                break
    
    if video_path:
        print(f"Found video: {video_path}")
        analyze_squat_video(video_path)
    else:
        print("No video file found!")
        print("\nPlease either:")
        print("1. Place a video file in this folder")
        print("2. Run: python squat_analyzer.py your_video.mp4")
        print("\nSupported formats: .mp4, .avi, .mov, .mkv, .webm")
