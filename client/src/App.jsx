import { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Volume2, VolumeX } from 'lucide-react';
import IntroAnimation from './components/IntroAnimation';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import RealTimeCoach from './pages/RealTimeCoach';
import VideoAnalysis from './pages/VideoAnalysis';
import About from './pages/About';
import Contact from './pages/Contact';
import Navbar from './components/Navbar';

const AppContent = () => {
  const [showIntro, setShowIntro] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    audioRef.current = new Audio('/intro.mp3');
    audioRef.current.volume = 0.2; // Low background volume
    audioRef.current.loop = true;

    const playAudio = async () => {
      try {
        await audioRef.current.play();
      } catch (err) {
        console.log("Autoplay prevented");
      }
    };

    playAudio();

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleIntroComplete = () => {
    setShowIntro(false);
  };

  const handleStart = () => {
    navigate('/dashboard');
  };

  return (
    <>
      {showIntro && <IntroAnimation onComplete={handleIntroComplete} />}
      {!showIntro && (
        <Routes>
          <Route path="/" element={<><Navbar /><LandingPage onStart={handleStart} /></>} />
          <Route path="/about" element={<><Navbar /><About /></>} />
          <Route path="/contact" element={<><Navbar /><Contact /></>} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/coach" element={<RealTimeCoach />} />
          <Route path="/upload" element={<VideoAnalysis />} />
        </Routes>
      )}

      {/* Global Audio Control */}
      <button
        onClick={toggleMute}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 9999,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          border: '1px solid #333',
          borderRadius: '50%',
          width: '50px',
          height: '50px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: 'var(--color-neon-green, #0f0)',
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        {isMuted ? <VolumeX size={24} /> : <Volume2 size={24} />}
      </button>
    </>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
