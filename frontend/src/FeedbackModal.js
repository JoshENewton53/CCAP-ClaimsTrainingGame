import React from 'react';
import './FeedbackModal.css';

function FeedbackModal({ result, onNext }) {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className={`result-header ${result.is_correct ? 'correct' : 'incorrect'}`}>
          <h2>{result.is_correct ? '✓ Correct!' : '✗ Incorrect'}</h2>
          <p className="points">{result.points_earned > 0 ? '+' : ''}{result.points_earned} points</p>
        </div>
        
        {result.new_achievements && result.new_achievements.length > 0 && (
          <div className="achievements-unlocked">
            <h3>🏆 New Achievements Unlocked!</h3>
            {result.new_achievements.map((ach, idx) => (
              <div key={idx} className="new-achievement">
                <strong>{ach.name}</strong>: {ach.desc}
              </div>
            ))}
          </div>
        )}
        
        <div className="modal-body">
          <div className="feedback-section">
            <h3>Feedback:</h3>
            <p>{result.feedback_text}</p>
          </div>
          
          <div className="answer-section">
            <p><strong>Correct Answer:</strong> {result.correct_answer}</p>
          </div>
        </div>
        
        <div className="modal-footer">
          <button className="next-button" onClick={onNext}>
            Next Scenario
          </button>
        </div>
      </div>
    </div>
  );
}

export default FeedbackModal;
