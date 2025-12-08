import cv2
import mediapipe as mp
import numpy as np
import time
import os
import sys

def analyze_video_with_skeleton(video_path, output_video=None, show_preview=True):
    """
    Analyze video and show skeleton overlay throughout
    
    Args:
        video_path: Path to input video
        output_video: Path to save analyzed video (optional)
        show_preview: Show live preview window
    """
    
    print("=" * 60)
    print("🏋️‍♂️ EXERCISE VIDEO ANALYZER WITH SKELETON OVERLAY")
    print("=" * 60)
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ ERROR: Video file not found!")
        print(f"   Looking for: {video_path}")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Files in directory: {os.listdir('.')}")
        return None
    
    # Initialize MediaPipe
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Create Pose instance
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,  # 0=Light, 1=Full, 2=Heavy
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ ERROR: Cannot open video file!")
        print("   Possible issues:")
        print("   - File corrupted")
        print("   - Wrong codec format")
        print("   - File in use by another program")
        return None
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📹 VIDEO INFO:")
    print(f"   File: {os.path.basename(video_path)}")
    print(f"   Resolution: {width} x {height}")
    print(f"   FPS: {fps:.1f}")
    print(f"   Total frames: {total_frames}")
    print(f"   Duration: {duration:.1f} seconds")
    print("-" * 60)
    
    # Prepare output video writer
    out = None
    if output_video:
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_video) if os.path.dirname(output_video) else '.', exist_ok=True)
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID' for avi
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        print(f"💾 Will save analyzed video to: {output_video}")
    
    # Initialize variables
    frame_count = 0
    pose_detected_count = 0
    start_time = time.time()
    
    # Color scheme for different body parts
    skeleton_color = (0, 255, 0)  # Green skeleton
    angle_color = (255, 255, 0)   # Yellow for angles
    info_color = (255, 100, 0)    # Orange for info
    
    # Joint connections for angle calculations
    JOINT_PAIRS = [
        ("Left Shoulder", 11), ("Left Elbow", 13), ("Left Wrist", 15),
        ("Right Shoulder", 12), ("Right Elbow", 14), ("Right Wrist", 16),
        ("Left Hip", 23), ("Left Knee", 25), ("Left Ankle", 27),
        ("Right Hip", 24), ("Right Knee", 26), ("Right Ankle", 28)
    ]
    
    print("▶️  Starting video analysis...")
    print("   Press 'Q' to quit")
    print("   Press 'P' to pause/resume")
    print("   Press 'S' to save screenshot")
    print("-" * 60)
    
    paused = False
    last_print_time = time.time()
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Show progress every 50 frames or 5 seconds
            current_time = time.time()
            if current_time - last_print_time > 5.0:
                progress = (frame_count / total_frames) * 100
                elapsed = current_time - start_time
                eta = (elapsed / frame_count) * (total_frames - frame_count) if frame_count > 0 else 0
                
                print(f"   Progress: {progress:.1f}% ({frame_count}/{total_frames}) | "
                      f"Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")
                last_print_time = current_time
            
            # Convert BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            
            # Process with MediaPipe
            results = pose.process(frame_rgb)
            
            # Convert back to BGR for OpenCV
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                pose_detected_count += 1
                
                # Draw full skeleton with custom styling
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=skeleton_color, thickness=3, circle_radius=3
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=skeleton_color, thickness=2
                    )
                )
                
                # Get all landmarks
                landmarks = results.pose_landmarks.landmark
                h, w = frame.shape[:2]
                
                # Function to convert normalized coordinates to pixel coordinates
                def get_pixel_coord(landmark_idx):
                    lm = landmarks[landmark_idx]
                    return (int(lm.x * w), int(lm.y * h))
                
                # Calculate and display key angles
                angles_to_display = []
                
                # LEFT ARM ANGLES
                try:
                    l_shoulder = get_pixel_coord(11)
                    l_elbow = get_pixel_coord(13)
                    l_wrist = get_pixel_coord(15)
                    
                    # Calculate left elbow angle
                    l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
                    angles_to_display.append(("L Elbow", l_elbow_angle, l_elbow))
                    
                    # Calculate left shoulder angle (hip-shoulder-elbow)
                    l_hip = get_pixel_coord(23)
                    l_shoulder_angle = calculate_angle(l_hip, l_shoulder, l_elbow)
                    angles_to_display.append(("L Shoulder", l_shoulder_angle, l_shoulder))
                except:
                    pass
                
                # RIGHT ARM ANGLES
                try:
                    r_shoulder = get_pixel_coord(12)
                    r_elbow = get_pixel_coord(14)
                    r_wrist = get_pixel_coord(16)
                    
                    # Calculate right elbow angle
                    r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                    angles_to_display.append(("R Elbow", r_elbow_angle, r_elbow))
                    
                    # Calculate right shoulder angle
                    r_hip = get_pixel_coord(24)
                    r_shoulder_angle = calculate_angle(r_hip, r_shoulder, r_elbow)
                    angles_to_display.append(("R Shoulder", r_shoulder_angle, r_shoulder))
                except:
                    pass
                
                # LEFT LEG ANGLES
                try:
                    l_hip = get_pixel_coord(23)
                    l_knee = get_pixel_coord(25)
                    l_ankle = get_pixel_coord(27)
                    
                    l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
                    angles_to_display.append(("L Knee", l_knee_angle, l_knee))
                except:
                    pass
                
                # RIGHT LEG ANGLES
                try:
                    r_hip = get_pixel_coord(24)
                    r_knee = get_pixel_coord(26)
                    r_ankle = get_pixel_coord(28)
                    
                    r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
                    angles_to_display.append(("R Knee", r_knee_angle, r_knee))
                except:
                    pass
                
                # Display angles on frame
                for joint_name, angle, position in angles_to_display:
                    # Put angle text near the joint
                    text = f"{joint_name}: {angle}°"
                    text_position = (position[0] + 10, position[1] - 10)
                    
                    # Draw background rectangle for better visibility
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(frame,
                                (text_position[0] - 5, text_position[1] - text_size[1] - 5),
                                (text_position[0] + text_size[0] + 5, text_position[1] + 5),
                                (0, 0, 0), -1)
                    
                    # Draw angle text
                    cv2.putText(frame, text, text_position,
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, angle_color, 2)
                
                # Print angles to console for selected frames
                if frame_count % 10 == 0:  # Every 10th frame
                    timestamp = frame_count / fps
                    print(f"Frame {frame_count:4d} ({timestamp:5.1f}s): ", end="")
                    for joint_name, angle, _ in angles_to_display[:2]:  # Show first 2 angles
                        print(f"{joint_name}: {angle:3d}° ", end="")
                    print()
        
        # Add informational overlay
        overlay_height = 120
        overlay = np.zeros((overlay_height, width, 3), dtype=np.uint8)
        
        # Add overlay to bottom of frame
        frame_with_overlay = np.vstack([frame, overlay])
        
        # Add info text to overlay
        info_y_start = height + 20
        
        # Frame info
        timestamp = frame_count / fps if fps > 0 else 0
        cv2.putText(frame_with_overlay, f"Frame: {frame_count}/{total_frames}",
                   (20, info_y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 2)
        cv2.putText(frame_with_overlay, f"Time: {timestamp:.1f}s",
                   (20, info_y_start + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 2)
        
        # Detection info
        detection_rate = (pose_detected_count / frame_count * 100) if frame_count > 0 else 0
        cv2.putText(frame_with_overlay, f"Pose detected: {detection_rate:.1f}%",
                   (20, info_y_start + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 2)
        
        # Instructions
        cv2.putText(frame_with_overlay, "Controls: Q=Quit | P=Pause | S=Screenshot",
                   (width - 400, info_y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Exercise info (you can customize this)
        cv2.putText(frame_with_overlay, "Exercise: Squat Analysis",
                   (width - 400, info_y_start + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Angle legend
        if angles_to_display:
            legend_x = width - 400
            legend_y = info_y_start + 50
            for i, (joint_name, angle, _) in enumerate(angles_to_display[:3]):  # Show first 3
                cv2.putText(frame_with_overlay, f"{joint_name}: {angle}°",
                           (legend_x, legend_y + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, angle_color, 2)
        
        # Show video preview
        if show_preview:
            cv2.namedWindow('Exercise Analysis - Skeleton Overlay', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Exercise Analysis - Skeleton Overlay', min(1280, width), min(800, height + overlay_height))
            cv2.imshow('Exercise Analysis - Skeleton Overlay', frame_with_overlay)
        
        # Write to output video if enabled
        if out is not None:
            out.write(frame_with_overlay if show_preview else frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1 if not paused else 0) & 0xFF
        
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("\n⏹️  Stopping analysis...")
            break
        elif key == ord('p'):  # 'p' to pause/resume
            paused = not paused
            print(f"   {'⏸️  Paused' if paused else '▶️  Resumed'}")
        elif key == ord('s'):  # 's' to save screenshot
            screenshot_path = f"screenshot_frame_{frame_count}.jpg"
            cv2.imwrite(screenshot_path, frame_with_overlay if show_preview else frame)
            print(f"   💾 Saved screenshot: {screenshot_path}")
        elif key == ord('f'):  # 'f' to skip forward 60 frames (2 seconds at 30fps)
            if not paused:
                new_pos = frame_count + 60
                if new_pos < total_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                    frame_count = new_pos - 1
                    print(f"   ⏩ Skipped forward 2 seconds")
        elif key == ord('b'):  # 'b' to skip backward 60 frames
            if not paused:
                new_pos = max(0, frame_count - 60)
                cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                frame_count = new_pos - 1
                print(f"   ⏪ Skipped backward 2 seconds")
    
    # Cleanup
    cap.release()
    if out is not None:
        out.release()
    pose.close()
    
    if show_preview:
        cv2.destroyAllWindows()
    
    # Print final summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"✅ Total frames processed: {frame_count}")
    print(f"✅ Frames with pose detected: {pose_detected_count} ({pose_detected_count/frame_count*100:.1f}%)")
    print(f"✅ Total processing time: {elapsed_time:.1f} seconds")
    print(f"✅ Processing speed: {frame_count/elapsed_time:.1f} FPS")
    
    if output_video and os.path.exists(output_video):
        print(f"✅ Analyzed video saved: {output_video}")
        file_size = os.path.getsize(output_video) / (1024 * 1024)  # MB
        print(f"   File size: {file_size:.1f} MB")
    
    print("=" * 60)
    return frame_count

def calculate_angle(a, b, c):
    """
    Calculate the angle at point b formed by points a, b, c
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate cosine of angle
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Handle floating point errors
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    # Calculate angle in degrees
    angle = np.degrees(np.arccos(cosine_angle))
    
    return int(round(angle))

def create_test_video():
    """
    Create a test video if no video is available
    """
    print("📹 Creating test video...")
    
    # Create a simple animation of a person doing squats
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration
    
    # Create output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    test_video_path = 'test_squat_video.mp4'
    out = cv2.VideoWriter(test_video_path, fourcc, fps, (width, height))
    
    for frame_idx in range(total_frames):
        # Create blank frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = (40, 40, 40)  # Dark gray background
        
        # Calculate squat position (sin wave for up/down motion)
        t = frame_idx / total_frames
        squat_depth = np.sin(t * 4 * np.pi) * 0.4 + 0.5  # 0.1 to 0.9
        
        # Draw a simple stick figure doing squats
        center_x, center_y = width // 2, height // 2
        
        # Head
        head_radius = 20
        head_y = int(center_y - 100 * squat_depth)
        cv2.circle(frame, (center_x, head_y), head_radius, (255, 255, 255), -1)
        
        # Body
        body_length = 80
        body_end_y = head_y + head_radius + body_length
        cv2.line(frame, (center_x, head_y + head_radius), 
                (center_x, body_end_y), (255, 255, 255), 3)
        
        # Arms
        arm_angle = 45 * (1 - squat_depth)  # Arms move with squat
        arm_length = 60
        
        # Left arm
        left_arm_end = (
            int(center_x - arm_length * np.cos(np.radians(arm_angle))),
            int(body_end_y - 40 - arm_length * np.sin(np.radians(arm_angle)))
        )
        cv2.line(frame, (center_x, body_end_y - 40), left_arm_end, (255, 255, 255), 3)
        
        # Right arm
        right_arm_end = (
            int(center_x + arm_length * np.cos(np.radians(arm_angle))),
            int(body_end_y - 40 - arm_length * np.sin(np.radians(arm_angle)))
        )
        cv2.line(frame, (center_x, body_end_y - 40), right_arm_end, (255, 255, 255), 3)
        
        # Legs
        leg_length = 100
        leg_spread = 30 * squat_depth  # Legs spread more at bottom
        
        # Left leg
        left_leg_end = (
            int(center_x - leg_spread),
            int(body_end_y + leg_length)
        )
        cv2.line(frame, (center_x, body_end_y), left_leg_end, (255, 255, 255), 3)
        
        # Right leg
        right_leg_end = (
            int(center_x + leg_spread),
            int(body_end_y + leg_length)
        )
        cv2.line(frame, (center_x, body_end_y), right_leg_end, (255, 255, 255), 3)
        
        # Add text
        cv2.putText(frame, "TEST VIDEO: Person Doing Squats", (50, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Frame: {frame_idx}/{total_frames}", (50, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "MediaPipe will detect this skeleton", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Created test video: {test_video_path}")
    print(f"   Duration: {duration} seconds, {total_frames} frames")
    
    return test_video_path

def main():
    """Main function to run the analyzer"""
    
    print("🎬 VIDEO SKELETON ANALYZER")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Look for video files in current directory
        video_files = []
        for ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']:
            video_files.extend([f for f in os.listdir('.') if f.lower().endswith(ext)])
        
        if not video_files:
            print("📹 No video files found in current directory.")
            print("   Creating a test video...")
            video_path = create_test_video()
        else:
            print("📹 Available video files:")
            for i, f in enumerate(video_files, 1):
                print(f"   {i}. {f}")
            
            try:
                choice = input(f"\nSelect video (1-{len(video_files)}) or press Enter for first: ").strip()
                if choice == "":
                    video_path = video_files[0]
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_path = video_files[idx]
                    else:
                        print("❌ Invalid choice. Using first video.")
                        video_path = video_files[0]
            except:
                print("❌ Invalid input. Using first video.")
                video_path = video_files[0]
        
        # Ask for output filename
        default_output = video_path.replace('.mp4', '_analyzed.mp4').replace('.avi', '_analyzed.avi')
        save_output = input(f"\nSave analyzed video? (y/n) [default: {default_output}]: ").strip().lower()
        
        if save_output == 'y' or save_output == '':
            custom_name = input(f"Output filename [{default_output}]: ").strip()
            output_path = custom_name if custom_name else default_output
        else:
            output_path = None
    
    # Ask for preview preference
    show_preview = input("\nShow live preview? (y/n) [y]: ").strip().lower()
    show_preview = not (show_preview == 'n')
    
    # Run analysis
    print("\n" + "=" * 50)
    analyze_video_with_skeleton(video_path, output_path, show_preview)
    
    print("\n🎉 Analysis complete! Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()