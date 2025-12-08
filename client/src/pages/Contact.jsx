import React from 'react';
import { motion } from 'framer-motion';

const Contact = () => {
    const inputStyle = {
        width: '100%',
        padding: '1rem',
        backgroundColor: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '0.5rem',
        color: 'var(--color-white)',
        fontSize: '1rem',
        outline: 'none',
        transition: 'border-color 0.3s'
    };

    const focusStyle = (e) => {
        e.target.style.borderColor = 'var(--color-neon-pink)';
    };

    const blurStyle = (e) => {
        e.target.style.borderColor = '#333';
    };

    return (
        <div className="page-container" style={{ padding: '4rem 2rem', minHeight: '100vh', backgroundColor: 'var(--color-black)', color: 'var(--color-white)' }}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="content-wrapper"
                style={{ maxWidth: '800px', margin: '0 auto' }}
            >
                <h1 style={{ fontSize: '3rem', marginBottom: '1rem', color: 'var(--color-neon-pink)' }}>Get in Touch</h1>
                <p className="subtitle" style={{ fontSize: '1.2rem', color: '#aaa', marginBottom: '3rem' }}>
                    Have questions or feedback? We'd love to hear from you.
                </p>

                <div className="contact-form-container" style={{ backgroundColor: 'var(--color-dark-gray)', padding: '3rem', borderRadius: '2rem', border: '1px solid #333' }}>
                    <form className="contact-form" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <div className="form-group">
                            <label htmlFor="name" style={{ display: 'block', marginBottom: '0.5rem', color: '#ccc' }}>Name</label>
                            <input
                                type="text"
                                id="name"
                                placeholder="Your Name"
                                style={inputStyle}
                                onFocus={focusStyle}
                                onBlur={blurStyle}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', color: '#ccc' }}>Email</label>
                            <input
                                type="email"
                                id="email"
                                placeholder="Your Email"
                                style={inputStyle}
                                onFocus={focusStyle}
                                onBlur={blurStyle}
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="message" style={{ display: 'block', marginBottom: '0.5rem', color: '#ccc' }}>Message</label>
                            <textarea
                                id="message"
                                rows="5"
                                placeholder="Your Message"
                                style={{ ...inputStyle, resize: 'vertical' }}
                                onFocus={focusStyle}
                                onBlur={blurStyle}
                            ></textarea>
                        </div>
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            type="submit"
                            className="btn-primary"
                            style={{
                                padding: '1rem 2rem',
                                backgroundColor: 'var(--color-neon-pink)',
                                color: 'var(--color-black)',
                                border: 'none',
                                borderRadius: '2rem',
                                fontSize: '1.2rem',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                marginTop: '1rem'
                            }}
                        >
                            Send Message
                        </motion.button>
                    </form>
                </div>
            </motion.div>
        </div>
    );
};

export default Contact;
