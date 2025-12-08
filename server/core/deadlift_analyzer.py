
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

def analyze_deadlift_video(video_path, output_path=None):
    if not os.path.exists(video_path): return {"error": "Video not found"}
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return {"error": "Cannot open video"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Output frames
    output_frames = []

    rep_count = 0
    state = "down" # down (weights on floor), up (standing)
    feedback = []
    corrections = []
    
    back_angles = []

    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            hip_angle = 0
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                lm = results.pose_landmarks.landmark
                
                def get_pt(idx): return [lm[idx].x * width, lm[idx].y * height]
                
                # Check hips extension (Shoulder - Hip - Knee)
                # Standing up: Angle ~ 170-180
                # Bent over: Angle ~ 45-90
                
                s_h_k = calculate_angle(get_pt(11), get_pt(23), get_pt(25)) # Left side
                hip_angle = s_h_k
                back_angles.append(hip_angle)
                
                if state == "down":
                    if hip_angle > 160: # Standing up
                        state = "up"
                        rep_count += 1
                elif state == "up":
                    if hip_angle < 100: # Back down
                        state = "down"

            # Overlay
            panel = np.zeros((80, width, 3), dtype=np.uint8)
            panel[:, :] = (40, 40, 40)
            final = np.vstack([image_rgb, panel])
            cv2.putText(final, f"Reps: {rep_count}", (30, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(final, f"Hip Angle: {hip_angle}", (200, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
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
        feedback.append("Good Hinge Movement")
        corrections.append("Keep your back flat and chest up.")
    else:
        feedback.append("No Full Reps")
        corrections.append("Ensure you stand up fully to lock out the hips.")

    return {
        "reps_count": rep_count,
        "avg_depth": 0, 
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": []
    }
