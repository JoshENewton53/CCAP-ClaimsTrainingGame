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
      const response = await axios.post('http://localhost:5000/api/scenario/generate', {
        claim_type: claimType,
        difficulty
      }, { withCredentials: true });
      onGameStart({ ...response.data, mode: 'standard' });
    } catch (err) {
      setError('Failed to generate scenario. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const points = { easy: '50 pts', medium: '100 pts', hard: '200 pts' };
  const xpByDiff = {
    easy: claimType === 'life' ? '14 XP' : '20 XP',
    medium: claimType === 'life' ? '35 XP' : '50 XP',
    hard: claimType === 'life' ? '70 XP' : '100 XP',
  };
  const diffColor = { easy: 'text-green-400', medium: 'text-yellow-400', hard: 'text-red-400' };

  return (
    <div className="flex justify-center">
      <div className="bg-principal-dark rounded-lg shadow-2xl p-8 w-full max-w-2xl border border-principal-blue/20">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">Start New Game</h2>

        <div className="space-y-6">
          <div>
            <label className="block text-principal-blue font-semibold mb-2 text-lg">Claim Type:</label>
            <select
              value={claimType}
              onChange={e => setClaimType(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all cursor-pointer"
            >
              <option value="medical">Medical Insurance</option>
              <option value="dental">Dental Insurance</option>
              <option value="life">Life Insurance</option>
            </select>
          </div>

          <div>
            <label className="block text-principal-blue font-semibold mb-2 text-lg">Difficulty:</label>
            <select
              value={difficulty}
              onChange={e => setDifficulty(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none focus:ring-2 focus:ring-principal-blue/50 transition-all cursor-pointer"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <div className={`mt-2 text-center ${diffColor[difficulty]} font-semibold`}>
              {points[difficulty]} · {xpByDiff[difficulty]}
            </div>
          </div>

          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg">{error}</div>
          )}

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
