import React, { useState } from 'react';
import API_BASE from './config';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
    
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data);
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  return (
    <div className="flex justify-center items-center">
      <div className="bg-principal-dark rounded-lg shadow-2xl p-8 w-full max-w-md border border-principal-blue/20">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">{isRegister ? 'Create Account' : 'Login'}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all"
          />
          {error && <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-2 rounded-lg">{error}</div>}
          <button type="submit" className="w-full bg-principal-blue hover:bg-blue-400 text-black font-bold py-3 rounded-lg transition-colors shadow-lg">
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>
        <button className="w-full mt-4 text-principal-blue hover:text-blue-400 font-semibold transition-colors" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Already have an account? Login' : 'Need an account? Register'}
        </button>
      </div>
    </div>
  );
}

export default Login;
