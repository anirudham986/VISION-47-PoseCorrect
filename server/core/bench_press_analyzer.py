"""
Bench Press Analyzer - NSCA Standards Based Analysis
Analyzes bench press form using MediaPipe pose detection
"""

import cv2
import mediapipe as mp
import numpy as np
import os


# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# NSCA Bench Press Standards
NSCA_STANDARDS = {
    "elbow_angle_bottom": {"optimal": 90, "range": (80, 100)},  # At chest
    "elbow_angle_top": {"optimal": 180, "range": (170, 180)},  # Full extension
    "elbow_flare": {"optimal": 45, "range": (30, 75)},  # Angle from torso
    "bar_path": "inverted_j",  # Diagonal down, arc up
    "five_point_contact": True,  # Head, shoulders, glutes, both feet
    "wrist_alignment": "vertical_forearms"  # Forearms perpendicular to floor
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
    """Extract key metrics for bench press analysis"""
    def pixel_coord(idx):
        lm = landmarks[idx]
        return (int(lm.x * width), int(lm.y * height))
    
    metrics = {}
    
    try:
        # Elbow angles (shoulder-elbow-wrist)
        l_shoulder = pixel_coord(11)
        l_elbow = pixel_coord(13)
        l_wrist = pixel_coord(15)
        metrics['left_elbow'] = calculate_angle(l_shoulder, l_elbow, l_wrist)
        
        r_shoulder = pixel_coord(12)
        r_elbow = pixel_coord(14)
        r_wrist = pixel_coord(16)
        metrics['right_elbow'] = calculate_angle(r_shoulder, r_elbow, r_wrist)
        
        # Elbow flare (angle from torso)
        l_hip = pixel_coord(23)
        r_hip = pixel_coord(24)
        hip_mid = (
            (l_hip[0] + r_hip[0]) // 2,
            (l_hip[1] + r_hip[1]) // 2
        )
        
        # Calculate elbow flare angle
        metrics['left_elbow_flare'] = calculate_angle(hip_mid, l_shoulder, l_elbow)
        metrics['right_elbow_flare'] = calculate_angle(hip_mid, r_shoulder, r_elbow)
        
        # Wrist position (for bar path tracking)
        wrist_mid_y = (l_wrist[1] + r_wrist[1]) // 2
        shoulder_mid_y = (l_shoulder[1] + r_shoulder[1]) // 2
        
        metrics['bar_height'] = shoulder_mid_y - wrist_mid_y  # Negative when bar is above shoulders
        metrics['wrist_x'] = (l_wrist[0] + r_wrist[0]) // 2
        
        # Shoulder angle (for ROM)
        metrics['left_shoulder_angle'] = calculate_angle(l_elbow, l_shoulder, l_hip)
        metrics['right_shoulder_angle'] = calculate_angle(r_elbow, r_shoulder, r_hip)
        
    except Exception as e:
        print(f"Error in metrics: {e}")
        metrics = {k: None for k in ['left_elbow', 'right_elbow', 'left_elbow_flare', 
                                    'right_elbow_flare', 'bar_height', 'wrist_x',
                                    'left_shoulder_angle', 'right_shoulder_angle']}
    
    return metrics

def get_depth_rating(elbow_angle):
    """Rate bench press depth based on elbow angle"""
    if elbow_angle > 120:
        return "Partial ROM"
    elif 100 <= elbow_angle <= 120:
        return "Shallow"
    elif 80 <= elbow_angle < 100:
        return "Good Depth (NSCA Standard)"
    elif 60 <= elbow_angle < 80:
        return "Full ROM"
    else:
        return "Very Deep"

def add_metric_overlays(image, metrics):
    """Add metric displays to frame"""
    y_pos = 40
    
    if metrics['left_elbow'] is not None:
        # Color code based on NSCA standard
        if 80 <= metrics['left_elbow'] <= 100:
            color = (0, 255, 0)  # Green - good depth
        elif 100 < metrics['left_elbow'] <= 120:
            color = (0, 200, 255)  # Yellow - shallow
        elif 170 <= metrics['left_elbow'] <= 180:
            color = (255, 255, 255)  # White - lockout
        else:
            color = (0, 0, 255)  # Red - poor
        
        cv2.putText(image, f"Elbow: {metrics['left_elbow']} (NSCA: 80-100 at chest)", 
                   (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    if metrics['left_elbow_flare'] is not None:
        flare_color = (0, 255, 0) if 30 <= metrics['left_elbow_flare'] <= 75 else (0, 165, 255)
        cv2.putText(image, f"Elbow Flare: {metrics['left_elbow_flare']} (Opt: 30-75)", 
                   (20, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, flare_color, 2)
    
    return image

def add_info_panel(image, frame, total_frames, fps, reps, current_elbow_angle):
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
    cv2.putText(image_with_panel, "• Bar to chest", 
               (w - 280, new_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Full extension", 
               (w - 280, new_h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    cv2.putText(image_with_panel, "• Controlled tempo", 
               (w - 280, new_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
    
    return image_with_panel

def analyze_bench_press_video(video_path, output_path=None):
    """
    Main analysis function for bench press
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
    in_press = False
    rep_count = 0
    min_elbow_angle = 180
    max_elbow_flare = 0
    bar_path_positions = []
    
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
                
                # Calculate key metrics
                metrics = get_key_metrics(landmarks, width, height)
                
                # Determine which side to track based on visibility/validity
                # Default to left if both are None (which shouldn't happen if landmarks exist)
                track_side = "left" 
                current_angle = metrics.get('left_elbow')
                current_flare = metrics.get('left_elbow_flare')
                
                # If right arm is valid and (left is invalid OR right has better angle detection?)
                # Simple logic: If one is None, use the other. If both valid, use the one closer to camera?
                # For now, let's use the one with the more "active" angle or just default to left but switch if left is None
                if metrics.get('right_elbow') is not None:
                     if metrics.get('left_elbow') is None:
                         track_side = "right"
                         current_angle = metrics['right_elbow']
                         current_flare = metrics['right_elbow_flare']
                     else:
                         # Both valid, check visibility if possible or use heuristic
                         # If left elbow is suspiciously straight (180) constant, maybe it's occluded?
                         # Let's stick to left unless it's None for now, but improving this might require visibility scores
                         # Re-implementing with visibility check from landmarks would be better but requires signature change of get_key_metrics
                         # Let's just check if ONE side is fulfilling the "rep" condition better?
                         # Or just check both?
                         
                         # HYBRID APPROACH: Track BOTH. If EITHER completes a rep, count it.
                         # But need to avoid double counting.
                         # Let's stick to a robust "Best Side" selector.
                         pass
                
                # Get visibility from landmarks directly to be robust
                try:
                    l_vis = (landmarks[11].visibility + landmarks[13].visibility + landmarks[15].visibility) / 3
                    r_vis = (landmarks[12].visibility + landmarks[14].visibility + landmarks[16].visibility) / 3
                    if r_vis > l_vis:
                        track_side = "right"
                        current_angle = metrics['right_elbow']
                        current_flare = metrics['right_elbow_flare']
                except:
                    pass

                if current_angle is not None:
                    current_angle_val = current_angle
                    
                    # Track bar path
                    if metrics['wrist_x'] is not None:
                        bar_path_positions.append(metrics['wrist_x'])
                    
                    # Detect bench press reps
                    # Starting position: arms extended (lockout)
                    # Relaxed threshold: > 150 degrees (was 160)
                    if not in_press and current_angle > 150:
                        in_press = True
                        min_elbow_angle = 180
                        max_elbow_flare = 0
                        bar_path_start = metrics['wrist_x'] if metrics['wrist_x'] else 0
                    
                    if in_press:
                        # Track minimum elbow angle (bottom of press)
                        if current_angle < min_elbow_angle:
                            min_elbow_angle = current_angle
                        
                        # Track elbow flare
                        if current_flare is not None and current_flare > max_elbow_flare:
                            max_elbow_flare = current_flare
                    
                    # Complete rep when returning to lockout
                    # Condition: Was in press, returned to > 150, and went deep enough (< 135)
                    # We use 135 to prevent "micro-reps" from noise at the top position
                    if in_press and current_angle > 150 and min_elbow_angle < 135:
                        in_press = False
                        rep_count += 1
                        
                        # Calculate bar path deviation
                        bar_path_deviation = 0
                        if len(bar_path_positions) > 1:
                            bar_path_deviation = max(bar_path_positions) - min(bar_path_positions)
                        bar_path_positions = []
                        
                        rep_data.append({
                            "rep": rep_count,
                            "min_elbow_angle": min_elbow_angle,
                            "max_elbow_flare": max_elbow_flare,
                            "bar_path_deviation": bar_path_deviation,
                            "depth_rating": get_depth_rating(min_elbow_angle)
                        })
                
                # Add metric displays
                image_rgb = add_metric_overlays(image_rgb, metrics)
            
            # Add info panel
            final_image = add_info_panel(image_rgb, frame_count, total_frames, fps, rep_count, 
                                        min_elbow_angle)
            
            # Ensure final frame is uint8
            if final_image.dtype != np.uint8:
                final_image = final_image.astype(np.uint8)
                
            output_frames.append(final_image)

    cap.release()
    
    # Write using MoviePy
    if output_path and output_frames:
        try:
            # Fix for Real Time Coach video speed
            # If it's a recorded video, calculate FPS based on known 10s duration
            if "recorded_video" in os.path.basename(video_path) and len(output_frames) > 0:
                fps = len(output_frames) / 10.0
                print(f"DEBUG: Detected Real Time Coach video. Corrected FPS: {fps}")
            
            # Ensure FPS is valid
            if fps <= 0 or fps > 120:
                fps = 30.0
            
            from moviepy.editor import ImageSequenceClip
            clip = ImageSequenceClip(output_frames, fps=fps)
            clip.write_videofile(output_path, codec='libx264', audio=False, logger=None, preset='ultrafast', threads=4)
        except Exception as e:
            print(f"Error writing video: {e}")
            pass

    # Generate Feedback
    avg_elbow_angle = 0
    feedback_summary = []
    corrections = []
    
    if rep_data:
        avg_elbow_angle = np.mean([r["min_elbow_angle"] for r in rep_data])
        avg_elbow_flare = np.mean([r["max_elbow_flare"] for r in rep_data])
        
        # Depth feedback
        if avg_elbow_angle > 100:
            feedback_summary.append("Insufficient Depth")
            corrections.append("Bar is not reaching chest level.")
            corrections.append("Lower the bar until it lightly touches your chest at nipple level.")
            corrections.append("Practice with lighter weight to build proper ROM.")
        elif 80 <= avg_elbow_angle <= 100:
            feedback_summary.append("Good Depth (NSCA Standard)")
            corrections.append("Excellent depth achieved.")
            corrections.append("Maintain this form as you progress.")
        else:
            feedback_summary.append("Full ROM")
            corrections.append("Great range of motion.")
            corrections.append("Ensure you're not bouncing the bar off your chest.")
        
        # Elbow flare feedback
        if avg_elbow_flare > 75:
            feedback_summary.append("Excessive Elbow Flare")
            corrections.append("Elbows are flaring out too much.")
            corrections.append("Keep elbows at 30-75° from torso to protect shoulders.")
            corrections.append("Think about 'tucking' your elbows slightly.")
        elif avg_elbow_flare < 30:
            feedback_summary.append("Elbows Too Tucked")
            corrections.append("Elbows are too close to your sides.")
            corrections.append("Allow natural 30-75° angle for optimal chest activation.")
        
    else:
        feedback_summary.append("No Reps Detected")
        corrections.append("Could not detect full bench press reps.")
        corrections.append("Ensure your full upper body is visible in the frame.")
        corrections.append("Film from the side for best results.")

    return {
        "reps_count": rep_count,
        "avg_elbow_angle": int(avg_elbow_angle) if avg_elbow_angle else 0,
        "feedback": feedback_summary,
        "corrections": corrections,
        "rep_details": rep_data
    }
