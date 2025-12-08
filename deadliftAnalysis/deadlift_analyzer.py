"""
Deadlift Analyzer - Fixed Version with Proper Rep Counter Logic
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os
from datetime import datetime

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Deadlift Standards
NSCA_STANDARDS = {
    "back_angle_start": {"optimal": 45, "range": (40, 50)},
    "hip_height_start": {"optimal": "above_knees"},
}

def calculate_angle(a, b, c):
    """Calculate angle at point b formed by a-b-c with error handling"""
    try:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        
        return int(np.degrees(np.arccos(cosine_angle)))
    except:
        return None

def safe_min(values):
    """Safely find minimum, ignoring None values"""
    valid_values = [v for v in values if v is not None]
    return min(valid_values) if valid_values else 180

def safe_max(values):
    """Safely find maximum, ignoring None values"""
    valid_values = [v for v in values if v is not None]
    return max(valid_values) if valid_values else 0

def safe_mean(values):
    """Safely calculate mean, ignoring None values"""
    valid_values = [v for v in values if v is not None]
    return np.mean(valid_values) if valid_values else 0

def analyze_deadlift_video(video_path):
    """
    Main deadlift analysis function - shows live preview and gives feedback
    """
    print("=" * 60)
    print("DEADLIFT ANALYZER - LIVE PREVIEW + FEEDBACK")
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
    rep_data = []
    # Initialize current_rep with default values
    current_rep = {
        "frames": [],
        "back_angles": [],
        "hip_angles": [],
        "knee_angles": [],
        "shoulder_positions": [],
        "start_frame": 0
    }
    
    lift_phase = "setup"
    in_lift = False  # Flag indicating the lifter is actively performing the lift part of a rep
    rep_count = 0
    warning_flags = []
    
    # Setup MediaPipe
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    ) as pose:
        
        frame_count = 0
        paused = False
        last_valid_knee_angle = 180
        
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
                    
                    # Highlight spine
                    try:
                        # Shoulder points
                        left_shoulder = results.pose_landmarks.landmark[11]
                        right_shoulder = results.pose_landmarks.landmark[12]
                        left_hip = results.pose_landmarks.landmark[23]
                        right_hip = results.pose_landmarks.landmark[24]
                        
                        h, w = image.shape[:2]
                        
                        # Draw spine line
                        shoulder_mid_x = int((left_shoulder.x + right_shoulder.x) * w / 2)
                        shoulder_mid_y = int((left_shoulder.y + right_shoulder.y) * h / 2)
                        hip_mid_x = int((left_hip.x + right_hip.x) * w / 2)
                        hip_mid_y = int((left_hip.y + right_hip.y) * h / 2)
                        
                        cv2.line(image, (shoulder_mid_x, shoulder_mid_y), 
                                (hip_mid_x, hip_mid_y), (0, 0, 255), 3)
                    except:
                        pass
                    
                    # Get landmarks
                    landmarks = results.pose_landmarks.landmark
                    
                    # Calculate key angles
                    angles = get_deadlift_angles(landmarks, width, height)
                    
                    # Use current knee angle for phase detection
                    current_knee_angle = angles.get('left_knee') or angles.get('right_knee')
                    
                    if current_knee_angle is not None:
                        last_valid_knee_angle = current_knee_angle
                        
                        # Detect lift phases
                        lift_phase = detect_lift_phase_simple(current_knee_angle, lift_phase)
                    
                        # --- START OF THE CORRECTED REP LOGIC ---
                        
                        # 1. Detect start of lift (Deep bend/Setup phase)
                        # Starts when the knee angle drops significantly (i.e., lifter is pulling)
                        if not in_lift and current_knee_angle < 140 and frame_count > fps / 2: # Ensure setup phase isn't too short
                            in_lift = True
                            current_rep = {
                                "frames": [],
                                "back_angles": [],
                                "hip_angles": [],
                                "knee_angles": [],
                                "shoulder_positions": [],
                                "start_frame": frame_count
                            }
                            print(f"Rep {rep_count + 1} started (Knee: {current_knee_angle}°)")

                        # 2. Track rep data while in lift
                        if in_lift:
                            current_rep["frames"].append(frame_count)
                            
                            if angles.get('back_angle'):
                                current_rep["back_angles"].append(angles['back_angle'])
                            current_rep["knee_angles"].append(current_knee_angle)

                        # 3. Detect completion of a cycle (Lockout achieved)
                        # Rep is complete when the knee angle reaches near full extension (>170)
                        if (in_lift and current_knee_angle > 170 and 
                            frame_count - current_rep["start_frame"] > fps / 2): # At least half a second duration
                            
                            in_lift = False
                            rep_count += 1
                            
                            # Analyze the completed rep
                            if current_rep["knee_angles"]:
                                rep_analysis = analyze_single_deadlift_rep_safe(current_rep, rep_count)
                                rep_data.append(rep_analysis)
                                
                                if rep_analysis["warnings"]:
                                    warning_flags.extend(rep_analysis["warnings"])
                                    print(f"Rep {rep_count} complete with warnings (Knee: {current_knee_angle}°)")
                                else:
                                    print(f"Rep {rep_count} complete (Knee: {current_knee_angle}°)")
                        
                        # --- END OF THE CORRECTED REP LOGIC ---
                        
                    # Add angle displays
                    image = add_deadlift_overlays_safe(image, angles, lift_phase, rep_count, width, height)
                
                # Add info panel
                image = add_deadlift_info_panel_safe(image, frame_count, total_frames, fps, 
                                                   rep_count, lift_phase, warning_flags, width, height)
                
                # Show live preview
                cv2.imshow('LIVE DEADLIFT ANALYSIS - Press Q to quit', image)
            
            # Handle keys
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            
            if key == ord('q') or key == 27:
                print("\nStopping analysis...")
                break
            elif key == ord('p'):
                paused = not paused
                print(f"   {'Paused' if paused else 'Resumed'}")
            elif key == ord('s'):
                screenshot = f"deadlift_frame_{frame_count}.jpg"
                cv2.imwrite(screenshot, image)
                print(f"Saved: {screenshot}")
            elif key == ord(' '):  # Space to manually mark rep
                if in_lift:
                    in_lift = False
                    rep_count += 1
                    print(f"Manually marked rep {rep_count}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Generate feedback
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE - GENERATING FEEDBACK")
    print("=" * 60)
    
    generate_deadlift_feedback_safe(rep_data, video_path, warning_flags)

def get_deadlift_angles(landmarks, width, height):
    """Extract key angles for deadlift analysis with error handling"""
    angles = {}
    
    try:
        def pixel_coord(idx):
            lm = landmarks[idx]
            return (int(lm.x * width), int(lm.y * height))
        
        # Get key points
        l_shoulder = pixel_coord(11)
        r_shoulder = pixel_coord(12)
        l_hip = pixel_coord(23)
        r_hip = pixel_coord(24)
        l_knee = pixel_coord(25)
        r_knee = pixel_coord(26)
        l_ankle = pixel_coord(27)
        r_ankle = pixel_coord(28)
        
        # Mid points
        shoulder_mid = (
            (l_shoulder[0] + r_shoulder[0]) // 2,
            (l_shoulder[1] + r_shoulder[1]) // 2
        )
        hip_mid = (
            (l_hip[0] + r_hip[0]) // 2,
            (l_hip[1] + r_hip[1]) // 2
        )
        
        # Back angle (vertical line through hips vs shoulder-hip line)
        vertical_point = (hip_mid[0], hip_mid[1] - 100)
        back_angle = calculate_angle(vertical_point, hip_mid, shoulder_mid)
        angles['back_angle'] = back_angle if back_angle else None
        
        # Knee angles
        angles['left_knee'] = calculate_angle(l_hip, l_knee, l_ankle)
        angles['right_knee'] = calculate_angle(r_hip, r_knee, r_ankle)
        
        # Hip angle
        # Note: Using left knee for hip angle calculation, assuming side view
        angles['hip_angle'] = calculate_angle(shoulder_mid, hip_mid, l_knee)
        
    except Exception as e:
        # Set all to None if any calculation fails
        angles = {
            'back_angle': None,
            'left_knee': None,
            'right_knee': None,
            'hip_angle': None
        }
    
    return angles

def detect_lift_phase_simple(knee_angle, current_phase):
    """Simple phase detection based on knee angle"""
    if knee_angle is None:
        return current_phase
    
    if knee_angle > 170: # Lockout threshold increased for more stability
        return "lockout"
    elif knee_angle < 100:
        return "setup"
    elif 100 <= knee_angle <= 140:
        return "pull"
    else:
        return "lower"

def analyze_single_deadlift_rep_safe(rep_data, rep_number):
    """Safe analysis of a single deadlift rep"""
    warnings = []
    
    # Get valid angles only
    valid_back_angles = [a for a in rep_data["back_angles"] if a is not None]
    valid_knee_angles = [a for a in rep_data["knee_angles"] if a is not None]
    
    if not valid_back_angles or not valid_knee_angles:
        warnings.append(f"Rep {rep_number}: Insufficient data for analysis")
        return {
            "rep": rep_number,
            "start_back_angle": None,
            "min_knee_angle": None,
            "max_back_angle": None,
            "avg_back_angle": None,
            "warnings": warnings,
            "frames": len(rep_data["frames"])
        }
    
    # Calculate metrics
    start_back_angle = valid_back_angles[0] if valid_back_angles else None
    min_knee_angle = safe_min(valid_knee_angles)
    max_back_angle = safe_max(valid_back_angles)
    avg_back_angle = safe_mean(valid_back_angles)
    
    # Check for form issues
    if start_back_angle:
        if start_back_angle > 55:
            warnings.append(f"Back too horizontal at start ({start_back_angle}°)")
        elif start_back_angle < 35:
            warnings.append(f"Back too vertical at start ({start_back_angle}°)")
    
    # Check lockout
    if valid_knee_angles:
        final_knee_angle = valid_knee_angles[-1]
        if final_knee_angle < 170:
            warnings.append(f"Incomplete lockout ({final_knee_angle}°)")
    
    return {
        "rep": rep_number,
        "start_back_angle": start_back_angle,
        "min_knee_angle": min_knee_angle,
        "max_back_angle": max_back_angle,
        "avg_back_angle": avg_back_angle,
        "warnings": warnings,
        "frames": len(rep_data["frames"])
    }

def add_deadlift_overlays_safe(image, angles, phase, rep_count, width, height):
    """Safe version of overlays"""
    h, w = image.shape[:2]
    
    # Display at top
    y_pos = 40
    
    # Back angle
    back_angle = angles.get('back_angle')
    if back_angle is not None:
        # Color coding
        if 40 <= back_angle <= 50:
            color = (0, 255, 0)  # Green
        elif 35 <= back_angle < 40 or 50 < back_angle <= 55:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 0, 255)  # Red
        
        cv2.putText(image, f"Back: {back_angle}°", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    else:
        cv2.putText(image, "Back: --°", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
    
    # Knee angle
    knee_angle = angles.get('left_knee') or angles.get('right_knee')
    if knee_angle is not None:
        knee_color = (0, 255, 0) if knee_angle > 170 else (0, 165, 255)
        cv2.putText(image, f"Knee: {knee_angle}°", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, knee_color, 2)
    else:
        cv2.putText(image, "Knee: --°", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
    
    # Phase and reps
    phase_color = {
        "setup": (255, 255, 0),
        "pull": (0, 255, 255),
        "lockout": (0, 255, 0),
        "lower": (255, 165, 0)
    }.get(phase, (255, 255, 255))
    
    cv2.putText(image, f"Phase: {phase.upper()}", 
               (w - 150, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, phase_color, 2)
    cv2.putText(image, f"Reps: {rep_count}", 
               (w - 150, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    return image

def add_deadlift_info_panel_safe(image, frame, total_frames, fps, reps, phase, warnings, width, height):
    """Safe info panel"""
    h, w = image.shape[:2]
    
    # Create bottom panel
    panel_height = 100
    panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
    panel[:, :] = (40, 40, 40)
    
    # Add panel
    image_with_panel = np.vstack([image, panel])
    new_h = h + panel_height
    
    # Basic info
    time_sec = frame / fps if fps > 0 else 0
    cv2.putText(image_with_panel, f"Frame: {frame}/{total_frames}", 
               (20, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(image_with_panel, f"Time: {time_sec:.1f}s", 
               (20, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Phase and reps
    phase_color = {
        "setup": (255, 255, 0),
        "pull": (0, 255, 255),
        "lockout": (0, 255, 0),
        "lower": (255, 165, 0)
    }.get(phase, (255, 255, 255))
    
    cv2.putText(image_with_panel, f"Phase: {phase.upper()}", 
               (w//2 - 100, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, phase_color, 2)
    cv2.putText(image_with_panel, f"Reps: {reps}", 
               (w//2 - 100, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Last warning
    if warnings:
        last_warning = warnings[-1] if isinstance(warnings[-1], str) else str(warnings[-1])
        if len(last_warning) > 40:
            last_warning = last_warning[:37] + "..."
        cv2.putText(image_with_panel, f"Last: {last_warning}", 
                   (20, new_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    return image_with_panel

def generate_deadlift_feedback_safe(rep_data, video_path, warnings):
    """Safe feedback generation"""
    
    if not rep_data:
        print("\nNO DEADLIFTS DETECTED!")
        print("\nTips:")
        print("1. Use SIDE VIEW for best results")
        print("2. Make sure entire body is visible")
        print("3. Perform complete reps with clear lockout")
        print("4. Good lighting helps detection")
        return
    
    print(f"\nDETECTED {len(rep_data)} DEADLIFT REPS")
    print("-" * 60)
    
    # Collect valid angles
    valid_start_angles = [rep.get("start_back_angle") for rep in rep_data 
                         if rep.get("start_back_angle") is not None]
    
    if valid_start_angles:
        avg_start_angle = safe_mean(valid_start_angles)
        min_start_angle = safe_min(valid_start_angles)
        max_start_angle = safe_max(valid_start_angles)
        
        print("\n📊 BACK ANGLE ANALYSIS:")
        print(f"   Average: {avg_start_angle:.1f}° (NSCA Optimal: 45°)")
        print(f"   Best: {min_start_angle}°")
        print(f"   Worst: {max_start_angle}°")
        
        # Consistency
        if max_start_angle != min_start_angle:
            consistency = 100 - (max_start_angle - min_start_angle)
            print(f"   Consistency: {consistency:.1f}%")
    
    # Warning summary
    all_warnings = []
    for rep in rep_data:
        all_warnings.extend(rep.get("warnings", []))
    
    if all_warnings:
        print("\nFORM ISSUES DETECTED:")
        print("-" * 40)
        for warning in set(all_warnings):  # Remove duplicates
            count = all_warnings.count(warning)
            print(f"   • {warning} ({count} reps)")
    else:
        print("\nNO MAJOR FORM ISSUES DETECTED")
    
    print("\n" + "=" * 60)
    print("NSCA DEADLIFT GUIDELINES")
    print("=" * 60)
    
    print("\nPROPER SETUP:")
    print("-" * 40)
    setup_points = [
        "1. Feet hip-width apart",
        "2. Bar over mid-foot",
        "3. Shoulders slightly ahead of bar",
        "4. Back angle: 40-50°",
        "5. Chest up, lats tight",
        "6. Hips above knees",
        "7. Neutral spine (NO rounding!)",
        "8. Arms straight, grip the bar"
    ]
    
    for point in setup_points:
        print(f"   {point}")
    
    print("\nEXECUTION:")
    print("-" * 40)
    execution_points = [
        "1. Push through heels (leg drive)",
        "2. Keep bar close to body",
        "3. Back angle should remain constant initially",
        "4. Hips and shoulders rise together",
        "5. Extend knees, then hips",
        "6. Lock out fully (stand tall)",
        "7. Squeeze glutes at top"
    ]
    
    for point in execution_points:
        print(f"   {point}")
    
    print("\nCOMMON FIXES:")
    print("-" * 40)
    fixes = [
        "Back rounds: Reduce weight, strengthen core",
        "Hips rise first: Focus on leg drive",
        "Incomplete lockout: Practice rack pulls",
        "Bar away from body: Drag bar up legs",
        "Slow off floor: Add deficit deadlifts"
    ]
    
    for fix in fixes:
        print(f"   • {fix}")
    
    # Save simple report
    save_simple_report(rep_data, video_path, warnings)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

def save_simple_report(rep_data, video_path, warnings):
    """Save a simple report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"deadlift_report_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write("DEADLIFT ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Video: {os.path.basename(video_path)}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reps: {len(rep_data)}\n\n")
        
        f.write("Rep Analysis:\n")
        f.write("-" * 30 + "\n")
        for rep in rep_data:
            angle = rep.get("start_back_angle", "N/A")
            if angle:
                rating = "Good" if 40 <= angle <= 50 else "Needs Work"
                f.write(f"Rep {rep['rep']}: {angle}° - {rating}\n")
            else:
                f.write(f"Rep {rep['rep']}: No angle data\n")
            
            if rep.get("warnings"):
                for warning in rep["warnings"]:
                    f.write(f"{warning}\n")
        
        f.write("\nRecommendations:\n")
        f.write("-" * 30 + "\n")
        f.write("1. Film from side view for better analysis\n")
        f.write("2. Ensure full body visibility\n")
        f.write("3. Maintain neutral spine\n")
        f.write("4. Focus on leg drive, not back pull\n")
        f.write("5. Keep bar close to body\n")
    
    print(f"\nReport saved: {filename}")

# Main function
if __name__ == "__main__":
    import sys
    
    # Check for video file
    video_path = None
    
    # Check command line
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    
    # Look for videos in current directory
    if not video_path:
        video_ext = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in video_ext):
                video_path = file
                break
    
    if video_path and os.path.exists(video_path):
        print(f"Analyzing: {video_path}")
        analyze_deadlift_video(video_path)
    else:
        print("No video file found!")
        print("\nUsage: python deadlift_analyzer.py <video_file>")
        print("   or place a video in the same folder")
        print("\nSupported: .mp4, .avi, .mov, .mkv, .webm")
