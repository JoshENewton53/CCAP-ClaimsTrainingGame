import React, { useState, useEffect } from 'react';
import './App.css';
import API_BASE from './config';
import Login from './Login';
import StartGame from './StartGame';
import GameScreen from './GameScreen';
import Achievements from './Achievements';
import Account from './Account';
import Leaderboard from './Leaderboard';
import AdminDashboard from './AdminDashboard';
import IntroPage from './IntroPage';

function App() {
  const [user, setUser] = useState(null);
  const [scenario, setScenario] = useState(null);
  const [showAchievements, setShowAchievements] = useState(false);
  const [showAccount, setShowAccount] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [showIntro, setShowIntro] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    fetch(`${API_BASE}/api/auth/me`, {
      credentials: 'include'
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setUser(data);
          if (!localStorage.getItem('seenIntro')) {
            setShowIntro(true);
          }
        }
        return data;
      })
      .catch(() => {});
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    if (!localStorage.getItem('seenIntro')) {
      setShowIntro(true);
    }
  };

  const handleLogout = async () => {
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
    setScenario(null);
    setShowIntro(false);
  };

  const handleGameStart = (scenarioData) => {
    setScenario(scenarioData);
  };

  const handleComplete = (result) => {
    setUser({ ...user, score: result.total_score, current_streak: result.current_streak, 
             xp: result.xp, level: result.level });
    setScenario(null);
  };

  const handleAccountUpdate = () => {
    // Refresh user data after profile update
    fetch(`${API_BASE}/api/auth/me`, {
      credentials: 'include'
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => data && setUser(data))
      .catch(() => {});
  };

  const xpToNextLevel = user ? ((user.level || 1) * 100) : 100;
  const currentLevelXp = user ? (user.xp || 0) % 100 : 0;
  const xpProgress = (currentLevelXp / 100) * 100;

  if (user && user.username === 'Admin1') {
    return <AdminDashboard onLogout={handleLogout} />;
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-principal-dark to-principal-darker flex flex-col items-center">
        <header className="mt-10 text-center w-full max-w-3xl px-6">
          <div className="flex items-center justify-center gap-4 mb-2">
            <h1 className="text-4xl font-bold text-white">Claims Training Buddy</h1>
            <img 
              src="/PrincipalLogo3.png" 
              alt="Principal Logo" 
              className="h-12 w-auto"
            />
          </div>
        </header>
        <main className="w-full max-w-3xl px-6 py-8">
          <Login onLogin={handleLogin} />
        </main>
      </div>
    );
  }

  if (showIntro) {
    return <IntroPage onContinue={() => {
      localStorage.setItem('seenIntro', 'true');
      setShowIntro(false);
    }} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-principal-dark to-principal-darker flex flex-col items-center">
      <header className="mt-10 text-center w-full max-w-7xl px-6">
        <div className="flex items-center justify-center gap-4 mb-4">
          <h1 className="text-4xl font-bold text-white">Claims Training Buddy</h1>
          <img 
            src="/PrincipalLogo3.png" 
            alt="Principal Logo" 
            className="h-12 w-auto"
          />
        </div>
        
        <div className="bg-principal-dark/50 backdrop-blur-sm rounded-xl p-4 border border-principal-blue/30 shadow-xl">
          <div className="flex items-center justify-between gap-6 flex-wrap">
            <div className="flex items-center gap-4">
              <span className="text-white font-bold text-xl">{user.username}</span>
              <div className="h-8 w-px bg-principal-blue/30"></div>
              <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black px-5 py-2 rounded-lg font-bold text-lg border-2 border-yellow-300 shadow-lg">
                Level {user.level || 1}
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex flex-col items-start min-w-[160px]">
                <span className="text-green-400 font-semibold text-sm mb-1">XP: {user.xp || 0} / {xpToNextLevel}</span>
                <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden border border-green-400/30">
                  <div 
                    className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-500"
                    style={{ width: `${xpProgress}%` }}
                  />
                </div>
              </div>
              
              <div className="bg-principal-blue/20 px-4 py-2 rounded-lg border border-principal-blue">
                <div className="text-principal-blue text-xs font-semibold">SCORE</div>
                <div className="text-white font-bold text-2xl">{user.score}</div>
              </div>
              
              <div className={`px-4 py-2 rounded-lg border-2 ${
                user.current_streak >= 0 
                  ? 'bg-principal-blue/20 border-principal-blue' 
                  : 'bg-red-500/20 border-red-500'
              }`}>
                <div className={`text-xs font-semibold ${
                  user.current_streak >= 0 ? 'text-principal-blue' : 'text-red-400'
                }`}>STREAK</div>
                <div className={`font-bold text-2xl ${
                  user.current_streak >= 0 ? 'text-white' : 'text-white'
                }`}>{user.current_streak}</div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors shadow-lg"
                onClick={() => setShowLeaderboard(true)}
              >
                🏆 Leaderboard
              </button>
              
              <button 
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors shadow-lg"
                onClick={() => setShowAccount(true)}
              >
                👤 Account
              </button>
              
              <button 
                className="bg-teal-600 hover:bg-teal-500 text-white px-4 py-2 rounded-lg font-semibold transition-colors shadow-lg"
                onClick={() => setShowIntro(true)}
              >
                📘 How to Play
              </button>

              <button 
                className="bg-principal-blue hover:bg-blue-400 text-black px-4 py-2 rounded-lg font-bold text-2xl transition-colors shadow-lg"
                onClick={() => setShowAchievements(true)}
              >
                🏆
              </button>
              
              <button 
                className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg font-semibold transition-colors shadow-lg"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="w-full max-w-7xl px-6 py-8">
        {!scenario ? (
          <StartGame onGameStart={handleGameStart} />
        ) : (
          <GameScreen scenario={scenario} onComplete={handleComplete} />
        )}
      </main>
      
      {showAchievements && <Achievements onClose={() => setShowAchievements(false)} />}
      {showAccount && <Account user={user} onClose={() => setShowAccount(false)} onUpdate={handleAccountUpdate} />}
      {showLeaderboard && <Leaderboard onClose={() => setShowLeaderboard(false)} />}
    </div>
  );
}

export default App;
