
import cv2
import mediapipe as mp
import numpy as np
import os
from .biomechanics import get_exercise_angles, get_exercise_errors

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

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

def get_depth_rating(knee_angle):
    """Rate squat depth"""
    # Fetch standards
    angles = get_exercise_angles("squat")
    ideal_knee = angles.get("knee", {}).get("ideal", 85)
    range_knee = angles.get("knee", {}).get("range", (70, 100))
    
    if knee_angle > range_knee[1] + 20:
        return "Very Shallow"
    elif knee_angle > range_knee[1]:
        return "Shallow"
    elif knee_angle > range_knee[0] + 15: # 85+
        return "Good (Parallel)"
    elif knee_angle > range_knee[0]:
        return "Excellent"
    else:
        return "Very Deep"

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
        
    except:
        angles = {k: None for k in ['left_knee', 'right_knee', 'torso']}
    
    return angles

def add_angle_overlays(image, angles):
    """Add angle displays to frame"""
    y_pos = 40
    
    # Fetch ideal
    standards = get_exercise_angles("squat")
    knee_range = standards.get("knee", {}).get("range", (70, 100))
    
    if angles['left_knee'] is not None:
        if knee_range[0] <= angles['left_knee'] <= knee_range[1]:
            color = (0, 255, 0)  # Green - good
        elif angles['left_knee'] <= knee_range[1] + 20:
            color = (0, 165, 255)  # Orange - shallow
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Knee: {angles['left_knee']} (Goal: {standards.get('knee', {}).get('ideal', 85)})", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return image

def add_info_panel(image, frame, total_frames, fps, reps, current_knee_angle):
    """Add information panel to frame"""
    h, w = image.shape[:2]
    panel_height = 80
    panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
    panel[:, :] = (40, 40, 40)
    
    image_with_panel = np.vstack([image, panel])
    new_h = h + panel_height
    
    time_sec = frame / fps if fps > 0 else 0
    
    cv2.putText(image_with_panel, f"Reps: {reps}", 
               (30, new_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    cv2.putText(image_with_panel, f"Knee Angle: {current_knee_angle}", 
               (200, new_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return image_with_panel

def analyze_squat_video(video_path, output_path=None):
    """
    Main analysis function
    Returns: Dictionary with analysis results
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
    
    # Setup Output Writer
    out = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height + 80)) # +80 for panel

    rep_data = []
    in_squat = False
    rep_count = 0
    min_knee_angle = 180
    
    current_feedback = []
    all_knee_angles = []

    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            current_angle_val = 0
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                angles = get_key_angles(results.pose_landmarks.landmark, width, height)
                
                if angles['left_knee'] is not None:
                    current_angle_val = angles['left_knee']
                    all_knee_angles.append(current_angle_val)
                    
                    # Squat logic (Start counting when knee < 150)
                    if not in_squat and angles['left_knee'] < 150:
                        in_squat = True
                        min_knee_angle = 180
                    
                    if in_squat:
                        if angles['left_knee'] < min_knee_angle:
                            min_knee_angle = angles['left_knee']
                    
                    if in_squat and angles['left_knee'] > 165:
                        in_squat = False
                        rep_count += 1
                        rep_data.append({
                            "rep": rep_count,
                            "min_angle": min_knee_angle,
                            "rating": get_depth_rating(min_knee_angle)
                        })
                
                image = add_angle_overlays(image, angles)
            
            # Add Panel
            final_image = add_info_panel(image, frame_count, total_frames, fps, rep_count, current_angle_val if 'current_angle_val' in locals() else 0)
            
            if out:
                out.write(final_image)

    cap.release()
    if out:
        out.release()
    
    # Generate Final Feedback
    avg_depth = 0
    feedback_summary = []
    corrections = []
    
    # Get Biomechanics Data
    standards = get_exercise_angles("squat")
    errors = get_exercise_errors("squat")
    ideal_depth = standards.get("knee", {}).get("ideal", 85)
    
    if rep_data:
        avg_depth = np.mean([r["min_angle"] for r in rep_data])
        
        if avg_depth > 100:
            feedback_summary.append("Insufficient Depth")
            corrections.append(f"You are not reaching proper depth ({ideal_depth}°). Sit back deeper.")
            if "forward_lean" in errors:
                corrections.append(errors["forward_lean"]["message"])
        elif 80 <= avg_depth <= 100:
            feedback_summary.append("Good Depth")
            corrections.append("Great work hitting parallel. Work on consistency.")
        else:
            feedback_summary.append("Excellent Depth")
            corrections.append("You have great mobility. Keep controlling the descent.")
            
        # Check for potential issues using "butt_wink" or other error keys if we had logic for them
        # Currently we only track knee angle here.
        
    else:
        feedback_summary.append("No Reps Detected")
        corrections.append("Could not detect full squats. Ensure your whole body is in frame.")
        corrections.append("Try filming from a side profile for best results.")

    return {
        "reps_count": rep_count,
        "avg_depth": int(avg_depth),
        "feedback": feedback_summary,
        "corrections": corrections,
        "rep_details": rep_data
    }
