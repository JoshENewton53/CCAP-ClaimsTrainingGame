import React, { useState, useEffect } from 'react';
import API_BASE from './config';

function Achievements({ onClose }) {
  const [achievements, setAchievements] = useState([]);

  const getAchievementIcon = (key) => {
    const icons = {
      'first_claim': '🎯',
      'streak_5': '🔥',
      'streak_10': '⚡',
      'perfect_10': '💯',
      'score_100': '⭐',
      'score_500': '🌟',
      'score_1000': '💎',
      'level_5': '🎖️',
      'level_10': '👑',
      'speed_demon': '⚡',
      'accuracy_master': '🎯',
      'claim_master': '🏆',
      'leaderboard_top25': '📊',
      'leaderboard_top10': '🥉',
      'leaderboard_top3': '🥈',
      'leaderboard_rank1': '🥇'
    };
    return icons[key] || '🏆';
  };

  useEffect(() => {
    fetch(`${API_BASE}/api/achievements`, {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.achievements) {
          setAchievements(data.achievements);
        }
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-principal-dark rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-principal-blue/30" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-gradient-to-r from-principal-dark to-principal-darker p-6 border-b border-principal-blue/30">
          <h2 className="text-3xl font-bold text-white text-center">🏆 Achievements</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
          {achievements && achievements.length > 0 ? achievements.map(ach => (
            <div key={ach.key} className={`rounded-lg p-5 border-2 transition-all ${
              ach.unlocked 
                ? 'bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border-yellow-500 shadow-lg shadow-yellow-500/20' 
                : 'bg-gray-800/50 border-gray-700 opacity-60'
            }`}>
              <div className="text-4xl text-center mb-3">{ach.unlocked ? getAchievementIcon(ach.key) : '🔒'}</div>
              <h3 className="text-xl font-bold text-white text-center mb-2">{ach.name}</h3>
              <p className="text-gray-300 text-center text-sm mb-2">{ach.description}</p>
              {ach.unlocked && ach.unlocked_at && (
                <span className="block text-center text-xs text-principal-blue mt-2">
                  {new Date(ach.unlocked_at).toLocaleDateString()}
                </span>
              )}
            </div>
          )) : (
            <div className="col-span-full text-center text-gray-400 py-8">
              Loading achievements...
            </div>
          )}
        </div>
        
        <div className="sticky bottom-0 bg-principal-dark p-6 border-t border-principal-blue/30">
          <button 
            onClick={onClose}
            className="w-full bg-principal-blue hover:bg-blue-400 text-black font-bold py-3 rounded-lg transition-colors shadow-lg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default Achievements;
