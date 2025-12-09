import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                <h2>GYMBRO</h2>
            </Link>
            <div className="navbar-links">
                <Link to="/about" className="nav-link">About Us</Link>
                <Link to="/contact" className="nav-link">Contact Us</Link>
                <Link to="/privacy" className="nav-link">Privacy</Link>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="btn-launch"
                >
                    Launch App
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
