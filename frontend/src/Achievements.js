import React, { useState, useEffect } from 'react';
import './Achievements.css';

function Achievements({ onClose }) {
  const [achievements, setAchievements] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/achievements', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => setAchievements(data.achievements))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="achievements-overlay" onClick={onClose}>
      <div className="achievements-modal" onClick={(e) => e.stopPropagation()}>
        <h2>Achievements</h2>
        <div className="achievements-grid">
          {achievements.map(ach => (
            <div key={ach.key} className={`achievement-card ${ach.unlocked ? 'unlocked' : 'locked'}`}>
              <div className="achievement-icon">{ach.unlocked ? '🏆' : '🔒'}</div>
              <h3>{ach.name}</h3>
              <p>{ach.description}</p>
              {ach.unlocked && ach.unlocked_at && (
                <span className="unlock-date">
                  {new Date(ach.unlocked_at).toLocaleDateString()}
                </span>
              )}
            </div>
          ))}
        </div>
        <button className="close-btn" onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

export default Achievements;
