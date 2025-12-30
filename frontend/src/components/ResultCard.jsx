import React from 'react';

const ResultCard = ({ result }) => {
    if (!result) return null;

    const { predicted_risk, exposure_score, key_factors } = result;

    // Determine implementation classes based on risk
    const riskClass =
        predicted_risk === 'HIGH' ? 'risk-high' :
            predicted_risk === 'MEDIUM' ? 'risk-medium' :
                'risk-low';

    const scorePercentage = Math.round(exposure_score * 100);

    // Dynamic color for progress bar
    const barColor =
        predicted_risk === 'HIGH' ? '#ef4444' :
            predicted_risk === 'MEDIUM' ? '#f59e0b' :
                '#10b981';

    return (
        <div className="result-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Risk Assessment</h2>
                <span className={`risk-badge ${riskClass}`}>{predicted_risk} RISK</span>
            </div>

            <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#94a3b8' }}>
                    <span>Exposure Score</span>
                    <span>{scorePercentage}/100</span>
                </div>
                <div className="score-bar">
                    <div
                        className="score-fill"
                        style={{ width: `${scorePercentage}%`, backgroundColor: barColor }}
                    />
                </div>
            </div>

            {key_factors && key_factors.length > 0 && (
                <div className="key-factors">
                    <h3>Contributing Factors:</h3>
                    <ul>
                        {key_factors.map((factor, index) => (
                            <li key={index}>{factor}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default ResultCard;
