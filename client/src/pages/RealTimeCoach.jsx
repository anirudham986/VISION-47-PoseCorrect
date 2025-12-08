import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Activity, Maximize2, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RealTimeCoach = () => {
    const navigate = useNavigate();

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--color-black)' }}>
            {/* Header */}
            <header style={{ padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #333' }}>
                <button onClick={() => navigate('/dashboard')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff' }}>
                    <ArrowLeft size={20} /> Exit Session
                </button>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-neon-green)', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-neon-green)', boxShadow: '0 0 10px var(--color-neon-green)' }}></div>
                        LIVE
                    </span>
                    <Settings size={20} color="#fff" />
                </div>
            </header>

            {/* Main Content */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Webcam Area */}
                <div style={{ flex: 3, position: 'relative', backgroundColor: '#000', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <p style={{ color: '#555' }}>[ Webcam Feed Placeholder ]</p>

                    {/* Overlay UI */}
                    <div style={{ position: 'absolute', bottom: '2rem', left: '2rem', right: '2rem', display: 'flex', justifyContent: 'space-between' }}>
                        <div style={{ backgroundColor: 'rgba(0,0,0,0.7)', padding: '1rem', borderRadius: '1rem', backdropFilter: 'blur(10px)' }}>
                            <h3 style={{ fontSize: '1rem', color: '#aaa', marginBottom: '0.5rem' }}>CURRENT EXERCISE</h3>
                            <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>SQUATS</p>
                        </div>
                        <div style={{ backgroundColor: 'rgba(0,0,0,0.7)', padding: '1rem', borderRadius: '1rem', backdropFilter: 'blur(10px)' }}>
                            <h3 style={{ fontSize: '1rem', color: '#aaa', marginBottom: '0.5rem' }}>REPS</h3>
                            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--color-neon-green)' }}>12</p>
                        </div>
                    </div>
                </div>

                {/* Sidebar */}
                <div style={{ flex: 1, backgroundColor: 'var(--color-dark-gray)', borderLeft: '1px solid #333', padding: '2rem', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Activity size={20} color="var(--color-neon-pink)" /> ANALYSIS
                    </h3>

                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        <motion.div
                            initial={{ x: 20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(255, 0, 153, 0.1)', borderLeft: '4px solid var(--color-neon-pink)', borderRadius: '0.5rem' }}
                        >
                            <p style={{ fontSize: '0.9rem', color: 'var(--color-neon-pink)', fontWeight: 'bold', marginBottom: '0.5rem' }}>CORRECTION</p>
                            <p>Keep your back straight. You're leaning too far forward.</p>
                        </motion.div>

                        <motion.div
                            initial={{ x: 20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(204, 255, 0, 0.1)', borderLeft: '4px solid var(--color-neon-green)', borderRadius: '0.5rem' }}
                        >
                            <p style={{ fontSize: '0.9rem', color: 'var(--color-neon-green)', fontWeight: 'bold', marginBottom: '0.5rem' }}>GOOD JOB</p>
                            <p>Great depth on that last rep!</p>
                        </motion.div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RealTimeCoach;
