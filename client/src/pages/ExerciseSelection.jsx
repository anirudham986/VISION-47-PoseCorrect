import React, { useState } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { Dumbbell, TrendingUp, Target, ChevronLeft, ChevronRight } from 'lucide-react';

const exercises = [
    {
        id: 'pushup',
        name: 'PUSH UP',
        targetMuscles: ['Chest', 'Triceps', 'Shoulders'],
        gradient: 'linear-gradient(135deg, #ccff00 0%, #99cc00 100%)',
        accentColor: '#ccff00',
        shadowColor: 'rgba(204, 255, 0, 0.4)',
        icon: '💪',
        description: 'Upper body strength foundation'
    },
    {
        id: 'pullup',
        name: 'PULL UP',
        targetMuscles: ['Back', 'Biceps', 'Lats'],
        gradient: 'linear-gradient(135deg, #9900ff 0%, #6600cc 100%)',
        accentColor: '#9900ff',
        shadowColor: 'rgba(153, 0, 255, 0.4)',
        icon: '🔥',
        description: 'Complete back development'
    },
    {
        id: 'benchpress',
        name: 'BENCH PRESS',
        targetMuscles: ['Chest', 'Triceps', 'Shoulders'],
        gradient: 'linear-gradient(135deg, #ff0099 0%, #cc0077 100%)',
        accentColor: '#ff0099',
        shadowColor: 'rgba(255, 0, 153, 0.4)',
        icon: '🏋️',
        description: 'Compound pushing power'
    },
    {
        id: 'squat',
        name: 'SQUAT',
        targetMuscles: ['Quads', 'Glutes', 'Hamstrings'],
        gradient: 'linear-gradient(135deg, #00ffcc 0%, #00cc99 100%)',
        accentColor: '#00ffcc',
        shadowColor: 'rgba(0, 255, 204, 0.4)',
        icon: '⚡',
        description: 'Lower body foundation'
    },
    {
        id: 'deadlift',
        name: 'DEADLIFT',
        targetMuscles: ['Back', 'Glutes', 'Hamstrings'],
        gradient: 'linear-gradient(135deg, #ff6600 0%, #cc5200 100%)',
        accentColor: '#ff6600',
        shadowColor: 'rgba(255, 102, 0, 0.4)',
        icon: '🎯',
        description: 'Full body strength builder'
    }
];

const ExerciseCard = ({ exercise, index, activeIndex, onSelect, onDismiss }) => {
    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const rotateZ = useTransform(x, [-200, 200], [-15, 15]);
    const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

    const isActive = index === activeIndex;
    const offset = index - activeIndex;

    const handleDragEnd = (event, info) => {
        const swipeThreshold = 100;

        if (Math.abs(info.offset.x) > swipeThreshold) {
            if (info.offset.x > 0) {
                onSelect(exercise);
            } else {
                onDismiss();
            }
        }
    };

    return (
        <motion.div
            drag={isActive ? "x" : false}
            dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
            style={{
                x: isActive ? x : 0,
                y: isActive ? y : 0,
                rotateZ: isActive ? rotateZ : 0,
                opacity,
                position: 'absolute',
                width: '100%',
                maxWidth: '400px',
                height: '550px',
                cursor: isActive ? 'grab' : 'default',
                zIndex: exercises.length - index,
            }}
            initial={false}
            animate={{
                scale: isActive ? 1 : 1 - offset * 0.05,
                y: offset * 20,
                opacity: offset > 2 ? 0 : 1,
            }}
            whileHover={isActive ? { scale: 1.02 } : {}}
            transition={{
                type: "spring",
                stiffness: 300,
                damping: 30,
            }}
        >
            <motion.div
                onClick={() => isActive && onSelect(exercise)}
                whileTap={isActive ? { scale: 0.98 } : {}}
                style={{
                    width: '100%',
                    height: '100%',
                    background: exercise.gradient,
                    borderRadius: '2rem',
                    padding: '3rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: `0 10px 30px ${exercise.shadowColor}`,
                    border: '2px solid rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    position: 'relative',
                    overflow: 'hidden',
                }}
            >
                {/* Background Pattern */}
                <div style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    fontSize: '15rem',
                    opacity: 0.1,
                    lineHeight: 1,
                    userSelect: 'none',
                }}>
                    {exercise.icon}
                </div>

                {/* Header */}
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: index * 0.1, type: "spring" }}
                        style={{
                            fontSize: '4rem',
                            marginBottom: '1rem',
                        }}
                    >
                        {exercise.icon}
                    </motion.div>

                    <h2 style={{
                        fontSize: '2.5rem',
                        fontWeight: '900',
                        color: '#000',
                        marginBottom: '0.5rem',
                        letterSpacing: '0.02em',
                    }}>
                        {exercise.name}
                    </h2>

                    <p style={{
                        fontSize: '1.1rem',
                        color: 'rgba(0, 0, 0, 0.7)',
                        fontWeight: '500',
                    }}>
                        {exercise.description}
                    </p>
                </div>

                {/* Middle Section */}
                <div style={{ position: 'relative', zIndex: 1 }}>


                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {exercise.targetMuscles.map((muscle, idx) => (
                            <motion.span
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 + idx * 0.1 }}
                                style={{
                                    padding: '0.4rem 0.8rem',
                                    backgroundColor: 'rgba(0, 0, 0, 0.15)',
                                    borderRadius: '1rem',
                                    fontSize: '0.85rem',
                                    color: '#000',
                                    fontWeight: '600',
                                    border: '1px solid rgba(0, 0, 0, 0.1)',
                                }}
                            >
                                {muscle}
                            </motion.span>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <motion.div
                        whileHover={{ x: 10 }}
                        style={{
                            fontSize: '1.2rem',
                            fontWeight: 'bold',
                            color: '#000',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                        }}
                    >
                        {isActive ? (
                            <>
                                <span>SWIPE RIGHT TO SELECT</span>
                                <span style={{ fontSize: '1.5rem' }}>→</span>
                            </>
                        ) : (
                            <span>TAP TO SELECT</span>
                        )}
                    </motion.div>
                </div>

                {/* Animated Glow Effect */}
                <motion.div
                    style={{
                        position: 'absolute',
                        top: '-50%',
                        left: '-50%',
                        width: '200%',
                        height: '200%',
                        background: `radial-gradient(circle, ${exercise.shadowColor} 0%, transparent 70%)`,
                        pointerEvents: 'none',
                        opacity: 0.1,
                    }}
                />
            </motion.div>
        </motion.div>
    );
};

