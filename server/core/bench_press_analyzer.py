
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

def analyze_bench_press_video(video_path, output_path=None):
    if not os.path.exists(video_path): return {"error": "Video not found"}
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return {"error": "Cannot open video"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height + 80))

    rep_count = 0
    state = "up" # up (arms extended), down (bar on chest)
    feedback = []
    corrections = []

    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            elbow_angle = 0
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                lm = results.pose_landmarks.landmark
                
                def get_pt(idx): return [lm[idx].x * width, lm[idx].y * height]
                
                # Check Elbow extension (Shoulder - Elbow - Wrist)
                left_elbow = calculate_angle(get_pt(11), get_pt(13), get_pt(15))
                elbow_angle = left_elbow
                
                if state == "up":
                    if elbow_angle < 80: # Bar came down
                        state = "down"
                elif state == "down":
                    if elbow_angle > 150: # Pushed back up
                        state = "up"
                        rep_count += 1

            # Overlay
            panel = np.zeros((80, width, 3), dtype=np.uint8)
            panel[:, :] = (40, 40, 40)
            final = np.vstack([image, panel])
            cv2.putText(final, f"Reps: {rep_count}", (30, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(final, f"Elbow Angle: {elbow_angle}", (200, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            if out: out.write(final)
            
    cap.release()
    if out: out.release()
    
    if rep_count > 0:
        feedback.append("Good Extensions")
        corrections.append("Keep elbows tucked at 45 degrees.")
    else:
        feedback.append("No Reps Detected")
        corrections.append("Ensure full range of motion (touch chest, fully extend).")

    return {
        "reps_count": rep_count,
        "avg_depth": 0, 
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": []
    }
