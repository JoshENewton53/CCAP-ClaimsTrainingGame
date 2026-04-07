import React from 'react';
import './ClientProfile.css';

function ClientProfile({ clientData }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const calculateAge = (dob) => {
    const today = new Date();
    const birthDate = new Date(dob);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className="client-profile-card">
      <h3>Client Profile</h3>
      
      <div className="profile-details">
        <div className="profile-row">
          <span className="profile-label">Name:</span>
          <span className="profile-value">{clientData.name}</span>
        </div>
        
        <div className="profile-row">
          <span className="profile-label">Policy #:</span>
          <span className="profile-value">{clientData.policy_number}</span>
        </div>
        
        <div className="profile-row">
          <span className="profile-label">Date of Birth:</span>
          <span className="profile-value">{formatDate(clientData.date_of_birth)}</span>
        </div>
        
        <div className="profile-row">
          <span className="profile-label">Policy Start:</span>
          <span className="profile-value">{formatDate(clientData.policy_start_date)}</span>
        </div>

        {clientData.policy_end_date && (
          <div className="profile-row">
            <span className="profile-label">Policy End:</span>
            <span className="profile-value" style={{ color: clientData.policy_lapsed ? '#f87171' : 'inherit' }}>
              {formatDate(clientData.policy_end_date)}
              {clientData.policy_lapsed && ' ⚠ LAPSED'}
            </span>
          </div>
        )}

        {clientData.claim_submission_date && (
          <div className="profile-row">
            <span className="profile-label">Claim Filed:</span>
            <span className="profile-value" style={{ color: clientData.filing_deadline_exceeded ? '#f87171' : 'inherit' }}>
              {formatDate(clientData.claim_submission_date)}
              {clientData.filing_deadline_exceeded && ' ⚠ LATE'}
            </span>
          </div>
        )}

        <div className="profile-row">
          <span className="profile-label">Coverage:</span>
          <span className="profile-value">{clientData.coverage_type}</span>
        </div>

        <div className="profile-row">
          <span className="profile-label">Limits:</span>
          <span className="profile-value">{clientData.coverage_limits}</span>
        </div>

        {clientData.excluded_procedures && clientData.excluded_procedures.length > 0 && (
          <div className="profile-row">
            <span className="profile-label">Exclusions:</span>
            <span className="profile-value" style={{ color: '#f87171' }}>
              {clientData.excluded_procedures.join(', ')}
            </span>
          </div>
        )}
        
        {clientData.dependents && clientData.dependents.length > 0 && (
          <div className="profile-row">
            <span className="profile-label">Dependents:</span>
            <div className="dependents-list">
              {clientData.dependents.map((dependent, index) => (
                <div key={index} className="dependent-item">
                  {dependent.name} ({dependent.relationship}, Age: {calculateAge(dependent.date_of_birth)})
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ClientProfile;