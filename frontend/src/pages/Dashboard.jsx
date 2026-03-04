import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const navigate = useNavigate();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    // Get User ID and Name from LocalStorage
    const USER_ID = localStorage.getItem('user_id');
    const USER_NAME = localStorage.getItem('username') || 'Patient'; // Fallback

    useEffect(() => {
        if (!USER_ID) {
            navigate('/');
            return;
        }
        fetchHistory();
    }, [USER_ID, navigate]);

    const fetchHistory = async () => {
        try {
            const res = await fetch(`http://127.0.0.1:5001/history?user_id=${USER_ID}`);
            const data = await res.json();
            if (res.ok) {
                // Reverse for chart (oldest to newest)
                setHistory(data);
            }
        } catch (err) {
            console.error("Failed to fetch history", err);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = async (item) => {
        try {
            const res = await fetch('http://127.0.0.1:5001/download-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: USER_NAME,
                    risk_data: {
                        risk_level: item.risk_level,
                        exposure_score: item.score,
                        factor_details: item.details.factor_details,
                        health_recommendations: item.details.health_recommendations,
                        creatinine_value: item.details.creatinine_value
                    }
                })
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Risk_Report_${item.date}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert("Failed to generate report");
            }
        } catch (err) {
            console.error(err);
            alert("Error downloading report");
        }
    };

    // Prepare data for Chart (Recharts needs data in ascending order usually for time)
    const chartData = [...history].reverse().map(item => ({
        date: new Date(item.date).toLocaleDateString(),
        score: item.score
    }));

    return (
        <div className="container" style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '2rem', textAlign: 'center' }}>Safety Dashboard</h1>

            {/* --- Prediction Startup Section --- */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
                <div className="glass-card" onClick={() => navigate('/predict')} style={{ cursor: 'pointer', textAlign: 'center' }}>
                    <h3 style={{ color: 'var(--primary)' }}>Standard Assessment</h3>
                    <p style={{ color: '#ccc', margin: '1rem 0' }}>Quick questionnaire-based check.</p>
                </div>
                <div className="glass-card" onClick={() => navigate('/predict-with-creatinine')} style={{ cursor: 'pointer', textAlign: 'center', border: '1px solid #34d399' }}>
                    <h3 style={{ color: '#34d399' }}>Advanced Lab Assessment</h3>
                    <p style={{ color: '#ccc', margin: '1rem 0' }}>High-precision check with Creatinine.</p>
                </div>
            </div>

            {/* --- Analytics Section --- */}
            <div className="glass-card" style={{ padding: '2rem' }}>
                <h2 style={{ marginBottom: '1.5rem' }}>Risk Trends Analytics</h2>

                {loading ? (
                    <p>Loading analytics...</p>
                ) : history.length > 0 ? (
                    <div style={{ height: '300px', width: '100%', marginBottom: '2rem' }}>
                        <ResponsiveContainer>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="date" stroke="#888" />
                                <YAxis domain={[0, 1]} stroke="#888" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#333', border: 'none' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Line type="monotone" dataKey="score" stroke="#8884d8" strokeWidth={3} activeDot={{ r: 8 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <p style={{ textAlign: 'center', color: '#666' }}>No history available. Run a prediction to see trends.</p>
                )}

                {/* --- Recent Activity Table --- */}
                <h3 style={{ marginBottom: '1rem', marginTop: '2rem' }}>Recent Reports</h3>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', color: 'white' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #444', textAlign: 'left' }}>
                                <th style={{ padding: '10px' }}>Date</th>
                                <th style={{ padding: '10px' }}>Risk Level</th>
                                <th style={{ padding: '10px' }}>Score</th>
                                <th style={{ padding: '10px' }}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map((item) => (
                                <tr key={item.id} style={{ borderBottom: '1px solid #333' }}>
                                    <td style={{ padding: '10px' }}>{new Date(item.date).toLocaleDateString()}</td>
                                    <td style={{
                                        padding: '10px',
                                        color: item.risk_level === 'HIGH' ? '#ff6b6b' : item.risk_level === 'MEDIUM' ? '#fcc419' : '#51cf66'
                                    }}>
                                        {item.risk_level}
                                    </td>
                                    <td style={{ padding: '10px' }}>{item.score}</td>
                                    <td style={{ padding: '10px' }}>
                                        <button
                                            onClick={() => downloadReport(item)}
                                            style={{
                                                padding: '5px 10px',
                                                fontSize: '0.8rem',
                                                background: '#228be6',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Download PDF
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
