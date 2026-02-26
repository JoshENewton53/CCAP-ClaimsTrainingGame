import React, { useState } from 'react';
import axios from 'axios';
import FeedbackModal from './FeedbackModal';
import ClientProfile from './ClientProfile';
import PolicyGuide from './PolicyGuide';
import CodeMatcher from './CodeMatcher';
import DeathCertificateReview from './DeathCertificateReview';

function GameScreen({ scenario, onComplete }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showCodeMatcher, setShowCodeMatcher] = useState(false);
  const [deathCertScenario, setDeathCertScenario] = useState(null);
  const [deathCertResult, setDeathCertResult] = useState(null);

  // Load death certificate for life insurance claims
  React.useEffect(() => {
    if (scenario.claim_type === 'life') {
      loadDeathCertificate();
    }
  }, [scenario]);

  const loadDeathCertificate = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/death-certificate/generate', {
        difficulty: scenario.difficulty,
        client_profile: scenario.client_profile
      }, { withCredentials: true });
      setDeathCertScenario(response.data);
    } catch (err) {
      console.error('Failed to load death certificate:', err);
      alert('Error loading death certificate: ' + (err.response?.data?.error || err.message));
    }
  };

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
    <div className="flex gap-6">
      <div className="w-80 space-y-4">
        <ClientProfile clientData={scenario.client_profile} />
        <button 
          className="w-full bg-principal-blue hover:bg-blue-400 text-black font-semibold py-2 px-4 rounded-lg transition-colors" 
          onClick={() => setShowCodeMatcher(true)}
        >
          View Code Reference
        </button>
        <PolicyGuide />
      </div>
      
      <div className="flex-1">
        <div className="bg-principal-dark rounded-lg shadow-2xl p-6 border border-principal-blue/20">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Claim Scenario</h2>
            <span className={`px-4 py-2 rounded-lg font-bold ${
              scenario.difficulty === 'easy' ? 'bg-green-500 text-white' :
              scenario.difficulty === 'medium' ? 'bg-yellow-500 text-black' :
              'bg-red-500 text-white'
            }`}>
              {scenario.difficulty.toUpperCase()} - {scenario.max_points} pts
            </span>
          </div>
        
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-800 p-3 rounded-lg">
            <span className="text-principal-blue font-semibold block mb-1">Claim Type:</span>
            <span className="text-white">{scenario.claim_type}</span>
          </div>
          <div className="bg-gray-800 p-3 rounded-lg">
            <span className="text-principal-blue font-semibold block mb-1">Procedure Code:</span>
            <span className="text-white">{scenario.procedure_code}</span>
          </div>
          <div className="bg-gray-800 p-3 rounded-lg">
            <span className="text-principal-blue font-semibold block mb-1">Diagnosis Code:</span>
            <span className="text-white">{scenario.diagnosis_code}</span>
          </div>
          <div className="bg-gray-800 p-3 rounded-lg">
            <span className="text-principal-blue font-semibold block mb-1">Claim Amount:</span>
            <span className="text-white">${scenario.claim_amount.toFixed(2)}</span>
          </div>
          <div className="bg-gray-800 p-3 rounded-lg">
            <span className="text-principal-blue font-semibold block mb-1">Patient Age:</span>
            <span className="text-white">{scenario.patient_age}</span>
          </div>
          
          {scenario.client_profile && scenario.client_profile.injury_date && (
            <div className="bg-gray-800 p-3 rounded-lg">
              <span className="text-principal-blue font-semibold block mb-1">Date of Injury/Service:</span>
              <span className="text-white">{new Date(scenario.client_profile.injury_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        <div className="mb-6">
          <h3 className="text-xl font-bold text-principal-blue mb-2">Description:</h3>
          <p className="text-gray-300 leading-relaxed">{scenario.description}</p>
        </div>

        <div className="mb-6">
          <h3 className="text-xl font-bold text-principal-blue mb-3">Document Status:</h3>
          
          {scenario.claim_type === 'life' && (
            <div className="mb-4 bg-gray-800 p-4 rounded-lg">
              <h4 className="text-lg font-semibold text-white mb-2">Death Certificate Review:</h4>
              {!deathCertScenario && <p className="text-gray-400">Loading certificate...</p>}
              {deathCertScenario && (
                <>
                  <div className="mb-3">
                    {deathCertScenario.certificate_pdf ? (
                      <object
                        data={`data:application/pdf;base64,${deathCertScenario.certificate_pdf}`}
                        type="application/pdf"
                        className="w-full h-96 rounded-lg border border-gray-700"
                      >
                        <p className="text-gray-400">PDF cannot be displayed. 
                          <a 
                            href={`data:application/pdf;base64,${deathCertScenario.certificate_pdf}`}
                            download="death_certificate.pdf"
                            className="text-principal-blue underline"
                          >
                            Download PDF
                          </a>
                        </p>
                      </object>
                    ) : deathCertScenario.certificate_image ? (
                      <img
                        src={`data:image/jpeg;base64,${deathCertScenario.certificate_image}`}
                        alt="Death Certificate"
                        className="w-full rounded-lg border border-gray-700"
                      />
                    ) : (
                      <p className="text-gray-400">Loading certificate...</p>
                    )}
                  </div>
                  <div className="text-gray-300 space-y-1 mb-3">
                    <p><strong>Policy Holder:</strong> {deathCertScenario.policy_data.policy_holder}</p>
                    <p><strong>Policy Date:</strong> {deathCertScenario.policy_data.policy_effective_date}</p>
                    <p><strong>Death Date:</strong> {deathCertScenario.policy_data.death_date}</p>
                  </div>
                </>
              )}
            </div>
          )}
          
          <div className="mb-4">
            <h4 className="text-green-400 font-semibold mb-2">✓ Documents Submitted:</h4>
            <ul className="space-y-1">
              {scenario.document_status.submitted.map((doc, index) => (
                <li key={index} className="text-gray-300 flex items-center">
                  <span className="text-green-400 mr-2">✓</span> {doc}
                </li>
              ))}
            </ul>
          </div>
          
          {scenario.document_status.missing.length > 0 && (
            <div>
              <h4 className="text-red-400 font-semibold mb-2">✗ Documents Missing:</h4>
              <ul className="space-y-1">
                {scenario.document_status.missing.map((doc, index) => (
                  <li key={index} className="text-gray-300 flex items-center">
                    <span className="text-red-400 mr-2">✗</span> {doc}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex gap-4">
          <button 
            className="flex-1 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white font-bold py-4 rounded-lg transition-colors shadow-lg" 
            onClick={() => handleSubmit('valid')}
            disabled={loading}
          >
            Valid
          </button>
          <button 
            className="flex-1 bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-600 text-black font-bold py-4 rounded-lg transition-colors shadow-lg" 
            onClick={() => handleSubmit('insufficient')}
            disabled={loading}
          >
            Insufficient Info
          </button>
          <button 
            className="flex-1 bg-red-500 hover:bg-red-600 disabled:bg-gray-600 text-white font-bold py-4 rounded-lg transition-colors shadow-lg" 
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
