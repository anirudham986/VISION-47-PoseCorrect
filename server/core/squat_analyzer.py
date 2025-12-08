
import cv2
import mediapipe as mp
import numpy as np
import os
from .biomechanics import get_exercise_angles, get_exercise_errors

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Squat Standards (Embedded from user snippet)
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
    y_pos = 40
    if angles['left_knee'] is not None:
        # Color code based on NSCA standard
        if 80 <= angles['left_knee'] <= 100:
            color = (0, 255, 0)  # Green - good
        elif 100 < angles['left_knee'] <= 120:
            color = (0, 165, 255)  # Orange - shallow
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Knee: {angles['left_knee']} (NSCA: 90)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if angles['torso'] is not None:
        torso_color = (0, 255, 0) if 40 <= angles['torso'] <= 50 else (0, 165, 255)
        cv2.putText(image, f"Torso: {angles['torso']} (Opt: 45)", 
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
    
    # Middle: Rep info
    cv2.putText(image_with_panel, f"Reps: {reps}", 
               (w//2 - 100, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(image_with_panel, f"Current Knee: {current_knee_angle}", 
               (w//2 - 100, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 1)
    
    # Right side: NSCA standard (Simplified for video)
    cv2.putText(image_with_panel, "NSCA Standard:", 
               (w - 250, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
    cv2.putText(image_with_panel, " Parallel depth (90)", 
               (w - 250, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)

    return image_with_panel

def analyze_squat_video(video_path, output_path=None):
    """
    Main analysis function adapted for backend
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
    
    output_frames = []

    rep_data = []
    in_squat = False
    rep_count = 0
    min_knee_angle = 180
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
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
            
            current_angle_val = 0

            # Draw skeleton for output video
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                landmarks = results.pose_landmarks.landmark
                
                # Calculate key angles using new logic
                angles = get_key_angles(landmarks, width, height)
                
                if angles['left_knee'] is not None:
                    current_angle_val = angles['left_knee']
                    
                    # Detect squat reps (Logic from snippet)
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

                # Add angle displays
                image_rgb = add_angle_overlays(image_rgb, angles)
            
            # Add info panel
            final_image = add_info_panel(image_rgb, frame_count, total_frames, fps, rep_count, min_knee_angle)
            output_frames.append(final_image)

    cap.release()
    
    # Write using MoviePy
    if output_path and output_frames:
        try:
            from moviepy.editor import ImageSequenceClip
            clip = ImageSequenceClip(output_frames, fps=fps)
            clip.write_videofile(output_path, codec='libx264', audio=False, logger=None, preset='ultrafast', threads=4)
        except Exception as e:
            print(f"Error writing video: {e}")
            return {"error": str(e)}

    # Generate Feedback (Adapted from snippet's print statements)
    avg_depth = 0
    feedback_summary = []
    corrections = []
    
    if rep_data:
        avg_depth = np.mean([r["min_angle"] for r in rep_data])
        
        if avg_depth > 100:
            feedback_summary.append("Insufficient Depth")
            corrections.append("You are not reaching parallel (90° knee angle). Sit back deeper.")
            corrections.append("Practice with a box or bench.")
            corrections.append("Improve ankle mobility.")
        elif 85 <= avg_depth <= 100:
            feedback_summary.append("Good Depth (NSCA Standard)")
            corrections.append("Great work hitting parallel.")
            corrections.append("Work on depth consistency.")
            corrections.append("Increase weight gradually.")
        else:
            feedback_summary.append("Excellent Depth")
            corrections.append("You're going deeper than required.")
            corrections.append("Maintain control at the bottom.")
            
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
