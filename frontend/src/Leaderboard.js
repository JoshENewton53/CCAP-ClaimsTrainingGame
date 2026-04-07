import React, { useState, useEffect } from 'react';
import API_BASE from './config';

function Leaderboard({ onClose }) {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/leaderboard`, {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        console.log('Leaderboard data:', data);
        setLeaderboard(data.leaderboard || []);
      })
      .catch(err => {
        console.error('Leaderboard error:', err);
        setLeaderboard([]);
      });
  }, []);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-principal-dark rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden border border-principal-blue/30" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-gradient-to-r from-principal-dark to-principal-darker p-6 border-b border-principal-blue/30">
          <h2 className="text-3xl font-bold text-white text-center">🏆 Leaderboard</h2>
        </div>
        
        <div className="overflow-y-auto max-h-[calc(90vh-200px)] p-6">
          {leaderboard.length === 0 ? (
            <div className="text-center text-gray-400 py-8">No users on leaderboard yet</div>
          ) : (
            <div className="space-y-3">
            {leaderboard.map((user, index) => (
              <div key={user.username} className={`flex items-center gap-4 p-4 rounded-lg border-2 ${
                index === 0 ? 'bg-yellow-500/20 border-yellow-500' :
                index === 1 ? 'bg-gray-400/20 border-gray-400' :
                index === 2 ? 'bg-orange-600/20 border-orange-600' :
                'bg-gray-800/50 border-gray-700'
              }`}>
                <div className={`text-2xl font-bold w-12 text-center ${
                  index === 0 ? 'text-yellow-400' :
                  index === 1 ? 'text-gray-300' :
                  index === 2 ? 'text-orange-400' :
                  'text-gray-400'
                }`}>
                  {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                </div>
                
                <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-700 border-2 border-principal-blue flex-shrink-0">
                  {user.profile_picture ? (
                    <img src={`data:image/jpeg;base64,${user.profile_picture}`} alt={user.username} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-3xl text-gray-400">
                      👤
                    </div>
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="text-white font-bold text-lg">{user.username}</div>
                  <div className="text-gray-400 text-sm">Level {user.level}</div>
                </div>
                
                <div className="text-right">
                  <div className="text-principal-blue font-bold text-2xl">{user.score}</div>
                  <div className="text-gray-400 text-sm">points</div>
                </div>
              </div>
            ))}
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

export default Leaderboard;
