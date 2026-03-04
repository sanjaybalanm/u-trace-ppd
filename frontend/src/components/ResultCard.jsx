import React, { useMemo } from 'react';


const ResultCard = ({ result }) => {
    if (!result) return null;

    // Handle both standard and creatinine modes
    const isCreatinineMode = result.mode === 'WITH_CREATININE';
    const predicted_risk = result.predicted_risk || result.risk_level;
    const exposure_score = result.exposure_score;
    const normalized_ppd = result.normalized_ppd;
    const confidence = result.confidence;
    const factor_details = result.factor_details || [];
    const recommendations = result.health_recommendations || [];
    const creatinine_status = result.creatinine_status;
    const risk_description = result.risk_description;

    // Determine risk styling
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

    // Factor risk level colors
    const getFactorColor = (level) => {
        if (level === 'High') return '#ef4444';
        if (level === 'Medium') return '#f59e0b';
        return '#10b981';
    };



    return (
        <div className="result-card" style={{ maxWidth: '900px', margin: '2rem auto' }}>
            {/* Header Section */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                    <h2 style={{ margin: 0, fontSize: '1.5rem' }}>
                        {isCreatinineMode ? 'Advanced Risk Analysis (With Creatinine)' : 'Standard Risk Assessment'}
                    </h2>
                    {risk_description && (
                        <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            {risk_description}
                        </p>
                    )}
                </div>
                <span className={`risk-badge ${riskClass}`} style={{ fontSize: '1.1rem', padding: '0.75rem 1.5rem' }}>
                    {predicted_risk} RISK
                </span>
            </div>

            {/* Safety Status Banner */}
            <div style={{
                padding: '1.5rem',
                marginBottom: '2rem',
                borderRadius: '12px',
                textAlign: 'center',
                background: predicted_risk === 'LOW'
                    ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1))'
                    : predicted_risk === 'MEDIUM'
                        ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1))'
                        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))',
                border: `2px solid ${predicted_risk === 'LOW' ? '#10b981'
                    : predicted_risk === 'MEDIUM' ? '#f59e0b'
                        : '#ef4444'
                    }`,
                boxShadow: predicted_risk === 'LOW'
                    ? '0 4px 20px rgba(16, 185, 129, 0.3)'
                    : predicted_risk === 'MEDIUM'
                        ? '0 4px 20px rgba(245, 158, 11, 0.3)'
                        : '0 4px 20px rgba(239, 68, 68, 0.3)'
            }}>
                <div style={{
                    fontSize: '2.5rem',
                    fontWeight: 'bold',
                    marginBottom: '0.5rem',
                    color: predicted_risk === 'LOW' ? '#10b981'
                        : predicted_risk === 'MEDIUM' ? '#f59e0b'
                            : '#ef4444'
                }}>
                    {predicted_risk === 'LOW' ? '✓ YOU ARE SAFE'
                        : predicted_risk === 'MEDIUM' ? '⚠ CAUTION REQUIRED'
                            : '⚠ YOU ARE UNSAFE'}
                </div>
                <div style={{
                    fontSize: '1.1rem',
                    color: 'var(--text-secondary)',
                    fontWeight: '500'
                }}>
                    {predicted_risk === 'LOW'
                        ? 'Your PPD exposure levels are within safe limits. Continue maintaining good practices.'
                        : predicted_risk === 'MEDIUM'
                            ? 'Moderate exposure detected. Review recommendations and take preventive measures.'
                            : 'High exposure risk detected. Immediate action required to reduce health risks.'}
                </div>
            </div>



            {/* Scores Section */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: isCreatinineMode ? '1fr 1fr' : '1fr',
                gap: '1.5rem',
                marginBottom: '2rem',
                background: 'rgba(255,255,255,0.02)',
                padding: '1.5rem',
                borderRadius: '12px'
            }}>
                {/* Base Exposure Score */}
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                        <span>Base Exposure Score</span>
                        <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{scorePercentage}/100</span>
                    </div>
                    <div className="score-bar">
                        <div
                            className="score-fill"
                            style={{ width: `${scorePercentage}%`, backgroundColor: barColor }}
                        />
                    </div>
                </div>

                {/* Normalized PPD (Creatinine Mode Only) */}
                {isCreatinineMode && (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                            <span>Normalized PPD Concentration</span>
                            <span style={{ fontWeight: 'bold', color: '#34d399' }}>{normalized_ppd} units</span>
                        </div>
                        <div style={{
                            padding: '0.75rem',
                            background: 'rgba(52, 211, 153, 0.1)',
                            borderRadius: '8px',
                            border: '1px solid rgba(52, 211, 153, 0.3)'
                        }}>
                            <div style={{ fontSize: '0.85rem', color: '#a7f3d0' }}>
                                Creatinine: {result.creatinine_value} mg/dL ({creatinine_status?.status || 'Normal'})
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                                {creatinine_status?.interpretation || 'Within normal range'}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Confidence Level (Creatinine Mode) */}
            {
                isCreatinineMode && confidence && (
                    <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                        <span style={{
                            display: 'inline-block',
                            padding: '0.5rem 1.5rem',
                            background: confidence === 'HIGH' ? 'rgba(52, 211, 153, 0.2)' : 'rgba(251, 191, 36, 0.2)',
                            border: `1px solid ${confidence === 'HIGH' ? 'rgba(52, 211, 153, 0.4)' : 'rgba(251, 191, 36, 0.4)'}`,
                            borderRadius: '20px',
                            fontSize: '0.9rem',
                            color: confidence === 'HIGH' ? '#a7f3d0' : '#fcd34d'
                        }}>
                            Confidence Level: {confidence}
                        </span>
                    </div>
                )
            }

            {/* Detailed Factor Analysis */}
            {
                factor_details && factor_details.length > 0 && (
                    <div className="key-factors" style={{ marginBottom: '2rem' }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem' }}>
                            Detailed Factor Analysis ({factor_details.length} factors)
                        </h3>
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {factor_details.map((factor, index) => (
                                <div key={index} style={{
                                    padding: '1rem',
                                    background: 'rgba(255,255,255,0.03)',
                                    borderRadius: '10px',
                                    border: `1px solid ${getFactorColor(factor.risk_level)}33`
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--text-main)' }}>
                                                {factor.name}
                                            </div>
                                            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                                                {factor.value}
                                            </div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{
                                                fontSize: '1.2rem',
                                                fontWeight: 'bold',
                                                color: getFactorColor(factor.risk_level)
                                            }}>
                                                {factor.contribution}%
                                            </div>
                                            <div style={{
                                                fontSize: '0.75rem',
                                                color: getFactorColor(factor.risk_level),
                                                opacity: 0.8
                                            }}>
                                                {factor.risk_level} Risk
                                            </div>
                                        </div>
                                    </div>
                                    <p style={{
                                        margin: '0.75rem 0 0 0',
                                        fontSize: '0.85rem',
                                        color: '#94a3b8',
                                        lineHeight: '1.5'
                                    }}>
                                        {factor.description}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )
            }

            {/* Health Recommendations (Creatinine Mode) */}
            {
                recommendations && recommendations.length > 0 && (
                    <div style={{
                        marginTop: '2rem',
                        padding: '1.5rem',
                        background: 'rgba(99, 102, 241, 0.1)',
                        borderRadius: '12px',
                        border: '1px solid rgba(99, 102, 241, 0.3)'
                    }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '1.2rem', color: '#c7d2fe' }}>
                            🏥 Personalized Health Recommendations
                        </h3>
                        <ul style={{
                            margin: 0,
                            paddingLeft: '1.5rem',
                            listStyle: 'none'
                        }}>
                            {recommendations.map((rec, index) => (
                                <li key={index} style={{
                                    marginBottom: '0.75rem',
                                    fontSize: '0.9rem',
                                    color: 'var(--text-secondary)',
                                    lineHeight: '1.6',
                                    paddingLeft: '0.5rem'
                                }}>
                                    {rec}
                                </li>
                            ))}
                        </ul>
                    </div>
                )
            }

            {/* Analysis Footer */}
            <div style={{
                marginTop: '2rem',
                padding: '1rem',
                textAlign: 'center',
                fontSize: '0.8rem',
                color: '#64748b',
                borderTop: '1px solid rgba(255,255,255,0.1)'
            }}>
                <div>{isCreatinineMode ? 'Advanced Creatinine-Normalized Analysis' : 'Standard Exposure Assessment'}</div>
                <div style={{ marginTop: '0.25rem' }}>
                    Total Factors Analyzed: {result.total_factors_analyzed || factor_details.length}
                </div>
                {result.analysis_date && (
                    <div style={{ marginTop: '0.25rem', fontStyle: 'italic' }}>
                        {result.analysis_date}
                    </div>
                )}
            </div>
        </div >
    );
};

export default ResultCard;
