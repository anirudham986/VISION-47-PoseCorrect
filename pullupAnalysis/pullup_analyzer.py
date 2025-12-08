"""
Pull-Up Analyzer - NSCA Standards Based Analysis
Analyzes pull-up form using MediaPipe pose detection
"""

import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Pull-Up Standards
NSCA_STANDARDS = {
    "elbow_angle_start": {"optimal": 175, "range": (170, 180)},  # Full extension
    "elbow_angle_top": {"optimal": 50, "range": (40, 60)},  # Chin over bar
    "chin_height": "above_bar",  # Chin must clear bar
    "body_swing": {"max_acceptable": 30},  # pixels of horizontal movement
    "tempo": {"controlled": True}  # No kipping/swinging
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

def get_key_metrics(landmarks, width, height):
    """Extract key metrics for pull-up analysis"""
    def pixel_coord(idx):
        lm = landmarks[idx]
        return (int(lm.x * width), int(lm.y * height))
    
    metrics = {}
    
    try:
        # Elbow angles
        l_shoulder = pixel_coord(11)
        l_elbow = pixel_coord(13)
        l_wrist = pixel_coord(15)
        metrics['left_elbow'] = calculate_angle(l_shoulder, l_elbow, l_wrist)
        
        r_shoulder = pixel_coord(12)
        r_elbow = pixel_coord(14)
        r_wrist = pixel_coord(16)
        metrics['right_elbow'] = calculate_angle(r_shoulder, r_elbow, r_wrist)
        
        # Shoulder position (for scapular engagement)
        l_hip = pixel_coord(23)
        r_hip = pixel_coord(24)
        metrics['left_shoulder_angle'] = calculate_angle(l_elbow, l_shoulder, l_hip)
        metrics['right_shoulder_angle'] = calculate_angle(r_elbow, r_shoulder, r_hip)
        
        # Body position tracking (for swing detection)
        shoulder_mid = (
            (l_shoulder[0] + r_shoulder[0]) // 2,
            (l_shoulder[1] + r_shoulder[1]) // 2
        )
        hip_mid = (
            (l_hip[0] + r_hip[0]) // 2,
            (l_hip[1] + r_hip[1]) // 2
        )
        
        metrics['shoulder_x'] = shoulder_mid[0]
        metrics['hip_x'] = hip_mid[0]
        
        # Chin position (relative to wrists - approximation of bar height)
        nose = pixel_coord(0)
        wrist_mid_y = (l_wrist[1] + r_wrist[1]) // 2
        metrics['chin_height'] = wrist_mid_y - nose[1]  # Positive when chin is above bar
        
        # Hip angle (to detect kipping)
        l_knee = pixel_coord(25)
        r_knee = pixel_coord(26)
        metrics['left_hip_angle'] = calculate_angle(l_shoulder, l_hip, l_knee)
        metrics['right_hip_angle'] = calculate_angle(r_shoulder, r_hip, r_knee)
        
    except Exception as e:
        print(f"Error in metrics: {e}")
        metrics = {k: None for k in ['left_elbow', 'right_elbow', 'left_shoulder_angle', 
                                    'right_shoulder_angle', 'shoulder_x', 'hip_x', 
                                    'chin_height', 'left_hip_angle', 'right_hip_angle']}
    
    return metrics

def get_depth_rating(elbow_angle, chin_height):
    """Rate pull-up depth based on elbow angle and chin position"""
    if chin_height < 0:
        return "No Chin Over Bar"
    elif elbow_angle > 90:
        return "Partial ROM"
    elif 60 <= elbow_angle <= 90:
        return "Good Depth"
    elif 40 <= elbow_angle < 60:
        return "Excellent (Full ROM)"
    else:
        return "Very Deep"

def add_metric_overlays(image, metrics):
    """Add metric displays to frame"""
    y_pos = 40
    
    if metrics['left_elbow'] is not None:
        # Color code based on NSCA standard
        if 40 <= metrics['left_elbow'] <= 60:
            color = (0, 255, 0)  # Green - excellent
        elif 60 < metrics['left_elbow'] <= 90:
            color = (0, 200, 255)  # Yellow - good
        elif metrics['left_elbow'] > 160:
            color = (255, 255, 255)  # White - starting position
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Elbow: {metrics['left_elbow']} (NSCA: 40-60 at top)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if metrics['chin_height'] is not None:
        chin_color = (0, 255, 0) if metrics['chin_height'] > 0 else (0, 0, 255)
        chin_status = "Above Bar" if metrics['chin_height'] > 0 else "Below Bar"
        cv2.putText(image, f"Chin: {chin_status}", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, chin_color, 2)
    
    return image

def add_info_panel(image, frame, total_frames, fps, reps, current_elbow_angle, chin_over_bar):
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
               (w - 280, new_h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
    cv2.putText(image_with_panel, "• Chin over bar", 
               (w - 280, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Full arm extension", 
               (w - 280, new_h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Controlled movement", 
               (w - 280, new_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    
    return image_with_panel

def analyze_pullup_video(video_path, output_path=None):
    """
    Main analysis function for pull-ups
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
    in_pullup = False
    rep_count = 0
    min_elbow_angle = 180
    max_chin_height = -1000
    body_swing_positions = []
    
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
            chin_over_bar = False

            # Draw skeleton for output video
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                landmarks = results.pose_landmarks.landmark
                
                # Calculate key metrics
                metrics = get_key_metrics(landmarks, width, height)
                
                if metrics['left_elbow'] is not None:
                    current_angle_val = metrics['left_elbow']
                    
                    # Track body swing
                    if metrics['shoulder_x'] is not None:
                        body_swing_positions.append(metrics['shoulder_x'])
                    
                    # Detect pull-up reps
                    # Starting position: arms extended
                    if not in_pullup and metrics['left_elbow'] > 160:
                        in_pullup = True
                        min_elbow_angle = 180
                        max_chin_height = -1000
                        body_swing_start = metrics['shoulder_x'] if metrics['shoulder_x'] else 0
                    
                    if in_pullup:
                        # Track minimum elbow angle (top of pull-up)
                        if metrics['left_elbow'] < min_elbow_angle:
                            min_elbow_angle = metrics['left_elbow']
                        
                        # Track chin height
                        if metrics['chin_height'] is not None and metrics['chin_height'] > max_chin_height:
                            max_chin_height = metrics['chin_height']
                            chin_over_bar = max_chin_height > 0
                    
                    # Complete rep when returning to extended position
                    if in_pullup and metrics['left_elbow'] > 160 and min_elbow_angle < 150:
                        in_pullup = False
                        rep_count += 1
                        
                        # Calculate body swing
                        body_swing = 0
                        if len(body_swing_positions) > 1:
                            body_swing = max(body_swing_positions) - min(body_swing_positions)
                        body_swing_positions = []
                        
                        rep_data.append({
                            "rep": rep_count,
                            "min_elbow_angle": min_elbow_angle,
                            "chin_over_bar": chin_over_bar,
                            "max_chin_height": max_chin_height,
                            "body_swing": body_swing,
                            "depth_rating": get_depth_rating(min_elbow_angle, max_chin_height)
                        })
                
                # Add metric displays
                image_rgb = add_metric_overlays(image_rgb, metrics)
            
            # Add info panel
            final_image = add_info_panel(image_rgb, frame_count, total_frames, fps, rep_count, 
                                        min_elbow_angle, chin_over_bar)
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

    # Generate Feedback
    avg_elbow_angle = 0
    feedback_summary = []
    corrections = []
    
    if rep_data:
        avg_elbow_angle = np.mean([r["min_elbow_angle"] for r in rep_data])
        chin_success_rate = sum(1 for r in rep_data if r["chin_over_bar"]) / len(rep_data) * 100
        avg_body_swing = np.mean([r["body_swing"] for r in rep_data])
        
        # Depth feedback
        if avg_elbow_angle > 90:
            feedback_summary.append("Insufficient Depth")
            corrections.append("You're not achieving full range of motion.")
            corrections.append("Focus on pulling until chin clears the bar.")
            corrections.append("Practice negative pull-ups to build strength.")
        elif 60 <= avg_elbow_angle <= 90:
            feedback_summary.append("Good Depth (NSCA Standard)")
            corrections.append("Good depth achieved.")
            corrections.append("Work on consistency across all reps.")
        else:
            feedback_summary.append("Excellent Depth")
            corrections.append("Excellent range of motion.")
            corrections.append("Maintain this form as you increase volume.")
        
        # Chin over bar feedback
        if chin_success_rate < 80:
            feedback_summary.append(f"Chin Over Bar: {chin_success_rate:.0f}%")
            corrections.append(f"Only {chin_success_rate:.0f}% of reps had chin over bar.")
            corrections.append("Focus on pulling higher to clear the bar.")
        
        # Body swing feedback
        if avg_body_swing > 30:
            feedback_summary.append("Excessive Body Swing")
            corrections.append("Minimize kipping and swinging.")
            corrections.append("Engage core and keep body stable.")
            corrections.append("Use controlled tempo throughout the movement.")
        
    else:
        feedback_summary.append("No Reps Detected")
        corrections.append("Could not detect full pull-ups.")
        corrections.append("Ensure your full body is visible in the frame.")
        corrections.append("Film from the side for best results.")

    return {
        "reps_count": rep_count,
        "avg_elbow_angle": int(avg_elbow_angle) if avg_elbow_angle else 0,
        "chin_success_rate": int(chin_success_rate) if rep_data else 0,
        "feedback": feedback_summary,
        "corrections": corrections,
        "rep_details": rep_data
    }
