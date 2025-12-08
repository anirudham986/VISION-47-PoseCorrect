import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const IntroAnimation = ({ onComplete }) => {
    const [step, setStep] = useState(0);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (step < 3) {
                setStep(step + 1);
            } else {
                // Allow user to click to enter after animation sequence
            }
        }, 1500);
        return () => clearTimeout(timer);
    }, [step]);

    const variants = {
        initial: { scale: 0.8, opacity: 0 },
        animate: { scale: 1, opacity: 1, transition: { duration: 0.5, ease: "circOut" } },
        exit: { scale: 1.5, opacity: 0, filter: "blur(10px)", transition: { duration: 0.5 } }
    };

    const bgColors = [
        'var(--color-black)',
        'var(--color-neon-pink)',
        'var(--color-neon-green)',
        'var(--color-neon-purple)'
    ];

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
                        <p style={{ fontFamily: 'var(--font-primary)', fontSize: '1.2rem' }}>Click to start</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default IntroAnimation;
