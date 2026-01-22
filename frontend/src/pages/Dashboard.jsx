import React from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();

    return (
        <div className="container">
            <div className="glass-card" style={{ maxWidth: '800px', textAlign: 'center' }}>
                <h1 style={{ marginBottom: '2rem' }}>Constructive Chemical Process</h1>
                <h2 style={{ color: 'var(--text-secondary)', marginBottom: '3rem', fontSize: '1.2rem' }}>Select Prediction Mode</h2>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>

                    {/* Mode 1: Without Test */}
                    <div
                        className="mode-card"
                        onClick={() => navigate('/predict')}
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            padding: '2rem',
                            borderRadius: '16px',
                            cursor: 'pointer',
                            border: '1px solid rgba(255,255,255,0.1)',
                            transition: 'transform 0.2s'
                        }}
                    >
                        <h3 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>Standard Mode</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                            Predict PPD exposure risk using questionnaire data only.
                        </p>
                        <div style={{ fontSize: '0.9rem', background: 'rgba(129, 140, 248, 0.2)', padding: '0.5rem', borderRadius: '8px', color: '#c7d2fe' }}>
                            No Lab Test Required
                        </div>
                    </div>

                    {/* Mode 2: With Creatinine */}
                    <div
                        className="mode-card"
                        onClick={() => navigate('/predict-with-creatinine')}
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            padding: '2rem',
                            borderRadius: '16px',
                            cursor: 'pointer',
                            border: '1px solid rgba(255,255,255,0.1)',
                            transition: 'transform 0.2s'
                        }}
                    >
                        <h3 style={{ color: '#34d399', marginBottom: '1rem' }}>Advanced Mode</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                            Refine prediction using Urine Creatinine value.
                        </p>
                        <div style={{ fontSize: '0.9rem', background: 'rgba(52, 211, 153, 0.2)', padding: '0.5rem', borderRadius: '8px', color: '#a7f3d0' }}>
                            Requires Lab Data
                        </div>
                    </div>

                </div>

                <div style={{ marginTop: '3rem' }}>
                    <button
                        onClick={() => navigate('/')}
                        style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', width: 'auto', padding: '0.5rem 2rem' }}
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
