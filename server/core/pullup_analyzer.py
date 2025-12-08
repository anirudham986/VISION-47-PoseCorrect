
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
    max_extension = 0
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # RGB for MediaPipe and MoviePy
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            
            current_ext = 0
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark
                
                def get_pt(idx): return [landmarks[idx].x * width, landmarks[idx].y * height]
                
                # Calculate Elbow Angle (Shoulder-Elbow-Wrist) for Extension tracking
                # We use left side for simplicity, ideally avg of both
                l_elbow_ang = calculate_angle(get_pt(11), get_pt(13), get_pt(15))
                current_ext = l_elbow_ang
                
                # Pullup Logic ( Chin over bar )
                nose_y = landmarks[0].y
                wrist_y = (landmarks[15].y + landmarks[16].y) / 2
                
                is_above_bar = nose_y < wrist_y
                
                if state == "down":
                    if is_above_bar:
                        state = "up"
                        rep_count += 1
                        max_extension = 0 # Reset for next drop
                elif state == "up":
                    if not is_above_bar:
                         state = "down"
                         # Track max extension during the "down" phase
                
                # Continuously track max extension in "down" state (or returning to it)
                if state == "down" and current_ext > max_extension:
                    max_extension = current_ext
                    if rep_count > 0 and len(rep_data) < rep_count:
                         # Append data for the COMPLETED rep (which just finished going down)
                         # Wait, logic is tricky. usually we log AFTER the full cycle.
                         # Simplified: Just log the max extension found between reps.
                         pass
                
                # Correct Logic: 
                # Rep starts at bottom (Extension ~180).
                # Goes UP (Extension ~40).
                # Goes DOWN (Extension ~180).
                # We count rep at TOP usually. 
                # Let's log the "Previous Rep's Extension" when we hit top of NEXT rep?
                # Or just append to rep_data when we return to "down" state fully?
                
                if state == "down" and current_ext > 160: 
                     # We are at bottom. If we have a rep count that isn't logged, log it.
                     if rep_count > len(rep_data):
                         rep_data.append({
                             "rep": rep_count,
                             "extension": max_extension
                         })

            # Overlay
            panel = np.zeros((80, width, 3), dtype=np.uint8)
            panel[:, :] = (40, 40, 40)
            final = np.vstack([image_rgb, panel])
            cv2.putText(final, f"Reps: {rep_count}", (30, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(final, f"Ext: {current_ext}", (200, height + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
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
    
    avg_extension = 0
    feedback = []
    corrections = []
    
    if rep_data:
        avg_extension = np.mean([r["extension"] for r in rep_data])
        
        if avg_extension < 140:
             feedback.append("Poor Extension")
             corrections.append("Fully straighten your arms at the bottom.")
        elif avg_extension < 160:
             feedback.append("Good Range")
             corrections.append("Try to relax into a dead hang for full benefit.")
        else:
             feedback.append("Excellent Form")
             corrections.append("Great full range of motion!")
    else:
        if rep_count == 0:
            feedback.append("No Reps Detected")
            corrections.append("Ensure your chin clears the bar.")

    return {
        "reps_count": rep_count,
        "avg_depth": int(avg_extension), # Sending extension as standard "depth" metric
        "feedback": feedback,
        "corrections": corrections,
        "rep_details": rep_data
    }
