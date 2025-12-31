import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/main.css';
import PredictionForm from './pages/PredictionForm';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/predict" element={<PredictionForm />} />
      </Routes>
    </Router>
  );
}

export default App;
