import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();

    return (
        <nav style={{ padding: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--color-black)', color: 'var(--color-white)' }}>
            <Link to="/" style={{ textDecoration: 'none' }}>
                <h2 style={{ fontSize: '1.5rem', color: 'var(--color-neon-green)', margin: 0 }}>GYMBRO</h2>
            </Link>
            <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                <Link to="/about" style={{ color: 'var(--color-white)', textDecoration: 'none', fontSize: '1rem' }}>About Us</Link>
                <Link to="/contact" style={{ color: 'var(--color-white)', textDecoration: 'none', fontSize: '1rem' }}>Contact Us</Link>
                <button
                    onClick={() => navigate('/dashboard')}
                    style={{
                        padding: '0.8rem 1.5rem',
                        backgroundColor: 'var(--color-white)',
                        color: 'var(--color-black)',
                        borderRadius: '2rem',
                        fontWeight: 'bold',
                        fontSize: '1rem',
                        border: 'none',
                        cursor: 'pointer'
                    }}
                >
                    Launch App
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
