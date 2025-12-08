import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Camera, Video, ArrowLeft } from 'lucide-react';

const exercises = [
    {
        id: 'pushup',
        name: 'PUSH UP',
        difficulty: 'Beginner',
        targetMuscles: ['Chest', 'Triceps', 'Shoulders'],
        gradient: 'linear-gradient(135deg, #ccff00 0%, #99cc00 100%)',
        accentColor: '#ccff00',
    },
    {
        id: 'pullup',
        name: 'PULL UP',
        difficulty: 'Advanced',
        targetMuscles: ['Back', 'Biceps', 'Lats'],
        gradient: 'linear-gradient(135deg, #9900ff 0%, #6600cc 100%)',
        accentColor: '#9900ff',
    },
    {
        id: 'benchpress',
        name: 'BENCH PRESS',
        difficulty: 'Intermediate',
        targetMuscles: ['Chest', 'Triceps', 'Shoulders'],
        gradient: 'linear-gradient(135deg, #ff0099 0%, #cc0077 100%)',
        accentColor: '#ff0099',
    },
    {
        id: 'squat',
        name: 'SQUAT',
        difficulty: 'Intermediate',
        targetMuscles: ['Quads', 'Glutes', 'Hamstrings'],
        gradient: 'linear-gradient(135deg, #00ffcc 0%, #00cc99 100%)',
        accentColor: '#00ffcc',
    },
    {
        id: 'deadlift',
        name: 'DEADLIFT',
        difficulty: 'Advanced',
        targetMuscles: ['Back', 'Glutes', 'Hamstrings'],
        gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)',
        accentColor: '#ff6600',
    }
];

const Dashboard = () => {
    const navigate = useNavigate();
    const [selectedExercise, setSelectedExercise] = useState(null);

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 }
    };

    const handleExerciseSelect = (exercise) => {
        setSelectedExercise(exercise);
    };

    const handleModeSelect = (mode) => {
        const targetPath = mode === 'upload' ? '/upload' : '/coach';
        navigate(targetPath, { state: { selectedExercise: selectedExercise.id } });
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

            {/* Exercise Selection Section */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginBottom: '4rem' }}
            >
                <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                    CHOOSE YOUR <span style={{ color: 'var(--color-neon-pink)' }}>EXERCISE</span>
                </h1>
                <p style={{ color: '#888', fontSize: '1.1rem', marginBottom: '2rem' }}>
                    Select an exercise to get started
                </p>

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '1.5rem',
                        maxWidth: '1400px',
                        marginBottom: '3rem'
                    }}
                >
                    {exercises.map((exercise) => (
                        <motion.div
                            key={exercise.id}
                            variants={itemVariants}
                            whileHover={{ scale: 1.05, y: -5 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleExerciseSelect(exercise)}
                            style={{
                                cursor: 'pointer',
                                background: exercise.gradient,
                                borderRadius: '1.5rem',
                                padding: '2rem',
                                position: 'relative',
                                overflow: 'hidden',
                                border: selectedExercise?.id === exercise.id
                                    ? `4px solid ${exercise.accentColor}`
                                    : '2px solid rgba(255, 255, 255, 0.1)',
                                boxShadow: selectedExercise?.id === exercise.id
                                    ? `0 0 30px ${exercise.accentColor}`
                                    : '0 4px 15px rgba(0, 0, 0, 0.3)',
                                transition: 'all 0.3s ease',
                            }}
                        >
                            {/* Content */}
                            <div style={{ position: 'relative', zIndex: 1 }}>
                                <h3 style={{
                                    fontSize: '1.5rem',
                                    fontWeight: '900',
                                    color: '#000',
                                    marginBottom: '0.5rem'
                                }}>
                                    {exercise.name}
                                </h3>
                                <div style={{
                                    display: 'inline-block',
                                    padding: '0.3rem 0.8rem',
                                    backgroundColor: 'rgba(0, 0, 0, 0.2)',
                                    borderRadius: '1rem',
                                    fontSize: '0.8rem',
                                    fontWeight: 'bold',
                                    color: '#000',
                                    marginBottom: '1rem'
                                }}>
                                    {exercise.difficulty}
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                                    {exercise.targetMuscles.map((muscle, idx) => (
                                        <span
                                            key={idx}
                                            style={{
                                                padding: '0.3rem 0.6rem',
                                                backgroundColor: 'rgba(0, 0, 0, 0.15)',
                                                borderRadius: '0.8rem',
                                                fontSize: '0.75rem',
                                                color: '#000',
                                                fontWeight: '600',
                                            }}
                                        >
                                            {muscle}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Selected Indicator */}
                            {selectedExercise?.id === exercise.id && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    style={{
                                        position: 'absolute',
                                        top: '1rem',
                                        right: '1rem',
                                        width: '30px',
                                        height: '30px',
                                        borderRadius: '50%',
                                        backgroundColor: '#000',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '1.2rem',
                                    }}
                                >
                                    ✓
                                </motion.div>
                            )}
                        </motion.div>
                    ))}
                </motion.div>
            </motion.div>

            {/* Mode Selection Section - Only shows after exercise is selected */}
            <AnimatePresence>
                {selectedExercise && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                    >
                        <motion.h1
                            style={{ fontSize: '3rem', marginBottom: '1rem' }}
                        >
                            {selectedExercise.name} - CHOOSE YOUR <span style={{ color: 'var(--color-neon-green)' }}>MODE</span>
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
                                onClick={() => handleModeSelect('coach')}
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
                                onClick={() => handleModeSelect('upload')}
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
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Dashboard;
