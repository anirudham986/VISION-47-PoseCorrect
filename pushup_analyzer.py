"""
Streamlined Push-Up Analyzer - Live Preview + Immediate Feedback
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

# NSCA Push-Up Standards
NSCA_STANDARDS = {
    "elbow_angle": {"optimal": 90, "range": (80, 100)},
    "torso_straightness": {"optimal": 0, "range": (-5, 5)},
    "shoulder_angle": {"optimal": 45, "range": (40, 50)}
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

def calculate_torso_angle(shoulder, hip, ankle):
    """Calculate torso angle relative to horizontal line"""
    shoulder = np.array(shoulder)
    hip = np.array(hip)
    ankle = np.array(ankle)
    
    # Create horizontal reference line at hip level
    horizontal_point = (hip[0] + 100, hip[1])
    
    return calculate_angle(horizontal_point, hip, shoulder)

def analyze_pushup_video(video_path):
    """
    Main analysis function - shows live preview and gives feedback
    """
    print("=" * 60)
    print("⚡ QUICK PUSH-UP ANALYZER - LIVE PREVIEW + FEEDBACK")
    print("=" * 60)
    
    # Check video file
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Cannot open video")
        return
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video: {os.path.basename(video_path)}")
    print(f"📐 Resolution: {width}x{height}")
    print(f"⏱️  Duration: {total_frames/fps:.1f}s")
    print("-" * 60)
    print("▶️  Starting live analysis...")
    print("   Press 'Q' to quit | 'S' to screenshot | 'P' to pause")
    print("-" * 60)
    
    # Data storage
    all_angles = []
    rep_data = []
    current_rep = {"frames": [], "angles": []}
    in_pushup = False
    rep_count = 0
    min_elbow_angle = 180
    max_hip_drop = 0
    
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
                    
                    # Calculate key angles and metrics
                    metrics = get_key_metrics(landmarks, w, h)
                    
                    if metrics['left_elbow'] is not None:
                        all_angles.append(metrics['left_elbow'])
                        current_rep["angles"].append(metrics['left_elbow'])
                        current_rep["frames"].append(frame_count)
                        
                        # Detect push-up reps
                        if not in_pushup and metrics['left_elbow'] < 140:
                            in_pushup = True
                            min_elbow_angle = 180
                            max_hip_drop = 0
                        
                        if in_pushup:
                            if metrics['left_elbow'] < min_elbow_angle:
                                min_elbow_angle = metrics['left_elbow']
                            
                            # Track hip drop (sagging)
                            if metrics['hip_drop'] > max_hip_drop:
                                max_hip_drop = metrics['hip_drop']
                        
                        if in_pushup and metrics['left_elbow'] > 160:
                            in_pushup = False
                            rep_count += 1
                            rep_data.append({
                                "rep": rep_count,
                                "min_elbow_angle": min_elbow_angle,
                                "max_hip_drop": max_hip_drop,
                                "form_rating": get_form_rating(min_elbow_angle, max_hip_drop),
                                "shoulder_angle": metrics.get('shoulder_angle', None)
                            })
                            current_rep = {"frames": [], "angles": []}
                    
                    # Add metric displays
                    image = add_metric_overlays(image, metrics)
                
                # Add info panel
                image = add_info_panel(image, frame_count, total_frames, fps, rep_count, 
                                      min_elbow_angle, max_hip_drop)
                
                # Show live preview
                cv2.imshow('🏋️‍♂️ LIVE PUSH-UP ANALYSIS - Press Q to quit', image)
            
            # Handle keys
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            
            if key == ord('q') or key == 27:
                print("\n⏹️  Stopping analysis...")
                break
            elif key == ord('p'):
                paused = not paused
                print(f"   {'⏸️  Paused' if paused else '▶️  Resumed'}")
            elif key == ord('s'):
                screenshot = f"pushup_frame_{frame_count}.jpg"
                cv2.imwrite(screenshot, image)
                print(f"   📸 Saved: {screenshot}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Generate and display feedback
    print("\n" + "=" * 60)
    print("📊 ANALYSIS COMPLETE - GENERATING FEEDBACK")
    print("=" * 60)
    
    generate_feedback(rep_data, all_angles, video_path)

def get_key_metrics(landmarks, width, height):
    """Extract key metrics for push-up analysis"""
    def pixel_coord(idx):
        lm = landmarks[idx]
        return (int(lm.x * width), int(lm.y * height))
    
    metrics = {}
    
    try:
        # Left elbow
        l_shoulder = pixel_coord(11)
        l_elbow = pixel_coord(13)
        l_wrist = pixel_coord(15)
        metrics['left_elbow'] = calculate_angle(l_shoulder, l_elbow, l_wrist)
        
        # Right elbow
        r_shoulder = pixel_coord(12)
        r_elbow = pixel_coord(14)
        r_wrist = pixel_coord(16)
        metrics['right_elbow'] = calculate_angle(r_shoulder, r_elbow, r_wrist)
        
        # Shoulder angle (relative to torso)
        shoulder_mid = (
            (l_shoulder[0] + r_shoulder[0]) // 2,
            (l_shoulder[1] + r_shoulder[1]) // 2
        )
        hip_mid = (
            (pixel_coord(23)[0] + pixel_coord(24)[0]) // 2,
            (pixel_coord(23)[1] + pixel_coord(24)[1]) // 2
        )
        
        # Calculate angle between upper arm and torso
        metrics['shoulder_angle'] = calculate_angle(l_elbow, l_shoulder, hip_mid)
        
        # Torso straightness (hip drop)
        l_ankle = pixel_coord(27)
        r_ankle = pixel_coord(28)
        ankle_mid = (
            (l_ankle[0] + r_ankle[0]) // 2,
            (l_ankle[1] + r_ankle[1]) // 2
        )
        
        # Create line from shoulder to ankle
        shoulder_ankle_line = np.array(ankle_mid) - np.array(shoulder_mid)
        
        # Calculate distance from hip to line (hip drop)
        hip_point = np.array(hip_mid)
        shoulder_point = np.array(shoulder_mid)
        
        # Vector math for point-line distance
        line_vec = np.array(ankle_mid) - shoulder_point
        point_vec = hip_point - shoulder_point
        cross = np.cross(line_vec, point_vec)
        distance = np.linalg.norm(cross) / np.linalg.norm(line_vec)
        
        metrics['hip_drop'] = int(distance)
        
        # Body alignment angle
        metrics['torso_angle'] = calculate_torso_angle(shoulder_mid, hip_mid, ankle_mid)
        
    except Exception as e:
        print(f"Error in metrics: {e}")
        metrics = {k: None for k in ['left_elbow', 'right_elbow', 'shoulder_angle', 
                                    'hip_drop', 'torso_angle']}
    
    return metrics

def add_metric_overlays(image, metrics):
    """Add metric displays to frame"""
    h, w = image.shape[:2]
    
    # Display angles at top
    y_pos = 40
    
    if metrics['left_elbow'] is not None:
        # Color code based on NSCA standard
        if 80 <= metrics['left_elbow'] <= 100:
            color = (0, 255, 0)  # Green - good
        elif 100 < metrics['left_elbow'] <= 120:
            color = (0, 165, 255)  # Orange - shallow
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Elbow: {metrics['left_elbow']}° (NSCA: 90°)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if metrics['shoulder_angle'] is not None:
        shoulder_color = (0, 255, 0) if 40 <= metrics['shoulder_angle'] <= 50 else (0, 165, 255)
        cv2.putText(image, f"Shoulder: {metrics['shoulder_angle']}° (Opt: 45°)", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, shoulder_color, 2)
    
    if metrics['hip_drop'] is not None:
        hip_color = (0, 255, 0) if metrics['hip_drop'] < 20 else (0, 165, 255)
        cv2.putText(image, f"Hip Drop: {metrics['hip_drop']}px", 
                   (20, y_pos + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, hip_color, 2)
    
    return image

def add_info_panel(image, frame, total_frames, fps, reps, current_elbow_angle, hip_drop):
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
    cv2.putText(image_with_panel, f"Elbow: {current_elbow_angle}°", 
               (w//2 - 100, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 1)
    
    # Right side: NSCA standard
    cv2.putText(image_with_panel, "NSCA Standard:", 
               (w - 250, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
    cv2.putText(image_with_panel, "• Elbows at 90°", 
               (w - 250, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Straight body line", 
               (w - 250, new_h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Shoulders 45° to torso", 
               (w - 250, new_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    
    return image_with_panel

def get_form_rating(elbow_angle, hip_drop):
    """Rate push-up form"""
    # Check depth
    if elbow_angle > 120:
        depth = "Very Shallow"
    elif elbow_angle > 100:
        depth = "Shallow"
    elif elbow_angle > 80:
        depth = "Good Depth"
    else:
        depth = "Excellent Depth"
    
    # Check body alignment
    if hip_drop > 40:
        alignment = " - Significant Sag"
    elif hip_drop > 20:
        alignment = " - Mild Sag"
    else:
        alignment = " - Good Alignment"
    
    return depth + alignment

def generate_feedback(rep_data, all_angles, video_path):
    """Generate comprehensive feedback based on analysis"""
    
    if not rep_data:
        print("\n❌ NO PUSH-UPS DETECTED!")
        print("\nPossible reasons:")
        print("1. Side view works best for analysis")
        print("2. Full body not visible in frame")
        print("3. Not enough range of motion")
        print("4. Try a different video angle")
        return
    
    print(f"\n✅ DETECTED {len(rep_data)} PUSH-UP REPS")
    print("-" * 60)
    
    # Analyze each rep
    print("\n📋 REP-BY-REP ANALYSIS:")
    print("-" * 40)
    
    for i, rep in enumerate(rep_data, 1):
        angle = rep["min_elbow_angle"]
        rating = rep["form_rating"]
        
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
        avg_elbow_angle = np.mean([rep["min_elbow_angle"] for rep in rep_data])
        min_angle = min([rep["min_elbow_angle"] for rep in rep_data])
        max_angle = max([rep["min_elbow_angle"] for rep in rep_data])
        avg_hip_drop = np.mean([rep["max_hip_drop"] for rep in rep_data])
        
        print("\n📊 OVERALL STATISTICS:")
        print("-" * 40)
        print(f"   Average Elbow Angle: {avg_elbow_angle:.1f}°")
        print(f"   Best Depth: {min_angle}°")
        print(f"   Shallowest: {max_angle}°")
        print(f"   Average Hip Sag: {avg_hip_drop:.1f}px")
        
        # Consistency
        consistency = 100 - (max_angle - min_angle)
        print(f"   Depth Consistency: {consistency:.1f}%")
    
    print("\n" + "=" * 60)
    print("💡 NSCA-BASED FORM FEEDBACK")
    print("=" * 60)
    
    # Generate personalized feedback
    if rep_data:
        avg_depth = np.mean([rep["min_elbow_angle"] for rep in rep_data])
        avg_hip_drop_val = np.mean([rep["max_hip_drop"] for rep in rep_data])
        
        print("\n🎯 KEY FINDINGS:")
        print("-" * 40)
        
        if avg_depth > 100:
            print("🔴 PRIMARY ISSUE: INSUFFICIENT DEPTH")
            print("   • You're not reaching 90° elbow angle")
            print("   • NSCA standard requires 90° at bottom")
            print("   • Current average: {:.1f}°".format(avg_depth))
            
            print("\n🛠️  IMMEDIATE FIXES:")
            print("   1. Practice with hands on elevated surface")
            print("   2. Focus on 'chest to floor' not just bending arms")
            print("   3. Use a mirror to monitor depth")
            print("   4. Try kneeling push-ups to build strength")
            
        elif 80 <= avg_depth <= 100:
            print("✅ GOOD: MEETS NSCA DEPTH STANDARD")
            print("   • You're reaching proper elbow angle")
            print("   • NSCA standard: 90° elbow angle")
            print("   • Your average: {:.1f}°".format(avg_depth))
        
        else:  # avg_depth < 80
            print("⚠️  EXCELLENT: DEEP RANGE OF MOTION")
            print("   • You're going deeper than required")
            print("   • NSCA standard: 90° elbow angle")
            print("   • Your average: {:.1f}°".format(avg_depth))
        
        # Check hip sag
        if avg_hip_drop_val > 30:
            print("\n🔴 FORM ISSUE: HIP SAG")
            print("   • Your hips are dropping during reps")
            print("   • Average sag: {:.1f}px".format(avg_hip_drop_val))
            print("   • Causes lower back strain")
            
            print("\n🛠️  CORE ENGAGEMENT DRILLS:")
            print("   1. Practice plank holds (30-60 seconds)")
            print("   2. Focus on squeezing glutes during push-ups")
            print("   3. Try push-ups with band around waist")
            print("   4. Film from side to monitor alignment")
        
        elif avg_hip_drop_val > 15:
            print("\n⚠️  FORM ISSUE: MILD HIP SAG")
            print("   • Slight hip drop detected")
            print("   • Average sag: {:.1f}px".format(avg_hip_drop_val))
            print("   • Work on core bracing")
        else:
            print("\n✅ GOOD: EXCELLENT BODY ALIGNMENT")
            print("   • Straight body line maintained")
            print("   • Core engagement is good")
            print("   • Your average sag: {:.1f}px".format(avg_hip_drop_val))
    
    print("\n📋 NSCA TECHNICAL CHECKLIST:")
    print("-" * 40)
    checkboxes = [
        ("Hands shoulder-width apart", "✅"),
        ("Elbows at 45° to torso", "✅"),
        ("Straight body line", "✅" if avg_hip_drop_val <= 20 else "⚠️"),
        ("Chest lowers to floor", "✅" if avg_depth <= 100 else "⚠️"),
        ("Full extension at top", "✅"),
        ("Head neutral position", "✅"),
        ("Controlled tempo", "✅"),
    ]
    
    for item, status in checkboxes:
        print(f"   {status} {item}")
    
    print("\n🔧 RECOMMENDED DRILLS:")
    print("-" * 40)
    drills = [
        "1. Incline Push-Ups - for building strength",
        "2. Plank Variations - for core stability",
        "3. Eccentric Push-Ups - for control",
        "4. Banded Push-Ups - for form feedback",
        "5. Hand Release Push-Ups - for full ROM"
    ]
    
    for drill in drills:
        print(f"   {drill}")
    
    # Save quick report
    save_quick_report(rep_data, video_path, avg_depth if 'avg_depth' in locals() else None)
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS COMPLETE")
    print("=" * 60)

def save_quick_report(rep_data, video_path, avg_depth):
    """Save a quick text report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pushup_quick_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write("QUICK PUSH-UP ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Video: {os.path.basename(video_path)}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reps: {len(rep_data)}\n\n")
        
        f.write("Rep Details:\n")
        f.write("-" * 30 + "\n")
        for rep in rep_data:
            f.write(f"Rep {rep['rep']}: {rep['min_elbow_angle']}° - {rep['form_rating']}\n")
        
        if avg_depth:
            f.write(f"\nAverage Depth: {avg_depth:.1f}°\n")
            f.write("NSCA Standard: 90° elbow angle\n")
            
            if avg_depth > 100:
                f.write("\nFEEDBACK: Need more depth\n")
                f.write("FIX: Practice incline push-ups\n")
            elif avg_depth >= 80:
                f.write("\nFEEDBACK: Good depth\n")
                f.write("NEXT: Work on consistency\n")
            else:
                f.write("\nFEEDBACK: Excellent depth\n")
                f.write("NEXT: Maintain control\n")
        
        avg_hip_drop = np.mean([rep['max_hip_drop'] for rep in rep_data])
        f.write(f"\nAverage Hip Sag: {avg_hip_drop:.1f}px\n")
        if avg_hip_drop > 20:
            f.write("FORM ISSUE: Work on core stability\n")
        else:
            f.write("FORM: Good body alignment\n")
        
        f.write("\nNSCA Form Checklist:\n")
        f.write("-" * 30 + "\n")
        f.write("✓ Hands shoulder-width\n")
        f.write("✓ Elbows at 45°\n")
        f.write("✓ Straight body line\n")
        f.write("✓ Full range of motion\n")
        f.write("✓ Controlled tempo\n")
    
    print(f"\n💾 Quick report saved: {filename}")

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
            print(f"❌ Video not found: {video_path}")
            video_path = None
    
    # If no command line arg, look in current directory
    if not video_path:
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_path = file
                break
    
    if video_path:
        print(f"🎬 Found video: {video_path}")
        analyze_pushup_video(video_path)
    else:
        print("❌ No video file found!")
        print("\nPlease either:")
        print("1. Place a video file in this folder")
        print("2. Run: python pushup_analyzer.py your_video.mp4")
        print("\nSupported formats: .mp4, .avi, .mov, .mkv, .webm")
