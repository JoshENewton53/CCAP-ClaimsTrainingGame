import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
import StartGame from './StartGame';
import GameScreen from './GameScreen';
import Achievements from './Achievements';

function App() {
  const [user, setUser] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [showAchievements, setShowAchievements] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    fetch('http://localhost:5000/api/auth/me', {
      credentials: 'include'
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => data && setUser(data))
      .catch(() => {});
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    await fetch('http://localhost:5000/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
    setScenario(null);
  };

  const handleGameStart = (scenarioData) => {
    setScenario(scenarioData);
  };

  const handleComplete = (result) => {
    setUser({ ...user, score: result.total_score, current_streak: result.current_streak });
    setScenario(null);
  };

  if (!user) {
    return (
      <div className="app">
        <header className="app-header">
          <img 
            src="/PrincipalLogo3.png" 
            alt="Principal Logo" 
            className="principal-logo"
          />
          <h1>CCAP Claims Training Game</h1>
        </header>
        <main className="app-main">
          <Login onLogin={handleLogin} />
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <img 
          src="/PrincipalLogo3.png" 
          alt="Principal Logo" 
          className="principal-logo"
        />
        <h1>CCAP Claims Training Game</h1>
        <div className="user-info">
          <span className="username">{user.username}</span>
          <span className="score-display">Score: {user.score}</span>
          <span className={`streak-display ${user.current_streak >= 0 ? 'positive' : 'negative'}`}>
            Streak: {user.current_streak}
          </span>
          <button className="achievements-btn" onClick={() => setShowAchievements(true)}>🏆</button>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </header>
      <main className="app-main">
        {!scenario ? (
          <StartGame onGameStart={handleGameStart} />
        ) : (
          <GameScreen scenario={scenario} onComplete={handleComplete} />
        )}
      </main>
      {showAchievements && <Achievements onClose={() => setShowAchievements(false)} />}
    </div>
  );
}

export default App;
