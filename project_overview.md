# VISION-47 PoseCorrect - Project Overview

## 1. Project Description
**GymBro AI** (VISION-47-PoseCorrect) is an AI-powered fitness application that analyzes exercise form using computer vision. Users upload videos of exercises (Squat, Pushup, Pullup, Deadlift, Bench Press), and the system provides real-time feedback, rep counting, and visual corrections.

---

## 2. System Architecture

The project follows a modern **Client-Server Architecture**:

### **Frontend (Client)**
- **Framework**: React.js (built with Vite)
- **Styling**: CSS Modules / Standard CSS
- **Routing**: React Router
- **Key Libraries**: `framer-motion` (animations), `lucide-react` (icons)
- **Responsibility**: Handles user UI, video upload, and displaying analysis results.

### **Backend (Server)**
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **AI/CV Engine**: MediaPipe (Pose Estimation), OpenCV (Image Processing), MoviePy (Video Generation)
- **Responsibility**: Receives video files, runs frame-by-frame analysis, generates annotated videos, and returns JSON feedback.

---

## 3. Data Flow

1.  **User Action**: User selects an exercise (e.g., Squat) and uploads a video file via the Frontend (`/upload`).
2.  **API Request**: Frontend sends a `POST` request to `http://localhost:8000/analyze` with the video file and `exercise_type`.
3.  **Backend Processing**:
    *   FastAPI receives the file and saves it to `server/uploads/`.
    *   Based on `exercise_type`, the corresponding analyzer is called (e.g., `analyze_squat_video`).
    *   **Frame Loop**:
        *   Read frame -> Convert to RGB.
        *   **MediaPipe Pose**: Detects 33 body landmarks (shoulders, hips, knees, ankles, etc.).
        *   **Angle Calculation**: Computes geometric angles (e.g., Hip-Knee-Ankle for squat depth).
        *   **Logic Check**: Compares angles against biomechanical thresholds to count reps and detect errors.
        *   **Annotation**: Draws skeleton and feedback overlays on the frame.
    *   **Video Generation**: Annotated frames are compiled into a new video using `MoviePy`.
4.  **Response**: Backend returns a JSON object containing:
    *   `reps_count`: Total reps performed.
    *   `feedback`: List of form corrections (e.g., "Insufficient Depth").
    *   `video_url`: Link to the processed video.
5.  **Display**: Frontend receives the JSON, displays the stats, and plays the returned video URL.

---

## 4. Key Files & Structure

### **Root Directory**
*   `project_overview.md`: This documentation file.
*   `system_architecture.md`: High-level system design document.

### **Frontend (`/client`)**
*   `package.json`: Manages JavaScript dependencies and scripts (`npm run dev`).
*   `src/main.jsx`: Entry point for React.
*   `src/App.jsx`: Main routing logic.
*   `src/pages/`:
    *   `Dashboard.jsx`: Main hub for selecting exercises.
    *   `VideoAnalysis.jsx`: Handles file upload and displaying results.
    *   `LandingPage.jsx`: Intro screen.

### **Backend (`/server`)**
*   `main.py`: Entry point for FastAPI. Defines API routes, CORS settings, and routes requests to analyzers.
*   `requirements.txt`: Python dependencies list.
*   `uploads/`: Temporary storage for raw user videos.
*   `outputs/`: Storage for processed/annotated videos.
*   **`core/` (Analysis Logic)**:
    *   `squat_analyzer.py`: Logic for analyzing squats.
    *   `pushup_analyzer.py`: Logic for pushups.
    *   `pullup_analyzer.py`, `deadlift_analyzer.py`, `bench_press_analyzer.py`, `biomechanics.py`.

---

## 5. Packages & Versions

### **Frontend Dependencies** (from `client/package.json`)
*   `react` (^18.3.1): UI Library.
*   `vite` (^5.4.1): Build tool.
*   `framer-motion` (^11.5.4): For fluid UI animations.
*   `lucide-react` (^0.439.0): Icon set.
*   `react-router-dom` (^6.26.1): Navigation.

### **Backend Dependencies** (from `server/requirements.txt`)
*   `fastapi` (>=0.100.0): Web framework.
*   `uvicorn` (>=0.23.0): ASGI server.
*   **`moviepy` (1.0.3)**: **CRITICAL**. Must be `<2.0.0` to avoid compatibility issues with the code.
*   **`numpy` (1.26.4)**: **CRITICAL**. Must be `<2.0.0` to work with MoviePy 1.x and OpenCV.
*   `opencv-python-headless`: For video frame manipulation.
*   `mediapipe` (>=0.10.8): Google's ML solution for high-fidelity pose tracking.

---

## 6. How the Model Works (Prediction Logic)

The "prediction" is a deterministic algorithm based on geometric analysis of Pose Coordinates, not a black-box neural network classification (though MediaPipe itself is a neural network).

**Example: Squat Analysis (`squat_analyzer.py`)**

1.  **Input**: A single video frame.
2.  **Pose Estimation**: MediaPipe returns `(x, y, z)` coordinates for landmarks.
    *   *Key Landmarks*: Left Hip (23), Left Knee (25), Left Ankle (27).
3.  **Feature Extraction (Angle Calculation)**:
    *   The system calculates the **Knee Angle** using the vector dot product formula between the Hip-Knee and Knee-Ankle vectors.
4.  **State Machine (The "Prediction")**:
    *   **Start State**: Standing (Angle > 165°).
    *   **Descent**: Angle decreases.
    *   **Bottom Check**: If Angle < **150°**, the system flags `in_squat = True`.
    *   **Depth Rating**:
        *   Angle < 80°: "Excellent Depth" (Deep Squat)
        *   80° < Angle < 100°: "Good Depth" (Parallel)
        *   Angle > 100°: "Shallow" (Partial Rep)
    *   **Ascent**: Angle increases.
    *   **Rep Completion**: If `in_squat` was True and Angle returns to > **165°**, a rep is counted (`rep_count += 1`).
5.  **Feedback Generation**:
    *   The system tracks the *minimum* angle reached during the rep.
    *   It appends text feedback (e.g., "Go Deeper") based on that minimum value.

**Note on Constraints**:
*   The current logic primarily tracks the **LEFT side**. Videos must be filmed from the user's left profile for accurate detection.
