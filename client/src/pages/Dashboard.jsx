import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Camera, Video, ArrowLeft } from 'lucide-react';

const Dashboard = () => {
    const navigate = useNavigate();

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.2 }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 }
    };

    return (
        <div style={{ minHeight: '100vh', padding: '2rem', backgroundColor: 'var(--color-black)', color: 'var(--color-white)' }}>
            <button
                onClick={() => navigate('/')}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#888',
                    fontSize: '1rem',
                    marginBottom: '2rem'
                }}
            >
                <ArrowLeft size={20} /> Back to Home
            </button>

            <motion.h1
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                style={{ fontSize: '3rem', marginBottom: '3rem' }}
            >
                CHOOSE YOUR <span style={{ color: 'var(--color-neon-green)' }}>MODE</span>
            </motion.h1>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                    gap: '2rem',
                    maxWidth: '1200px'
                }}
            >
                <motion.div
                    variants={itemVariants}
                    whileHover={{ scale: 1.02, backgroundColor: '#1a1a1a' }}
                    onClick={() => navigate('/coach')}
                    style={{
                        cursor: 'pointer',
                        padding: '4rem',
                        backgroundColor: 'var(--color-dark-gray)',
                        borderRadius: '2rem',
                        border: '2px solid transparent',
                        borderColor: 'var(--color-neon-purple)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        height: '400px'
                    }}
                >
                    <div>
                        <Camera size={64} color="var(--color-neon-purple)" style={{ marginBottom: '2rem' }} />
                        <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>REAL-TIME COACH</h2>
                        <p style={{ fontSize: '1.2rem', color: '#aaa' }}>
                            Instant form correction using your webcam.
                        </p>
                    </div>
                    <div style={{ alignSelf: 'flex-end', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--color-neon-purple)' }}>
                        START SESSION &rarr;
                    </div>
                </motion.div>

                <motion.div
                    variants={itemVariants}
                    whileHover={{ scale: 1.02, backgroundColor: '#1a1a1a' }}
                    onClick={() => navigate('/upload')}
                    style={{
                        cursor: 'pointer',
                        padding: '4rem',
                        backgroundColor: 'var(--color-dark-gray)',
                        borderRadius: '2rem',
                        border: '2px solid transparent',
                        borderColor: 'var(--color-neon-pink)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        height: '400px'
                    }}
                >
                    <div>
                        <Video size={64} color="var(--color-neon-pink)" style={{ marginBottom: '2rem' }} />
                        <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>VIDEO ANALYSIS</h2>
                        <p style={{ fontSize: '1.2rem', color: '#aaa' }}>
                            Upload and analyze your workout videos.
                        </p>
                    </div>
                    <div style={{ alignSelf: 'flex-end', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--color-neon-pink)' }}>
                        UPLOAD VIDEO &rarr;
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
};

export default Dashboard;
