
import cv2
import mediapipe as mp
import numpy as np
import os
from .biomechanics import get_exercise_angles, get_exercise_errors

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Push-Up Standards (Embedded from user snippet)
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
        metrics = {k: None for k in ['left_elbow', 'right_elbow', 'shoulder_angle', 
                                    'hip_drop', 'torso_angle']}
    
    return metrics

def add_metric_overlays(image, metrics):
    """Add metric displays to frame"""
    h, w = image.shape[:2]
    y_pos = 40
    
    if metrics['left_elbow'] is not None:
        if 80 <= metrics['left_elbow'] <= 100:
            color = (0, 255, 0)  # Green - good
        elif 100 < metrics['left_elbow'] <= 120:
            color = (0, 165, 255)  # Orange - shallow
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Elbow: {metrics['left_elbow']} (NSCA: 90)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if metrics['shoulder_angle'] is not None:
        shoulder_color = (0, 255, 0) if 40 <= metrics['shoulder_angle'] <= 50 else (0, 165, 255)
        cv2.putText(image, f"Shoulder: {metrics['shoulder_angle']} (Opt: 45)", 
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
    
    # Middle: Rep info
    cv2.putText(image_with_panel, f"Reps: {reps}", 
               (w//2 - 100, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(image_with_panel, f"Elbow: {current_elbow_angle}", 
               (w//2 - 100, new_h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 1)
    
    # Right side: NSCA standard
    cv2.putText(image_with_panel, "NSCA Standard:", 
               (w - 250, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
    cv2.putText(image_with_panel, " Elbows at 90", 
               (w - 250, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)

    return image_with_panel

def analyze_pushup_video(video_path, output_path=None):
    """
    Main pushup analysis function adapted for web backend
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
    in_pushup = False
    rep_count = 0
    min_elbow_angle = 180
    max_hip_drop = 0
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame_count += 1
            
            # Process frame
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                landmarks = results.pose_landmarks.landmark
                metrics = get_key_metrics(landmarks, width, height)
                
                if metrics['left_elbow'] is not None:
                    # Detect reps
                    if not in_pushup and metrics['left_elbow'] < 140:
                        in_pushup = True
                        min_elbow_angle = 180
                        max_hip_drop = 0
                    
                    if in_pushup:
                        if metrics['left_elbow'] < min_elbow_angle:
                            min_elbow_angle = metrics['left_elbow']
                        if metrics['hip_drop'] and metrics['hip_drop'] > max_hip_drop:
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
                
                image_rgb = add_metric_overlays(image_rgb, metrics)
            
            # Add info panel
            final_image = add_info_panel(image_rgb, frame_count, total_frames, fps, rep_count, min_elbow_angle, max_hip_drop)
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

    # Generate Feedback
    avg_depth = 0
    feedback_summary = []
    corrections = []
    
    if rep_data:
        avg_depth = np.mean([rep["min_elbow_angle"] for rep in rep_data])
        avg_hip_drop = np.mean([rep["max_hip_drop"] for rep in rep_data])
        
        if avg_depth > 100:
            feedback_summary.append("Insufficient Depth")
            corrections.append("Not reaching 90° elbow angle. Lower your chest further.")
            corrections.append("Practice hands-elevated pushups.")
        elif 80 <= avg_depth <= 100:
            feedback_summary.append("Good Depth (NSCA Standard)")
            corrections.append("Hitting proper elbow angle.")
        else:
            feedback_summary.append("Excellent Range of Motion")
            corrections.append("Going deeper than required.")
            
        if avg_hip_drop > 30:
            feedback_summary.append("Significant Hip Sag")
            corrections.append("Engage core to prevent hips from dropping.")
            corrections.append("Practice plank holds.")
        elif avg_hip_drop > 15:
             feedback_summary.append("Mild Hip Sag")
             corrections.append("Keep body in a straight line.")
            
    else:
        feedback_summary.append("No Reps Detected")
        corrections.append("Ensure full extension and side profile view.")

    return {
        "reps_count": rep_count,
        "avg_depth": int(avg_depth),
        "feedback": feedback_summary,
        "corrections": corrections,
        "rep_details": rep_data
    }
