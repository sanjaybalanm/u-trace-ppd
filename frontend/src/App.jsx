import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/main.css';
import PredictionForm from './pages/PredictionForm';
import PredictionWithCreatinine from './pages/PredictionWithCreatinine';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';

import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/predict" element={<PredictionForm />} />
          <Route path="/predict-with-creatinine" element={<PredictionWithCreatinine />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
        <ChatWidget />
      </div>
    </Router>
  );
}

export default App;
