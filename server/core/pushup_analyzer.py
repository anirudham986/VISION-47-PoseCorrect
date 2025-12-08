
import cv2
import mediapipe as mp
import numpy as np
import os
from moviepy.editor import ImageSequenceClip
from .biomechanics import get_exercise_angles, get_exercise_errors

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

def get_form_rating(elbow_angle, hip_drop):
    """Rate push-up form using biomechanics stats"""
    angles = get_exercise_angles("pushup")
    elbow_data = angles.get("elbow", {})
    ideal = elbow_data.get("ideal", 90)
    
    if elbow_angle > 120:
        depth = "Very Shallow"
    elif elbow_angle > 100:
        depth = "Shallow"
    elif elbow_angle > 80:
        depth = "Good Depth"
    else:
        depth = "Excellent Depth"
    
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
        
        # Shoulder angle relative to torso
        r_shoulder = pixel_coord(12)
        hip_mid = (
            (pixel_coord(23)[0] + pixel_coord(24)[0]) // 2,
            (pixel_coord(23)[1] + pixel_coord(24)[1]) // 2
        )
        metrics['shoulder_angle'] = calculate_angle(l_elbow, l_shoulder, hip_mid)
        
        # Hip drop 
        l_ankle = pixel_coord(27)
        r_ankle = pixel_coord(28)
        ankle_mid = (
            (l_ankle[0] + r_ankle[0]) // 2,
            (l_ankle[1] + r_ankle[1]) // 2
        )
        shoulder_mid = (
            (l_shoulder[0] + r_shoulder[0]) // 2,
            (l_shoulder[1] + r_shoulder[1]) // 2
        )
        
        shoulder_ankle_line = np.array(ankle_mid) - np.array(shoulder_mid)
        hip_point = np.array(hip_mid)
        shoulder_point = np.array(shoulder_mid)
        
        line_vec = np.array(ankle_mid) - shoulder_point
        point_vec = hip_point - shoulder_point
        cross = np.cross(line_vec, point_vec)
        distance = np.linalg.norm(cross) / np.linalg.norm(line_vec)
        metrics['hip_drop'] = int(distance)
        
    except Exception as e:
        metrics = {k: None for k in ['left_elbow', 'shoulder_angle', 'hip_drop']}
    
    return metrics

def add_overlays(image, metrics):
    y_pos = 40
    angles = get_exercise_angles("pushup")
    goal = angles.get("elbow", {}).get("ideal", 90)
    
    if metrics['left_elbow'] is not None:
        color = (0, 255, 0) if 80 <= metrics['left_elbow'] <= 100 else (0, 0, 255)
        cv2.putText(image, f"Elbow: {metrics['left_elbow']} (Goal: {goal})", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return image

def add_info_panel(image, fps, reps, current_angle):
    h, w = image.shape[:2]
    panel = np.zeros((80, w, 3), dtype=np.uint8)
    panel[:, :] = (40, 40, 40)
    image = np.vstack([image, panel])
    
    cv2.putText(image, f"Reps: {reps}", (30, h + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(image, f"Angle: {current_angle}", (200, h + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return image

def analyze_pushup_video(video_path, output_path=None):
    print(f"DEBUG: Pushup Analysis - Input: {video_path}")
    if not os.path.exists(video_path): 
        print("DEBUG: Video file does not exist")
        return {"error": "Video not found"}
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): 
        print("DEBUG: Failed to open video capture")
        return {"error": "Cannot open video"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"DEBUG: Video Props - Size: {width}x{height}, FPS: {fps}, Frames: {total_frames}")
    
    # Store frames for MoviePy
    output_frames = []

    rep_data = []
    in_pushup = False
    rep_count = 0
    min_elbow_angle = 180
    max_hip_drop = 0
    
    frame_count = 0
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"DEBUG: Processing frame {frame_count}/{total_frames}")
            
            # Convert to RGB for MediaPipe AND MoviePy
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            # Draw on RGB image for MoviePy output (OpenCV drawing functions work on RGB numpy arrays too if we don't convert back to BGR)
            # Actually simplest flow: Process RGB, Draw on RGB, Store RGB
            
            current_angle = 0
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                metrics = get_key_metrics(results.pose_landmarks.landmark, width, height)
                
                if metrics['left_elbow'] is not None:
                    current_angle = metrics['left_elbow']
                    
                    if not in_pushup and current_angle < 140:
                        in_pushup = True
                        min_elbow_angle = 180
                        max_hip_drop = 0
                        
                    if in_pushup:
                        if current_angle < min_elbow_angle: min_elbow_angle = current_angle
                        if metrics['hip_drop'] and metrics['hip_drop'] > max_hip_drop: max_hip_drop = metrics['hip_drop']
                        
                    if in_pushup and current_angle > 160:
                        in_pushup = False
                        rep_count += 1
                        rep_data.append({
                            "rep": rep_count,
                            "min_elbow_angle": min_elbow_angle,
                            "max_hip_drop": max_hip_drop,
                            "form_rating": get_form_rating(min_elbow_angle, max_hip_drop)
                        })
                image_rgb = add_overlays(image_rgb, metrics)
            
            final_image = add_info_panel(image_rgb, fps, rep_count, current_angle)
            output_frames.append(final_image)
            
    cap.release()
    print("DEBUG: Analysis loop finished")
    
    # Write using MoviePy
    if output_path and output_frames:
        try:
            print(f"DEBUG: Writing {len(output_frames)} frames to {output_path} with MoviePy...")
            clip = ImageSequenceClip(output_frames, fps=fps)
            # Use libx264 for H.264 encoding which is web standard
            clip.write_videofile(output_path, codec='libx264', audio=False, logger=None, preset='ultrafast', threads=4)
            print("DEBUG: Video writing complete")
        except Exception as e:
            print(f"DEBUG: MoviePy writing failed: {str(e)}")
            return {"error": f"Encoding failed: {str(e)}"}
    
    avg_depth = 0
    feedback = []
    corrections = []
    
    # Biomechanics
    angles_std = get_exercise_angles("pushup")
    errors = get_exercise_errors("pushup")
    ideal_depth = angles_std.get("elbow", {}).get("ideal", 90)
    
    if rep_data:
        avg_depth = np.mean([r["min_elbow_angle"] for r in rep_data])
        avg_hip_drop = np.mean([r["max_hip_drop"] for r in rep_data])
        
        if avg_depth > 100:
            feedback.append("Insufficient Depth")
            corrections.append(f"Lower your chest closer to the floor (goal: {ideal_depth}° elbows).")
        elif avg_depth < 80:
            feedback.append("Excellent Range of Motion")
        else:
            feedback.append("Good Depth")
            
        if avg_hip_drop > 20:
            feedback.append("Hip Sag Detected")
            corrections.append(f"{errors.get('hip_sag', {}).get('message', 'Engage core')}")
            corrections.append("Engage your core to keep your body in a straight line.")
    else:
        feedback.append("No Reps Detected")
        corrections.append("Ensure full extension at top and significant bend at bottom.")

    return {
        "reps_count": rep_count,
        "avg_depth": int(avg_depth),
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": rep_data
    }
