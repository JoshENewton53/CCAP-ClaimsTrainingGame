import React, { useState } from 'react';
import axios from 'axios';
import './GameScreen.css';
import FeedbackModal from './FeedbackModal';
import ClientProfile from './ClientProfile';
import PolicyGuide from './PolicyGuide';
import CodeMatcher from './CodeMatcher';

function GameScreen({ scenario, onComplete }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showCodeMatcher, setShowCodeMatcher] = useState(false);

  const handleSubmit = async (answer) => {
    setLoading(true);

    try {
      const response = await axios.post('/api/scenario/submit', {
        scenario_id: scenario.id,
        user_answer: answer
      }, {
        withCredentials: true
      });

      setResult(response.data);
    } catch (err) {
      console.error(err);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    onComplete(result);
  };

  return (
    <div className="game-screen">
      <div className="sidebar">
        <ClientProfile clientData={scenario.client_profile} />
        <button 
          className="btn btn-reference sidebar-btn" 
          onClick={() => setShowCodeMatcher(true)}
        >
          View Code Reference
        </button>
        <PolicyGuide />
      </div>
      
      <div className="main-content">
        <div className="scenario-card">
          <div className="scenario-header">
            <h2>Claim Scenario</h2>
            <div className="difficulty-badge">
              <span className={`badge badge-${scenario.difficulty}`}>
                {scenario.difficulty.toUpperCase()} - {scenario.max_points} pts
              </span>
            </div>
          </div>
        
        <div className="scenario-details">
          <div className="detail-row">
            <span className="label">Claim Type:</span>
            <span className="value">{scenario.claim_type}</span>
          </div>
          <div className="detail-row">
            <span className="label">Procedure Code:</span>
            <span className="value">{scenario.procedure_code}</span>
          </div>
          <div className="detail-row">
            <span className="label">Diagnosis Code:</span>
            <span className="value">{scenario.diagnosis_code}</span>
          </div>
          <div className="detail-row">
            <span className="label">Claim Amount:</span>
            <span className="value">${scenario.claim_amount.toFixed(2)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Patient Age:</span>
            <span className="value">{scenario.patient_age}</span>
          </div>
          
          {scenario.client_profile && scenario.client_profile.injury_date && (
            <div className="detail-row">
              <span className="label">Date of Injury/Service:</span>
              <span className="value">{new Date(scenario.client_profile.injury_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        <div className="description">
          <h3>Description:</h3>
          <p>{scenario.description}</p>
        </div>

        <div className="documents">
          <h3>Document Status:</h3>
          
          <div className="documents-section">
            <h4 className="documents-submitted-title">Documents Submitted: ✓</h4>
            <ul className="documents-submitted">
              {scenario.document_status.submitted.map((doc, index) => (
                <li key={index} className="document-item submitted">
                  <span className="checkmark">✓</span> {doc}
                </li>
              ))}
            </ul>
          </div>
          
          {scenario.document_status.missing.length > 0 && (
            <div className="documents-section">
              <h4 className="documents-missing-title">Documents Missing: ✗</h4>
              <ul className="documents-missing">
                {scenario.document_status.missing.map((doc, index) => (
                  <li key={index} className="document-item missing">
                    <span className="x-mark">✗</span> {doc}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="action-buttons">
          <button 
            className="btn btn-valid" 
            onClick={() => handleSubmit('valid')}
            disabled={loading}
          >
            Valid
          </button>
          <button 
            className="btn btn-insufficient" 
            onClick={() => handleSubmit('insufficient')}
            disabled={loading}
          >
            Insufficient Info
          </button>
          <button 
            className="btn btn-invalid" 
            onClick={() => handleSubmit('invalid')}
            disabled={loading}
          >
            Invalid
          </button>
        </div>
        </div>
      </div>

      <CodeMatcher
        isOpen={showCodeMatcher}
        onClose={() => setShowCodeMatcher(false)}
        claimType={scenario.claim_type}
        currentProcedure={scenario.procedure_code}
        currentDiagnosis={scenario.diagnosis_code}
      />

      {result && <FeedbackModal result={result} onNext={handleNext} />}
    </div>
  );
}

export default GameScreen;
