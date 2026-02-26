import React, { useState } from 'react';
import axios from 'axios';

function StartGame({ onGameStart }) {
  const [claimType, setClaimType] = useState('medical');
  const [difficulty, setDifficulty] = useState('easy');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStartGame = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/scenario/generate', {
        claim_type: claimType,
        difficulty: difficulty
      });

      onGameStart(response.data);
    } catch (err) {
      setError('Failed to generate scenario. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const difficultyInfo = {
    easy: { points: '50 pts', xp: claimType === 'life' ? '14 XP' : '20 XP', color: 'text-green-400' },
    medium: { points: '100 pts', xp: claimType === 'life' ? '35 XP' : '50 XP', color: 'text-yellow-400' },
    hard: { points: '200 pts', xp: claimType === 'life' ? '70 XP' : '100 XP', color: 'text-red-400' }
  };

  return (
    <div className="flex justify-center">
      <div className="bg-principal-dark rounded-lg shadow-2xl p-8 w-full max-w-2xl border border-principal-blue/20">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">Start New Game</h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-principal-blue font-semibold mb-2 text-lg">Claim Type:</label>
            <select 
              value={claimType} 
              onChange={(e) => setClaimType(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all cursor-pointer"
            >
              <option value="medical">Medical Insurance</option>
              <option value="dental">Dental Insurance</option>
              <option value="life">Life Insurance (Less XP)</option>
            </select>
          </div>

          <div>
            <label className="block text-principal-blue font-semibold mb-2 text-lg">Difficulty:</label>
            <select 
              value={difficulty} 
              onChange={(e) => setDifficulty(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all cursor-pointer"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <div className={`mt-2 text-center ${difficultyInfo[difficulty].color} font-semibold`}>
              {difficultyInfo[difficulty].points} • {difficultyInfo[difficulty].xp}
            </div>
          </div>

          {error && <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg">{error}</div>}

          <button 
            onClick={handleStartGame}
            disabled={loading}
            className="w-full bg-principal-blue hover:bg-blue-400 disabled:bg-gray-600 text-black font-bold py-4 rounded-lg transition-colors shadow-lg text-xl"
          >
            {loading ? 'Generating Scenario...' : 'Start Game'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default StartGame;
