import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import IntroAnimation from './components/IntroAnimation';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import RealTimeCoach from './pages/RealTimeCoach';
import VideoAnalysis from './pages/VideoAnalysis';

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
          <Route path="/" element={<LandingPage onStart={handleStart} />} />
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
