import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../services/api';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await signup({ username, password });
            navigate('/');
        } catch (err) {
            setError(err.message || 'Signup failed');
        }
    };

    return (
        <div className="container">
            <div className="glass-card">
                <h1>Signup</h1>
                {error && <div style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit">Signup</button>
                    <p style={{ marginTop: '1rem', textAlign: 'center', color: '#94a3b8' }}>
                        Already have an account? <Link to="/" style={{ color: '#818cf8' }}>Login</Link>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Signup;
