import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const IntroAnimation = ({ onComplete }) => {
    const [started, setStarted] = useState(false);
    const [step, setStep] = useState(0);
    const audioRef = useRef(null);

    // Configuration
    const START_TIME = 0;
    const DURATION = 3;

    useEffect(() => {
        if (!started) return;

        const timer = setTimeout(() => {
            if (step < 3) {
                setStep(step + 1);
            }
        }, 1500);
        return () => clearTimeout(timer);
    }, [started, step]);

    const handleStart = async () => {
        setStarted(true);

        try {
            audioRef.current = new Audio('/intro.mp3');
            audioRef.current.volume = 0.5;
            audioRef.current.currentTime = START_TIME;

            await audioRef.current.play();

            if (DURATION) {
                setTimeout(() => {
                    if (audioRef.current) {
                        const fadeOut = setInterval(() => {
                            if (audioRef.current.volume > 0.05) {
                                audioRef.current.volume -= 0.05;
                            } else {
                                audioRef.current.pause();
                                clearInterval(fadeOut);
                            }
                        }, 50);
                    }
                }, DURATION * 1000);
            }
        } catch (err) {
            console.error("Audio playback failed:", err);
        }
    };

    const variants = {
        initial: { scale: 0.8, opacity: 0 },
        animate: { scale: 1, opacity: 1, transition: { duration: 0.5, ease: "circOut" } },
        exit: { scale: 1.5, opacity: 0, filter: "blur(10px)", transition: { duration: 0.5 } }
    };

    const bgColors = [
        'var(--color-black)',      // Step 0: YOUR
        'var(--color-neon-pink)',  // Step 1: FITNESS
        'var(--color-neon-green)', // Step 2: REIMAGINED
        'var(--color-neon-purple)' // Step 3: READY?
    ];

    if (!started) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="intro-container"
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    backgroundColor: 'var(--color-black)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 9999,
                    cursor: 'pointer'
                }}
                onClick={handleStart}
            >
                <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                    style={{ textAlign: 'center' }}
                >
                    <h1 style={{ fontSize: '2rem', color: 'var(--color-white)', marginBottom: '1rem', letterSpacing: '0.2em' }}>GYMBRO</h1>
                    <p style={{ color: '#888', fontSize: '1rem' }}>CLICK TO START</p>
                </motion.div>
            </motion.div>
        );
    }

    return (
        <motion.div
            className="intro-container"
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                backgroundColor: bgColors[step] || 'var(--color-black)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 9999,
                cursor: step >= 3 ? 'pointer' : 'default'
            }}
            onClick={() => step >= 3 && onComplete()}
        >
            <AnimatePresence mode="wait">
                {step === 0 && (
                    <motion.h1 key="step1" variants={variants} initial="initial" animate="animate" exit="exit" style={{ fontSize: '5rem', color: 'var(--color-white)' }}>
                        YOUR
                    </motion.h1>
                )}
                {step === 1 && (
                    <motion.h1 key="step2" variants={variants} initial="initial" animate="animate" exit="exit" style={{ fontSize: '5rem', color: 'var(--color-black)' }}>
                        FITNESS
                    </motion.h1>
                )}
                {step === 2 && (
                    <motion.h1 key="step3" variants={variants} initial="initial" animate="animate" exit="exit" style={{ fontSize: '5rem', color: 'var(--color-black)' }}>
                        REIMAGINED
                    </motion.h1>
                )}
                {step === 3 && (
                    <motion.div key="step4" variants={variants} initial="initial" animate="animate" style={{ textAlign: 'center' }}>
                        <h1 style={{ fontSize: '4rem', color: 'var(--color-white)', marginBottom: '2rem' }}>READY?</h1>
                        <p style={{ fontFamily: 'var(--font-primary)', fontSize: '1.2rem' }}>Click to enter</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default IntroAnimation;
