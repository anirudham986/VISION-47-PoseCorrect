# GYMBRO - AI Fitness Coach 🏋️‍♂️🤖

**Your Personal Trainer, Reimagined.**

Gymbro is a next-generation full-stack fitness application that leverages computer vision to provide professional-grade form analysis. It combines a sleek React frontend with a powerful Python AI backend to democratize fitness coaching.

![Gymbro Demo](assets/FinalDemo.mp4)

---

## 🚀 Key Features

### 🟢 AI Video Analysis (Upload & Analyze)
Upload your workout videos to get instant, frame-by-frame biomechanical analysis.
*   **Squat Analyzer**: Checks for NSCA-standard depth (Hip crease below knee top) and torso alignment.
*   **Deadlift Analyzer**: Tracks "Setup → Pull → Lockout" phases, ensuring back neutrality (40-50°) and full hip extension.
*   **Push-Up Analyzer**: Monitors elbow angle (90°), shoulder position (45°), and hip sag.

### 📊 Professional-Grade Feedback
*   **Visual Overlays**: See your skeleton, joint angles, and error flags directly on the video.
*   **Actionable Corrections**: "Sit back deeper," "Don't round your back," "Engage core."
*   **Privacy First**: All processing happens locally on your machine.

### 🎨 Immersive Experience
*   **Kinetic Interface**: Smooth `framer-motion` animations.
*   **Dark Mode Aesthetic**: A premium Neon Green/Pink design system.

---

## 🛠️ System Architecture

For a deep dive into how the Front-End, Back-End, and Computer Vision pipeline interact, read our detailed **[System Architecture Documentation](system_architecture.md)**.

**Tech Stack:**
*   **Frontend**: React, Vite, Framer Motion
*   **Backend**: Python, FastAPI, Uvicorn
*   **AI Engine**: MediaPipe, OpenCV, MoviePy

---

## 📦 Installation & Quick Start

You will need **two terminal windows** to run the full application.

### Terminal 1: Frontend (The Interface)
```bash
cd client
npm install
npm run dev
```
👉 **Open Browser:** `http://localhost:5173`

### Terminal 2: Backend (The AI Engine)
```bash
cd server  # Important: Run from inside /server directory
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
👉 **API Status:** `http://localhost:8000`

---

## 📂 Project Structure

```bash
VISION-47-PoseCorrect/
├── client/                 # React Application
│   └── src/                # UI Components & Pages
├── server/                 # Python Backend
│   ├── main.py             # API Entry Point
│   ├── core/               # AI Analyzers (Squat, Deadlift, Pushup)
│   ├── uploads/            # Temporary storage for inputs
│   ├── outputs/            # Processed videos
│   └── requirements.txt    # Python dependencies
└── system_architecture.md  # Detailed Technical Docs
```

---

## 🎮 How to Use

1.  **Start Both Servers** (see above).
2.  Go to the **Dashboard** in the web app.
3.  Select **"Video Analysis"**.
4.  Choose your exercise (e.g., Squat).
5.  Drag & Drop your video file.
6.  **Watch the magic:** The AI will process your video and return a highlighted version with a detailed report card.

---

## 👥 Meet the Team

Built by students from **RV College of Engineering, Bangalore**.

- **Arya Wadhwa**
- **Dilraj Singh**
- **Shlokk Sikka**
- **Anirudh M**
- **Ashwin Acharya**

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
*Built with ❤️ by the Gymbro Team*