const ExerciseSelection = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [activeIndex, setActiveIndex] = useState(0);
    const [selectedExercise, setSelectedExercise] = useState(null);

    // Get mode from location state (coach or upload)
    const mode = location.state?.mode || 'coach';

    const handleSelect = (exercise) => {
        setSelectedExercise(exercise);
        // Navigate to the appropriate page based on mode
        const targetPath = mode === 'upload' ? '/upload' : '/coach';
        setTimeout(() => {
            navigate(targetPath, { state: { selectedExercise: exercise.id } });
        }, 500);
    };

    const handleDismiss = () => {
        if (activeIndex < exercises.length - 1) {
            setActiveIndex(activeIndex + 1);
        }
    };

    const currentExercise = exercises[activeIndex];

    return (
        <div style={{
            minHeight: '100vh',
            backgroundColor: 'var(--color-black)',
            color: 'var(--color-white)',
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            overflow: 'hidden',
        }}>
            {/* Animated Background */}
            <motion.div
                animate={{
                    background: [
                        'radial-gradient(circle at 20% 50%, rgba(204, 255, 0, 0.1) 0%, transparent 50%)',
                        'radial-gradient(circle at 80% 50%, rgba(255, 0, 153, 0.1) 0%, transparent 50%)',
                        'radial-gradient(circle at 50% 80%, rgba(153, 0, 255, 0.1) 0%, transparent 50%)',
                        'radial-gradient(circle at 20% 50%, rgba(204, 255, 0, 0.1) 0%, transparent 50%)',
                    ],
                }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "linear",
                }}
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    pointerEvents: 'none',
                }}
            />

            <div style={{ position: 'relative', zIndex: 10, marginBottom: '2rem' }}>
                <button
                    onClick={() => navigate('/dashboard')}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: '#888',
                        fontSize: '1rem',
                        marginBottom: '2rem',
                    }}
                >
                    <ChevronLeft size={20} /> Back
                </button>

                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ textAlign: 'center' }}
                >
                    <h1 style={{
                        fontSize: 'clamp(2rem, 5vw, 3.5rem)',
                        marginBottom: '0.5rem',
                        fontWeight: '900',
                    }}>
                        CHOOSE YOUR
                        <span style={{ color: currentExercise?.accentColor }}> EXERCISE</span>
                    </h1>
                    <p style={{ color: '#888', fontSize: '1.1rem' }}>
                        Swipe right to select • {activeIndex + 1} of {exercises.length}
                    </p>
                </motion.div>
            </div>

            {/* Card Stack */}
            <div style={{
                flex: 1,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                position: 'relative',
                minHeight: '550px',
                gap: '2rem',
            }}>
                {/* Left Arrow */}
                {activeIndex > 0 && (
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => setActiveIndex(activeIndex - 1)}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        style={{
                            width: '60px',
                            height: '60px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            border: '2px solid rgba(255, 255, 255, 0.2)',
                            backdropFilter: 'blur(10px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                        }}
                    >
                        <ChevronLeft size={32} color="#fff" />
                    </motion.button>
                )}

                <div style={{
                    position: 'relative',
                    width: '100%',
                    maxWidth: '400px',
                    height: '550px',
                }}>
                    <AnimatePresence>
                        {exercises.map((exercise, index) => (
                            <ExerciseCard
                                key={exercise.id}
                                exercise={exercise}
                                index={index}
                                activeIndex={activeIndex}
                                onSelect={handleSelect}
                                onDismiss={handleDismiss}
                            />
                        ))}
                    </AnimatePresence>
                </div>

                {/* Right Arrow */}
                {activeIndex < exercises.length - 1 && (
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={handleDismiss}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        style={{
                            width: '60px',
                            height: '60px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            border: '2px solid rgba(255, 255, 255, 0.2)',
                            backdropFilter: 'blur(10px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                        }}
                    >
                        <ChevronRight size={32} color="#fff" />
                    </motion.button>
                )}
            </div>

            {/* Progress Indicators */}
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '0.5rem',
                position: 'relative',
                zIndex: 10,
                marginTop: '2rem',
            }}>
                {exercises.map((exercise, index) => (
                    <motion.div
                        key={exercise.id}
                        initial={{ scale: 0 }}
                        animate={{
                            scale: 1,
                            backgroundColor: index === activeIndex ? exercise.accentColor : '#333',
                            width: index === activeIndex ? '2.5rem' : '0.5rem',
                        }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        style={{
                            height: '0.5rem',
                            borderRadius: '1rem',
                        }}
                    />
                ))}
            </div>

            {/* Instructions */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                style={{
                    textAlign: 'center',
                    marginTop: '2rem',
                    color: '#666',
                    fontSize: '0.9rem',
                    position: 'relative',
                    zIndex: 10,
                }}
            >
                💡 Tip: Swipe left to skip • Tap or swipe right to begin
            </motion.div>
        </div>
    );
};

export default ExerciseSelection;
