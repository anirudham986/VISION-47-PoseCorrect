import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Upload, FileVideo, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const VideoAnalysis = () => {
    const navigate = useNavigate();
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type.startsWith('video/')) {
            setFile(droppedFile);
            simulateAnalysis();
        }
    };

    const simulateAnalysis = () => {
        setAnalyzing(true);
        setTimeout(() => {
            setAnalyzing(false);
        }, 3000);
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-black)', padding: '2rem' }}>
            <button
                onClick={() => navigate('/dashboard')}
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#888',
                    fontSize: '1rem',
                    marginBottom: '2rem'
                }}
            >
                <ArrowLeft size={20} /> Back to Dashboard
            </button>

            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>UPLOAD <span style={{ color: 'var(--color-neon-pink)' }}>VIDEO</span></h1>
                <p style={{ color: '#aaa', marginBottom: '3rem' }}>Get a detailed breakdown of your form from professional AI analysis.</p>

                {!file && (
                    <motion.div
                        animate={{
                            borderColor: isDragging ? 'var(--color-neon-pink)' : '#333',
                            backgroundColor: isDragging ? 'rgba(255, 0, 153, 0.1)' : 'var(--color-dark-gray)'
                        }}
                        style={{
                            border: '2px dashed #333',
                            borderRadius: '2rem',
                            padding: '6rem 2rem',
                            textAlign: 'center',
                            cursor: 'pointer'
                        }}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <Upload size={64} color={isDragging ? 'var(--color-neon-pink)' : '#555'} style={{ marginBottom: '2rem' }} />
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Drag & Drop your video here</h3>
                        <p style={{ color: '#666' }}>or click to browse files</p>
                    </motion.div>
                )}

                {file && analyzing && (
                    <div style={{ textAlign: 'center', padding: '4rem' }}>
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                            style={{
                                width: '64px',
                                height: '64px',
                                border: '4px solid #333',
                                borderTopColor: 'var(--color-neon-pink)',
                                borderRadius: '50%',
                                margin: '0 auto 2rem'
                            }}
                        />
                        <h3 style={{ fontSize: '1.5rem' }}>Analyzing Form...</h3>
                    </div>
                )}

                {file && !analyzing && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        style={{ backgroundColor: 'var(--color-dark-gray)', borderRadius: '2rem', padding: '2rem' }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                            <CheckCircle size={32} color="var(--color-neon-green)" />
                            <div>
                                <h3 style={{ fontSize: '1.2rem' }}>Analysis Complete</h3>
                                <p style={{ color: '#888' }}>{file.name}</p>
                            </div>
                        </div>

                        <div style={{ backgroundColor: '#000', borderRadius: '1rem', padding: '2rem', marginBottom: '2rem' }}>
                            <h4 style={{ color: '#aaa', marginBottom: '1rem' }}>KEY INSIGHTS</h4>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                <li style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Spine Alignment</span>
                                    <span style={{ color: 'var(--color-neon-green)' }}>95% Perfect</span>
                                </li>
                                <li style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Knee Position</span>
                                    <span style={{ color: 'var(--color-neon-pink)' }}>Needs Improvement</span>
                                </li>
                            </ul>
                        </div>

                        <button
                            onClick={() => setFile(null)}
                            style={{
                                width: '100%',
                                padding: '1rem',
                                backgroundColor: '#333',
                                color: '#fff',
                                borderRadius: '1rem',
                                fontWeight: 'bold'
                            }}
                        >
                            Analyze Another Video
                        </button>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default VideoAnalysis;
