import React from 'react';
import { motion } from 'framer-motion';

const LoadingScreen = ({ onComplete }) => {
    return (
        <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.5 } }}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                backgroundColor: '#000',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 10000,
            }}
        >
            <motion.div
                animate={{
                    scale: [1, 1.1, 1],
                    opacity: [0.5, 1, 0.5],
                }}
                transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '1rem'
                }}
            >
                <h1 style={{
                    color: '#fff',
                    fontSize: '3rem',
                    fontWeight: '900',
                    letterSpacing: '0.2em',
                    margin: 0,
                    fontStyle: 'italic'
                }}>
                    GYMBRO
                </h1>
                <div style={{
                    width: '50px',
                    height: '2px',
                    backgroundColor: 'var(--color-neon-green, #0f0)',
                    borderRadius: '1px'
                }} />
            </motion.div>
        </motion.div>
    );
};

export default LoadingScreen;
