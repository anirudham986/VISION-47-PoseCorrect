
import cv2
import mediapipe as mp
import numpy as np
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
        
        cv2.putText(image, f"Back: {back_angle} (NSCA: 40-50)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    else:
        cv2.putText(image, "Back: --", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
    
    # Knee angle
    knee_angle = angles.get('left_knee') or angles.get('right_knee')
    if knee_angle is not None:
        knee_color = (0, 255, 0) if knee_angle > 170 else (0, 165, 255)
        cv2.putText(image, f"Knee: {knee_angle}", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, knee_color, 2)
    else:
        cv2.putText(image, "Knee: --", 
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

def analyze_deadlift_video(video_path, output_path=None):
    """
    Main deadlift analysis function adapted for web backend
    """
    if not os.path.exists(video_path):
        return {"error": "Video not found"}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_frames = []
    
    rep_data = []
    current_rep = {
        "frames": [],
        "back_angles": [],
        "hip_angles": [],
        "knee_angles": [],
        "shoulder_positions": [],
        "start_frame": 0
    }
    
    lift_phase = "setup"
    in_lift = False
    rep_count = 0
    warning_flags = []
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            if results.pose_landmarks:
                # Draw skeleton
                mp_drawing.draw_landmarks(
                    image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                # Highlight spine (simplified drawing)
                try:
                    left_shoulder = results.pose_landmarks.landmark[11]
                    right_shoulder = results.pose_landmarks.landmark[12]
                    left_hip = results.pose_landmarks.landmark[23]
                    right_hip = results.pose_landmarks.landmark[24]
                    
                    shoulder_mid_x = int((left_shoulder.x + right_shoulder.x) * width / 2)
                    shoulder_mid_y = int((left_shoulder.y + right_shoulder.y) * height / 2)
                    hip_mid_x = int((left_hip.x + right_hip.x) * width / 2)
                    hip_mid_y = int((left_hip.y + right_hip.y) * height / 2)
                    
                    cv2.line(image_rgb, (shoulder_mid_x, shoulder_mid_y), 
                            (hip_mid_x, hip_mid_y), (0, 0, 255), 3)
                except:
                    pass
                
                # Get landmarks and calculate angles
                landmarks = results.pose_landmarks.landmark
                angles = get_deadlift_angles(landmarks, width, height)
                
                current_knee_angle = angles.get('left_knee') or angles.get('right_knee')
                
                if current_knee_angle is not None:
                    # Detect lift phases
                    lift_phase = detect_lift_phase_simple(current_knee_angle, lift_phase)
                
                    # 1. Detect start of lift
                    if not in_lift and current_knee_angle < 140 and frame_count > 10: 
                        in_lift = True
                        current_rep = {
                            "frames": [],
                            "back_angles": [],
                            "hip_angles": [],
                            "knee_angles": [],
                            "shoulder_positions": [],
                            "start_frame": frame_count
                        }

                    # 2. Track rep data while in lift
                    if in_lift:
                        current_rep["frames"].append(frame_count)
                        if angles.get('back_angle'):
                            current_rep["back_angles"].append(angles['back_angle'])
                        current_rep["knee_angles"].append(current_knee_angle)

                    # 3. Detect completion (Lockout)
                    if (in_lift and current_knee_angle > 170 and 
                        frame_count - current_rep["start_frame"] > 10):
                        
                        in_lift = False
                        rep_count += 1
                        
                        # Analyze the completed rep
                        if current_rep["knee_angles"]:
                            rep_analysis = analyze_single_deadlift_rep_safe(current_rep, rep_count)
                            rep_data.append(rep_analysis)
                            
                            if rep_analysis["warnings"]:
                                warning_flags.extend(rep_analysis["warnings"])
                    
                # Add overlays
                image_rgb = add_deadlift_overlays_safe(image_rgb, angles, lift_phase, rep_count, width, height)
            
            # Add info panel
            final_image = add_deadlift_info_panel_safe(image_rgb, frame_count, total_frames, fps, 
                                                     rep_count, lift_phase, warning_flags, width, height)
            output_frames.append(final_image)

    cap.release()

    # Write using MoviePy
    if output_path and output_frames:
        try:
            # Fix for Real Time Coach video speed
            if "recorded_video" in os.path.basename(video_path) and len(output_frames) > 0:
                fps = len(output_frames) / 10.0
                print(f"DEBUG: Detected Real Time Coach video. Corrected FPS: {fps}")

            from moviepy.editor import ImageSequenceClip
            clip = ImageSequenceClip(output_frames, fps=fps)
            clip.write_videofile(output_path, codec='libx264', audio=False, logger=None, preset='ultrafast', threads=4)
        except Exception as e:
            return {"error": str(e)}

    # Generate Output Data
    feedback = []
    corrections = []
    
    # Collect warnings into feedback/corrections
    all_warnings = []
    for rep in rep_data:
        all_warnings.extend(rep.get("warnings", []))
    
    unique_warnings = sorted(list(set(all_warnings)))
    
    if unique_warnings:
        feedback.append("Form Issues Detected")
        for warning in unique_warnings:
            corrections.append(warning)
            
        # Add general deadlift advice based on specific warnings
        if any("Back" in w for w in unique_warnings):
            corrections.append("Keep your spine neutral to avoid injury. Engage your core.")
        if any("lockout" in w.lower() for w in unique_warnings):
            corrections.append("Squeeze glutes at the top to fully extend hips.")
    else:
        if rep_count > 0:
            feedback.append("Excellent Deadlift Form")
            corrections.append("Great neutral spine and full lockout.")
        else:
            feedback.append("No Reps Detected")
            corrections.append("Ensure you perform the full movement from floor to standing.")

    return {
        "reps_count": rep_count,
        "avg_depth": 0, # Not applicable for deadlift in the same way
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": rep_data
    }
