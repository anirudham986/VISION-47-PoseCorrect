import React from 'react';
import { motion } from 'framer-motion';

const About = () => {
    return (
        <div className="page-container">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="content-wrapper"
            >
                <h1>About Us</h1>
                <p className="subtitle">Meet the team behind Gymbro.</p>

                <div className="team-grid">
                    {/* Placeholder for team members */}
                    <div className="team-member">
                        <div className="member-image-placeholder"></div>
                        <h3>Team Member Name</h3>
                        <p>Role</p>
                    </div>
                    <div className="team-member">
                        <div className="member-image-placeholder"></div>
                        <h3>Team Member Name</h3>
                        <p>Role</p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default About;
