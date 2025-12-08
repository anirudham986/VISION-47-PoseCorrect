# GYMBRO - AI Fitness Coach

**Your Personal Trainer, Reimagined.**

Gymbro is a next-generation fitness application that leverages AI to provide real-time form correction and professional video analysis. Designed with a high-energy "Spotify Wrapped" aesthetic, it makes professional coaching accessible to everyone, anywhere.

![Gymbro Demo](assets/demo.webp)

## 🚀 Features

### 🟢 Real-Time Coaching
Turn your webcam into a personal trainer.
- **Instant Feedback**: Get voice-guided corrections as you exercise (e.g., "Keep your back straight", "Lower your hips").
- **Live Metrics**: Track your reps and form quality in real-time.
- **Privacy First**: All processing happens locally on your device.

### 📹 Video Analysis (Python Engine)
Upload your workout videos for a deep dive using our advanced computer vision engine.
- **Frame-by-Frame Breakdown**: Analyze your technique against professional standards.
- **Detailed Insights**: Receive specific scores on spine alignment, joint angles, and stability.
- **Skeleton Overlay**: Visualize your biomechanics with a color-coded skeletal tracking system.

### 🎨 Immersive Experience
- **Kinetic Interface**: Smooth animations and transitions powered by `framer-motion`.
- **Vibrant Design**: A dark mode aesthetic with neon accents (Neon Green, Pink, Purple) to keep you motivated.
- **Interactive Dashboard**: Seamlessly switch between modes with a premium, app-like feel.

---

## 🛠️ Tech Stack

### Frontend (Web Application)
- **Framework**: React + Vite
- **Styling**: Vanilla CSS (Custom Design System with CSS Variables)
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router DOM

### AI & Computer Vision (Analysis Engine)
- **Language**: Python 3.9+
- **Vision**: OpenCV, MediaPipe
- **Data Processing**: NumPy, Pandas
- **Visualization**: Matplotlib

---

## 📂 Project Structure

```bash
VISION-47-PoseCorrect/
├── client/                 # Frontend React Application
│   ├── src/                # Source code (Components, Pages, Assets)
│   ├── public/             # Static assets
│   ├── index.html          # Entry point
│   └── vite.config.js      # Vite configuration
├── video_analyzer.py       # Standalone Python Video Analysis Script
├── requirements.txt        # Python dependencies
└── README.md               # Project Documentation
```

---

## 📦 Installation & Setup

### 1. Frontend Setup (Web App)
The web interface allows users to interact with the coaching features.

```bash
# Navigate to the client directory
cd client

# Install Node dependencies
npm install

# Start the development server
npm run dev
```
The app will open at `http://localhost:5173`.

### 2. Backend Setup (AI Analysis Tool)
To use the advanced video analysis script locally:

```bash
# Navigate to the root directory
cd ..

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## 🎮 Usage

### Running the Web App
1. Open the web app in your browser (`http://localhost:5173`).
2. Navigate to **"Real-Time Coach"** for webcam-based feedback.
3. Explore the **"Dashboard"** for your workout history.

### Running the Video Analyzer
Use the Python script to analyze existing video files with detailed skeletal tracking.

```bash
# Basic usage
python video_analyzer.py

# Or specify a video file directly
python video_analyzer.py path/to/your/video.mp4
```
**Controls:**
- `Q`: Quit analysis
- `P`: Pause/Resume
- `S`: Save screenshot

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
