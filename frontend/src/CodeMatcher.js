import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CodeMatcher.css';

function CodeMatcher({ isOpen, onClose, claimType, currentProcedure, currentDiagnosis }) {
  const [codes, setCodes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && claimType) {
      loadCodes();
    }
  }, [isOpen, claimType]);

  const loadCodes = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/reference/codes?type=${claimType}`);
      setCodes(response.data.codes);
    } catch (error) {
      console.error('Failed to load reference codes:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCodes = codes.filter(code => 
    code.procedure_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    code.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    code.valid_diagnosis_codes.some(diag => 
      diag.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  if (!isOpen) return null;

  return (
    <div className="code-matcher-overlay">
      <div className="code-matcher-modal">
        <div className="code-matcher-header">
          <h3>Code Reference - {claimType.charAt(0).toUpperCase() + claimType.slice(1)} Claims</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {currentProcedure && currentDiagnosis && (
          <div className="current-claim-info">
            <strong>Current Claim:</strong> Procedure {currentProcedure} + Diagnosis {currentDiagnosis}
          </div>
        )}
        
        <div className="code-matcher-controls">
          <input
            type="text"
            placeholder="Search by code or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="code-matcher-content">
          {loading ? (
            <div className="loading">Loading reference codes...</div>
          ) : (
            <table className="codes-table">
              <thead>
                <tr>
                  <th>Procedure Code</th>
                  <th>Valid Diagnosis Codes</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {filteredCodes.map((code, index) => (
                  <tr key={index}>
                    <td className="procedure-code">{code.procedure_code}</td>
                    <td className="diagnosis-codes">
                      {code.valid_diagnosis_codes.join(', ')}
                    </td>
                    <td className="description">{code.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default CodeMatcher;
