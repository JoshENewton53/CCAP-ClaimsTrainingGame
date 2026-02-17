import React, { useState } from 'react';
import axios from 'axios';
import './StartGame.css';

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

  return (
    <div className="start-game">
      <h2>Start New Game</h2>
      
      <div className="form-group">
        <label htmlFor="claim-type">Claim Type:</label>
        <select 
          id="claim-type"
          value={claimType} 
          onChange={(e) => setClaimType(e.target.value)}
          disabled={loading}
        >
          <option value="medical">Medical</option>
          <option value="dental">Dental</option>
          <option value="life">Life Insurance</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="difficulty">Difficulty:</label>
        <select 
          id="difficulty"
          value={difficulty} 
          onChange={(e) => setDifficulty(e.target.value)}
          disabled={loading}
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button 
        className="start-button" 
        onClick={handleStartGame}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Start Game'}
      </button>
    </div>
  );
}

export default StartGame;
