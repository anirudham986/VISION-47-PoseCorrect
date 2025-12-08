import React from 'react';
import { motion } from 'framer-motion';
import { Linkedin } from 'lucide-react';

const teamMembers = [
    { name: 'Arya Wadhwa', role: 'Student', linkedin: 'https://www.linkedin.com/' },
    { name: 'Dilraj Singh', role: 'Student', linkedin: 'https://www.linkedin.com/' },
    { name: 'Shlokk Sikka', role: 'Student', linkedin: 'https://www.linkedin.com/' },
    { name: 'Anirudh M', role: 'Student', linkedin: 'https://www.linkedin.com/' },
    { name: 'Ashwin Acharya', role: 'Student', linkedin: 'https://www.linkedin.com/' },
];

const About = () => {
    return (
        <div className="page-container" style={{ padding: '4rem 2rem', minHeight: '100vh', backgroundColor: 'var(--color-black)', color: 'var(--color-white)' }}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="content-wrapper"
                style={{ maxWidth: '1200px', margin: '0 auto' }}
            >
                <h1 style={{ fontSize: '3rem', marginBottom: '1rem', color: 'var(--color-neon-green)' }}>About Us</h1>
                <p className="subtitle" style={{ fontSize: '1.2rem', color: '#aaa', marginBottom: '3rem' }}>
                    We are students from <span style={{ color: 'var(--color-white)', fontWeight: 'bold' }}>RV College of Engineering, Bangalore</span>.
                </p>

                <div className="team-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
                    {teamMembers.map((member, index) => (
                        <motion.a
                            key={index}
                            href={member.linkedin}
                            target="_blank"
                            rel="noopener noreferrer"
                            whileHover={{ y: -10, backgroundColor: '#1a1a1a' }}
                            style={{
                                textDecoration: 'none',
                                color: 'inherit',
                                backgroundColor: 'var(--color-dark-gray)',
                                padding: '2rem',
                                borderRadius: '1rem',
                                border: '1px solid #333',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                textAlign: 'center',
                                cursor: 'pointer',
                                transition: 'border-color 0.3s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--color-neon-purple)'}
                            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#333'}
                        >
                            <div style={{
                                width: '100px',
                                height: '100px',
                                borderRadius: '50%',
                                backgroundColor: '#333',
                                marginBottom: '1.5rem',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                <Linkedin size={40} color="var(--color-neon-purple)" />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{member.name}</h3>
                            <p style={{ color: '#888' }}>{member.role}</p>
                        </motion.a>
                    ))}
                </div>
            </motion.div>
        </div>
    );
};

export default About;
