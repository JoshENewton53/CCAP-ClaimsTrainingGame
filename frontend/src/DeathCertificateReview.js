import React, { useState, useEffect } from 'react';
import './DeathCertificateReview.css';
import API_BASE from './config';

function DeathCertificateReview({ difficulty, scenario, onComplete, onSubmit, compact }) {
  const [localScenario, setLocalScenario] = useState(scenario);
  const [selectedErrors, setSelectedErrors] = useState([]);
  const [errorOptions, setErrorOptions] = useState([]);
  const [loading, setLoading] = useState(!scenario);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!scenario) {
      loadScenario();
    }
    loadErrorOptions();
  }, [difficulty, scenario]);

  const loadScenario = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/death-certificate/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ difficulty })
      });
      const data = await response.json();
      console.log('Death cert scenario:', data);
      setLocalScenario(data);
    } catch (error) {
      console.error('Error loading scenario:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadErrorOptions = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/death-certificate/error-options`, {
        credentials: 'include'
      });
      const data = await response.json();
      setErrorOptions(data.error_options);
    } catch (error) {
      console.error('Error loading error options:', error);
    }
  };

  const toggleError = (errorId) => {
    setSelectedErrors(prev =>
      prev.includes(errorId)
        ? prev.filter(e => e !== errorId)
        : [...prev, errorId]
    );
  };

  const handleSubmit = async () => {
    if (!localScenario) return;

    if (compact && onSubmit) {
      // Compact mode - just pass findings to parent
      onSubmit(selectedErrors);
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE}/api/death-certificate/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          user_findings: selectedErrors,
          actual_errors: localScenario.errors,
          difficulty: localScenario.difficulty
        })
      });
      const data = await response.json();
      setResult(data);
      if (onSubmit) onSubmit(data);
    } catch (error) {
      console.error('Error submitting review:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleContinue = () => {
    if (onComplete) {
      onComplete(result);
    }
    setResult(null);
    setSelectedErrors([]);
    if (!scenario) {
      loadScenario();
    }
  };

  if (loading) {
    return <div className="loading">Loading death certificate...</div>;
  }

  if (!localScenario) {
    return <div className="error">Failed to load scenario</div>;
  }

  if (compact) {
    return (
      <div className="death-cert-compact">
        <div className="error-checklist-compact">
          {errorOptions.map(option => (
            <label key={option.id} className="error-option-compact">
              <input
                type="checkbox"
                checked={selectedErrors.includes(option.id)}
                onChange={() => toggleError(option.id)}
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="death-certificate-review">
      <h2>Life Insurance Claim - Death Certificate Review</h2>
      
      <div className="review-container">
        <div className="certificate-section">
          <h3>Death Certificate</h3>
          <div className="certificate-viewer">
            {localScenario.certificate_pdf ? (
              <>
                <object
                  data={`data:application/pdf;base64,${localScenario.certificate_pdf}`}
                  type="application/pdf"
                  className="certificate-pdf"
                >
                  <p>PDF cannot be displayed. 
                    <a 
                      href={`data:application/pdf;base64,${localScenario.certificate_pdf}`}
                      download="death_certificate.pdf"
                      className="download-link"
                    >
                      Download PDF
                    </a>
                  </p>
                </object>
                <a 
                  href={`data:application/pdf;base64,${localScenario.certificate_pdf}`}
                  download="death_certificate.pdf"
                  className="download-button"
                >
                  📄 Download Certificate
                </a>
              </>
            ) : localScenario.certificate_image ? (
              <img
                src={`data:image/jpeg;base64,${localScenario.certificate_image}`}
                alt="Death Certificate"
                className="certificate-image"
              />
            ) : (
              <p>Loading certificate...</p>
            )}
          </div>
          
          <div className="policy-info">
            <h4>Policy Information</h4>
            <p><strong>Policy Number:</strong> {localScenario.policy_data.policy_number}</p>
            <p><strong>Policy Holder:</strong> {localScenario.policy_data.policy_holder}</p>
            <p><strong>Policy Effective Date:</strong> {localScenario.policy_data.policy_effective_date}</p>
            <p><strong>Benefit Amount:</strong> ${localScenario.policy_data.benefit_amount.toLocaleString()}</p>
            <p><strong>State:</strong> {localScenario.policy_data.state}</p>
          </div>
        </div>

        <div className="review-section">
          <h3>Review Checklist</h3>
          <p className="instructions">
            Review the death certificate carefully and check all issues you identify:
          </p>
          
          <div className="error-checklist">
            {errorOptions.map(option => (
              <label key={option.id} className={`error-option severity-${option.severity}`}>
                <input
                  type="checkbox"
                  checked={selectedErrors.includes(option.id)}
                  onChange={() => toggleError(option.id)}
                  disabled={result !== null}
                />
                <span className="error-label">
                  {option.label}
                  <span className={`severity-badge ${option.severity}`}>
                    {option.severity}
                  </span>
                </span>
              </label>
            ))}
          </div>

          <div className="no-errors-option">
            <label>
              <input
                type="checkbox"
                checked={selectedErrors.length === 0}
                onChange={() => setSelectedErrors([])}
                disabled={result !== null}
              />
              <span>No issues found - Certificate is valid</span>
            </label>
          </div>

          {!result && (
            <button
              className="submit-button"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
          )}

          {result && (
            <div className={`result-panel ${result.correct ? 'correct' : 'incorrect'}`}>
              <h3>{result.correct ? '✓ Correct!' : '✗ Incorrect'}</h3>
              <p className="score">Score: {result.score}/100</p>
              <p className="points">Points Earned: {result.points_earned}</p>
              
              {result.missed_errors && result.missed_errors.length > 0 && (
                <div className="missed-errors">
                  <h4>Missed Issues:</h4>
                  <ul>
                    {result.missed_errors.map(error => (
                      <li key={error}>{error.replace('_', ' ')}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {result.incorrect_flags && result.incorrect_flags.length > 0 && (
                <div className="false-positives">
                  <h4>Incorrectly Flagged:</h4>
                  <ul>
                    {result.incorrect_flags.map(error => (
                      <li key={error}>{error.replace('_', ' ')}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.new_achievements && result.new_achievements.length > 0 && (
                <div className="new-achievements">
                  <h4>🏆 New Achievements!</h4>
                  {result.new_achievements.map((ach, idx) => (
                    <div key={idx} className="achievement">
                      <strong>{ach.name}</strong>: {ach.desc}
                    </div>
                  ))}
                </div>
              )}

              <button className="continue-button" onClick={handleContinue}>
                Continue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DeathCertificateReview;
