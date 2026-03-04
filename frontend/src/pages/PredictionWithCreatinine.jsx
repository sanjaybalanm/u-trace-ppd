import React, { useState } from 'react';
import { predictRiskWithCreatinine } from '../services/api';
import ResultCard from '../components/ResultCard';
import { useNavigate } from 'react-router-dom';

const PredictionWithCreatinine = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        age: '',
        gender: 'male',
        bmi: '',
        occupation: 'student',
        outdoor_hours: '',
        distance_to_main_road: '',
        two_wheeler_use: false,
        smoker: false,
        creatinine: '',
        ige_level: '',
        eosinophil_percentage: '',
        fev1: '',
        patch_test: '0'
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        // Basic validation
        if (!formData.age || !formData.bmi || !formData.creatinine) {
            setError("Please fill in all required fields.");
            setLoading(false);
            return;
        }

        try {
            const userId = localStorage.getItem('user_id');
            // If occupation is 'other', use the custom input value
            const finalOccupation = formData.occupation === 'other' ? (formData.customOccupation || 'Other') : formData.occupation;

            const dataToSubmit = {
                ...formData,
                occupation: finalOccupation,
                user_id: userId ? parseInt(userId) : null
            };
            // Remove temp field before sending
            delete dataToSubmit.customOccupation;

            const data = await predictRiskWithCreatinine(dataToSubmit);
            setResult(data);
        } catch (err) {
            console.error("Prediction Error:", err);
            setError("Failed to get prediction. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container" style={{ maxWidth: '100%', padding: '1rem' }}>
            <div className="glass-card" style={{ maxWidth: '1400px', margin: '0 auto' }}>
                <div style={{ marginBottom: '1rem' }}>
                    <button
                        onClick={() => navigate('/dashboard')}
                        style={{ background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', padding: 0, fontSize: '0.9rem' }}
                    >
                        ← Back to Dashboard
                    </button>
                </div>
                <h1>PPD Risk Predictor (Creatinine Mode)</h1>

                <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', justifyContent: 'center' }}>
                    <button
                        onClick={() => navigate('/predict')}
                        style={{ background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)' }}
                    >
                        Predict Without Test
                    </button>
                    <button
                        disabled
                        style={{ background: 'var(--primary)', color: 'white', cursor: 'default' }}
                    >
                        Predict With Creatinine Test
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    {/* Row 1: Age, Gender, BMI */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Age</label>
                            <input
                                type="number"
                                name="age"
                                value={formData.age}
                                onChange={handleChange}
                                placeholder="Years"
                                min="0"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Gender</label>
                            <select name="gender" value={formData.gender} onChange={handleChange}>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>BMI</label>
                            <input
                                type="number"
                                name="bmi"
                                value={formData.bmi}
                                onChange={handleChange}
                                placeholder="e.g. 24.5"
                                step="0.1"
                                required
                            />
                        </div>
                    </div>

                    {/* Row 2: Occupation, Outdoor Hours, Creatinine */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Occupation</label>
                            <select
                                name="occupation"
                                value={formData.occupation}
                                onChange={handleChange}
                            >
                                <option value="student">Student</option>
                                <option value="tyre_worker">Tyre Worker (High Risk)</option>
                                <option value="mechanic">Mechanic</option>
                                <option value="painter">Painter</option>
                                <option value="driver">Driver</option>
                                <option value="office_worker">Office Worker</option>
                                <option value="construction_worker">Construction Worker</option>
                                <option value="factory_worker">Factory Worker</option>
                                <option value="farmer">Farmer</option>
                                <option value="teacher">Teacher</option>
                                <option value="doctor">Healthcare Professional</option>
                                <option value="engineer">Engineer</option>
                                <option value="sales">Sales Professional</option>
                                <option value="other">Other (Specify)</option>
                            </select>

                            {formData.occupation === 'other' && (
                                <input
                                    type="text"
                                    name="customOccupation"
                                    value={formData.customOccupation || ''}
                                    onChange={handleChange}
                                    placeholder="Enter your occupation"
                                    style={{ marginTop: '0.5rem', border: '1px solid var(--primary)' }}
                                    required
                                />
                            )}
                        </div>

                        <div className="form-group">
                            <label>Outdoor Hours (Daily)</label>
                            <input
                                type="number"
                                name="outdoor_hours"
                                value={formData.outdoor_hours}
                                onChange={handleChange}
                                placeholder="Hours"
                                min="0"
                                max="24"
                            />
                        </div>

                        <div className="form-group">
                            <label>Urine Creatinine (mg/dL)</label>
                            <input
                                type="number"
                                name="creatinine"
                                value={formData.creatinine}
                                onChange={handleChange}
                                placeholder="Range: 0.5 - 2.5"
                                step="0.1"
                                min="0"
                                required
                            />
                        </div>
                    </div>

                    {/* Row 3: Clinical Markers */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Serum IgE (IU/mL)</label>
                            <input
                                type="number"
                                name="ige_level"
                                value={formData.ige_level || ''}
                                onChange={handleChange}
                                placeholder="Normal: 0-100"
                                min="0"
                            />
                        </div>
                        <div className="form-group">
                            <label>Eosinophil % (CBC)</label>
                            <input
                                type="number"
                                name="eosinophil_percentage"
                                value={formData.eosinophil_percentage || ''}
                                onChange={handleChange}
                                placeholder="Normal: 1-5%"
                                step="0.1"
                                min="0"
                                max="100"
                            />
                        </div>
                        <div className="form-group">
                            <label>FEV1 (% Predicted)</label>
                            <input
                                type="number"
                                name="fev1"
                                value={formData.fev1 || ''}
                                onChange={handleChange}
                                placeholder="Normal: ≥ 80%"
                                min="0"
                                max="150"
                            />
                        </div>
                    </div>

                    {/* Row 4: Patch Test & Distance */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Skin Patch Test Result</label>
                            <select name="patch_test" value={formData.patch_test || '0'} onChange={handleChange}>
                                <option value="0">Negative (Normal)</option>
                                <option value="1">Weak Positive (+)</option>
                                <option value="2">Strong Positive (++)</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Distance to Main Road (Meters)</label>
                            <input
                                type="number"
                                name="distance_to_main_road"
                                value={formData.distance_to_main_road}
                                onChange={handleChange}
                                placeholder="Meters"
                            />
                        </div>
                    </div>



                    <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                        <div className="checkbox-group">
                            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: 'var(--text-main)' }}>
                                <input
                                    type="checkbox"
                                    name="two_wheeler_use"
                                    checked={formData.two_wheeler_use}
                                    onChange={handleChange}
                                    style={{ width: 'auto', marginRight: '0.5rem' }}
                                />
                                Two-Wheeler User
                            </label>
                        </div>

                        <div className="checkbox-group">
                            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: 'var(--text-main)' }}>
                                <input
                                    type="checkbox"
                                    name="smoker"
                                    checked={formData.smoker}
                                    onChange={handleChange}
                                    style={{ width: 'auto', marginRight: '0.5rem' }}
                                />
                                Smoker
                            </label>
                        </div>
                    </div>

                    {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

                    <button type="submit" disabled={loading}>
                        {loading ? 'Analyzing...' : 'Predict (Refined with Creatinine)'}
                    </button>
                </form>

                <ResultCard result={result} />
            </div>
        </div>
    );
};

export default PredictionWithCreatinine;
