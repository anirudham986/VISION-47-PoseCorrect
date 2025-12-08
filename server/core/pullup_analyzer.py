
import cv2
import mediapipe as mp
import numpy as np
import os

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    return int(np.degrees(np.arccos(cosine_angle)))

def analyze_pullup_video(video_path, output_path=None):
    if not os.path.exists(video_path): return {"error": "Video not found"}
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return {"error": "Cannot open video"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Output storage
    output_frames = []

    rep_data = []
    state = "down" # down, up
    rep_count = 0
    
    feedback = []
    corrections = []
    
    min_chim_clearance = float('inf') 
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # RGB for MediaPipe and MoviePy
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            status_text = "Analysis Running"
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                landmarks = results.pose_landmarks.landmark
                
                # Coordinates
                l_wrist = landmarks[15]
                r_wrist = landmarks[16]
                l_shoulder = landmarks[11]
                r_shoulder = landmarks[12]
                nose = landmarks[0]
                
                # Y coords (image coordinates, 0 is top)
                wrist_y = (l_wrist.y + r_wrist.y) / 2
                shoulder_y = (l_shoulder.y + r_shoulder.y) / 2
                nose_y = nose.y
                
                is_above_bar = nose_y < wrist_y
                is_full_hang = (shoulder_y - wrist_y) > 0.3 
                
                if state == "down":
                    if is_above_bar:
                        state = "up"
                        rep_count += 1
                elif state == "up":
                    if not is_above_bar and (shoulder_y - wrist_y) > 0.2: # Returning down
                        state = "down"
                        
            # Overlay
            panel = np.zeros((80, width, 3), dtype=np.uint8)
            panel[:, :] = (40, 40, 40)
            final = np.vstack([image_rgb, panel])
            cv2.putText(final, f"Reps: {rep_count}", (30, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            output_frames.append(final)
            
    cap.release()
    
    # Write using MoviePy
    if output_path and output_frames:
        try:
            from moviepy.editor import ImageSequenceClip
            clip = ImageSequenceClip(output_frames, fps=fps)
            clip.write_videofile(output_path, codec='libx264', audio=False, logger=None)
        except Exception as e:
            print(f"Error writing video: {e}")
            return {"error": str(e)}
    
    if rep_count > 0:
        feedback.append("Great Effort")
        corrections.append("Focus on full extension at the bottom.")
    else:
        feedback.append("No Reps Detected")
        corrections.append("Try to clear your chin above the bar (or wrists).")

    return {
        "reps_count": rep_count,
        "avg_depth": 0, # Not applicable really
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": []
    }
