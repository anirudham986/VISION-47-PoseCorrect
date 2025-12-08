import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();

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
