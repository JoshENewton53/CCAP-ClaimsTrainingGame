import React, { useState } from 'react';
import './PolicyGuide.css';

function PolicyGuide() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('acceptance');

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'acceptance':
        return (
          <div>
            <p className="policy-intro">A claim is VALID when ALL of the following are met:</p>
            <ul className="policy-list">
              <li>✓ Procedure code matches diagnosis code (verify in Code Reference)</li>
              <li>✓ Patient age matches client profile DOB (within 1 year)</li>
              <li>✓ All CRITICAL documents submitted (see below)</li>
              <li>✓ Claim amount within reasonable ranges</li>
            </ul>
            <p className="policy-section-title">Critical Documents by Claim Type:</p>
            <ul className="policy-list">
              <li><strong>Medical:</strong> Patient medical records, Physician notes and diagnosis</li>
              <li><strong>Dental:</strong> X-rays or diagnostic images, Treatment plan with CDT codes</li>
              <li><strong>Life:</strong> Death certificate, Policy documents</li>
            </ul>
          </div>
        );
      case 'denial':
        return (
          <div>
            <p className="policy-intro">A claim is INVALID when ANY of the following occur:</p>
            <ul className="policy-list">
              <li>✗ Procedure code does NOT match diagnosis code</li>
              <li>✗ Patient age differs by more than 1 year from profile</li>
              <li>✗ Injury/service date is BEFORE policy start date (pre-existing condition)</li>
              <li>✗ Service not covered under policy type</li>
              <li>✗ Policy expired, lapsed, or within contestability period</li>
              <li>✗ Evidence of fraud or duplicate submission</li>
            </ul>
            <p className="policy-note">Note: Invalid claims cannot be fixed with additional documentation.</p>
          </div>
        );
      case 'insufficient':
        return (
          <div>
            <p className="policy-intro">A claim has INSUFFICIENT INFO when:</p>
            <ul className="policy-list">
              <li>⚠ Missing CRITICAL documents (see Acceptance tab)</li>
              <li>⚠ Missing supporting documents (insurance card, authorization)</li>
              <li>⚠ Illegible or incomplete forms</li>
              <li>⚠ High-value claims requiring investigation (&gt;$20K medical, &gt;$500K life)</li>
            </ul>
            <p className="policy-note">Note: These claims can be approved once missing information is provided.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="policy-guide">
      <div className="policy-header" onClick={toggleExpanded}>
        <h3>Company Claims Policy</h3>
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
          ▼
        </span>
      </div>
      
      {isExpanded && (
        <div className="policy-content">
          <div className="policy-tabs">
            <button
              className={`tab-button ${activeTab === 'acceptance' ? 'active' : ''}`}
              onClick={() => setActiveTab('acceptance')}
            >
              Acceptance Criteria
            </button>
            <button
              className={`tab-button ${activeTab === 'denial' ? 'active' : ''}`}
              onClick={() => setActiveTab('denial')}
            >
              Denial Criteria
            </button>
            <button
              className={`tab-button ${activeTab === 'insufficient' ? 'active' : ''}`}
              onClick={() => setActiveTab('insufficient')}
            >
              Insufficient Info
            </button>
          </div>
          
          <div className="tab-content">
            {renderTabContent()}
          </div>
        </div>
      )}
    </div>
  );
}

export default PolicyGuide;