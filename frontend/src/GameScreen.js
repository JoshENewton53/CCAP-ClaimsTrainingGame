import React, { useState } from 'react';
import axios from 'axios';
import API_BASE from './config';
import FeedbackModal from './FeedbackModal';
import ClientProfile from './ClientProfile';
import PolicyGuide from './PolicyGuide';
import CodeMatcher from './CodeMatcher';
import DeathCertificateReview from './DeathCertificateReview';
import ReasonModal from './ReasonModal';

function GameScreen({ scenario, onComplete }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showCodeMatcher, setShowCodeMatcher] = useState(false);
  const [deathCertScenario, setDeathCertScenario] = useState(null);
  const [deathCertResult, setDeathCertResult] = useState(null);
  const [showReasonModal, setShowReasonModal] = useState(false);
  const [pendingAnswer, setPendingAnswer] = useState(null);
  const [aiHints, setAiHints] = useState([]);
  const [attempts, setAttempts] = useState(0);
  const [openDocs, setOpenDocs] = useState(new Set());

  const toggleDoc = (key) => setOpenDocs(prev => {
    const next = new Set(prev);
    next.has(key) ? next.delete(key) : next.add(key);
    return next;
  });

  // Load death certificate for life insurance claims
  React.useEffect(() => {
    if (scenario.claim_type === 'life') {
      loadDeathCertificate();
    }
  }, [scenario]);

  const loadDeathCertificate = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/death-certificate/generate`, {
        difficulty: scenario.difficulty,
        client_profile: scenario.client_profile
      }, { withCredentials: true });
      setDeathCertScenario(response.data);
    } catch (err) {
      console.error('Failed to load death certificate:', err);
      alert('Error loading death certificate: ' + (err.response?.data?.error || err.message));
    }
  };

  const getAiHint = async () => {
    console.log('Getting AI hint for scenario:', scenario.id);
    try {
      const response = await axios.post(`${API_BASE}/api/ai/hint`, {
        scenario_id: scenario.id,
        attempts: attempts
      }, { withCredentials: true });
      console.log('AI hint response:', response.data);
      setAiHints(response.data.hints || []);
      setAttempts(attempts + 1);
    } catch (err) {
      console.error('Failed to get AI hint:', err);
      alert('Failed to get AI hint: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleSubmit = async (answer) => {
    if (answer === 'invalid' || answer === 'insufficient') {
      setPendingAnswer(answer);
      setShowReasonModal(true);
    } else {
      submitAnswer(answer, []);
    }
  };

  const submitAnswer = async (answer, reasons) => {
    setLoading(true);
    setShowReasonModal(false);

    try {
      const response = await axios.post(`${API_BASE}/api/scenario/submit`, {
        scenario_id: scenario.id,
        user_answer: answer,
        reasons: reasons
      }, {
        withCredentials: true
      });

      setResult(response.data);
    } catch (err) {
      console.error('Submit error:', err.response?.data || err.message);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    onComplete(result);
  };

  console.log('Scenario data:', scenario);
  console.log('Has itemized_bill:', !!scenario.itemized_bill);

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
        <button 
          className="w-full bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2 px-4 rounded-lg transition-colors" 
          onClick={getAiHint}
        >
          🤖 Get AI Hint
        </button>
        {aiHints.length > 0 && (
          <div className="bg-purple-900/50 border border-purple-500 rounded-lg p-4">
            <h4 className="text-purple-300 font-bold mb-2 flex items-center">
              <span className="mr-2">🤖</span> AI Hints:
            </h4>
            {aiHints.map((hint, idx) => (
              <p key={idx} className="text-gray-300 text-sm mb-1">{hint}</p>
            ))}
          </div>
        )}
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
          <h3 className="text-xl font-bold text-principal-blue mb-3">Claim Documents:</h3>
          <div className="space-y-2">
            {[...scenario.document_status.submitted, ...scenario.document_status.missing].map((docName) => {
              const isSubmitted = scenario.document_status.submitted.includes(docName);
              const open = openDocs.has(docName);

              const renderContent = () => {
                if (!isSubmitted) {
                  return <p className="text-gray-500 italic text-sm">This document was not submitted with the claim.</p>;
                }

                if (docName === 'Itemized bill with CPT codes' && scenario.itemized_bill) {
                  const bill = scenario.itemized_bill;
                  return (
                    <div>
                      <div className="bg-white text-black p-4 rounded">
                        <div className="text-center mb-3">
                          <h5 className="font-bold text-lg">{bill.provider}</h5>
                          <p className="text-sm">Service Date: {bill.service_date}</p>
                        </div>
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b-2 border-black">
                              <th className="text-left py-2">Code</th>
                              <th className="text-left py-2">Description</th>
                              <th className="text-center py-2">Qty</th>
                              <th className="text-right py-2">Unit Cost</th>
                              <th className="text-right py-2">Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {bill.items.map((item, idx) => (
                              <tr key={idx} className="border-b border-gray-300">
                                <td className="py-2 font-mono">{item.code}</td>
                                <td className="py-2">{item.description}</td>
                                <td className="text-center py-2">{item.quantity}</td>
                                <td className="text-right py-2">${item.unit_cost.toFixed(2)}</td>
                                <td className="text-right py-2">${item.total.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot>
                            <tr className="border-t-2 border-black font-bold">
                              <td colSpan="4" className="text-right py-2">Total:</td>
                              <td className="text-right py-2">${bill.total.toFixed(2)}</td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                      <p className="text-yellow-400 text-sm mt-2">⚠️ Review carefully for accuracy</p>
                    </div>
                  );
                }

                if (docName === 'Death certificate') {
                  if (!deathCertScenario) {
                    return <p className="text-gray-400 text-sm">Loading certificate...</p>;
                  }
                  return (
                    <div>
                      <div className="mb-3">
                        {deathCertScenario.certificate_pdf ? (
                          <object
                            data={`data:application/pdf;base64,${deathCertScenario.certificate_pdf}`}
                            type="application/pdf"
                            className="w-full h-96 rounded-lg border border-gray-700"
                          >
                            <p className="text-gray-400 text-sm">PDF cannot be displayed.{' '}
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
                          <p className="text-gray-400 text-sm">Loading certificate...</p>
                        )}
                      </div>
                      <div className="text-gray-300 space-y-1 text-sm">
                        <p><strong>Policy Holder:</strong> {deathCertScenario.policy_data.policy_holder}</p>
                        <p><strong>Policy Date:</strong> {deathCertScenario.policy_data.policy_effective_date}</p>
                        <p><strong>Death Date:</strong> {deathCertScenario.policy_data.death_date}</p>
                      </div>
                    </div>
                  );
                }

                if (docName === 'Insurance card copy' && scenario.generated_docs?.insurance_card) {
                  const card = scenario.generated_docs.insurance_card;
                  return (
                    <div className="bg-gradient-to-br from-principal-blue to-blue-800 rounded-xl p-4 text-white max-w-sm mx-auto shadow-lg">
                      <div className="text-xs font-bold uppercase tracking-widest mb-3 opacity-75">{card.plan_name}</div>
                      <div className="text-lg font-bold mb-1">{card.member_name}</div>
                      <div className="text-xs opacity-75 mb-3">Member Name</div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div><div className="opacity-75 text-xs">Member ID</div><div className="font-mono font-semibold">{card.member_id}</div></div>
                        <div><div className="opacity-75 text-xs">Group #</div><div className="font-mono font-semibold">{card.group_number}</div></div>
                        <div><div className="opacity-75 text-xs">Effective</div><div className="font-semibold">{card.effective_date}</div></div>
                        <div><div className="opacity-75 text-xs">Expires</div><div className={`font-semibold ${card.is_expired ? 'text-red-300' : ''}`}>{card.expiry_date}</div></div>
                        <div><div className="opacity-75 text-xs">Copay</div><div className="font-semibold">{card.copay}</div></div>
                        <div><div className="opacity-75 text-xs">Deductible</div><div className="font-semibold">{card.deductible}</div></div>
                      </div>
                    </div>
                  );
                }

                if ((docName === 'Prior authorization (if required)' || docName === 'Prior authorization') && scenario.generated_docs?.prior_auth) {
                  const auth = scenario.generated_docs.prior_auth;
                  const statusColor = auth.status === 'Approved' ? 'text-green-400' : auth.status === 'Pending' ? 'text-yellow-400' : 'text-red-400';
                  return (
                    <div className="font-mono text-sm">
                      <div className="bg-gray-900 rounded p-4 space-y-2 text-gray-300">
                        <div className="flex justify-between border-b border-gray-700 pb-2 mb-3">
                          <span className="text-white font-bold text-base not-italic" style={{fontFamily:'sans-serif'}}>Prior Authorization Notice</span>
                          <span className={`font-bold ${statusColor}`} style={{fontFamily:'sans-serif'}}>{auth.status}</span>
                        </div>
                        <div>Auth Number: <span className="text-white">{auth.auth_number}</span></div>
                        <div>Auth Date: <span className="text-white">{auth.auth_date}</span></div>
                        <div>Expiry Date: <span className={auth.is_expired ? 'text-red-400' : 'text-white'}>{auth.expiry_date}</span></div>
                        <div>Requested Procedure: <span className="text-white">{auth.requested_procedure}</span></div>
                        <div>Authorized Procedure: <span className={auth.is_mismatch ? 'text-yellow-400' : 'text-white'}>{auth.authorized_procedure}</span></div>
                      </div>
                    </div>
                  );
                }

                if (docName === 'Physician notes and diagnosis' && scenario.generated_docs?.physician_notes) {
                  return (
                    <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono bg-gray-900 rounded p-4 leading-relaxed">
                      {scenario.generated_docs.physician_notes.content}
                    </pre>
                  );
                }

                if (docName === 'Patient medical records' && scenario.generated_docs?.medical_record) {
                  return (
                    <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono bg-gray-900 rounded p-4 leading-relaxed">
                      {scenario.generated_docs.medical_record.content}
                    </pre>
                  );
                }

                return <p className="text-gray-400 text-sm">Document on file.</p>;
              };

              const docIcons = {
                'Itemized bill with CPT codes': '📄',
                'Death certificate': '📋',
                'Insurance card copy': '🪪',
                'Prior authorization (if required)': '📝',
                'Prior authorization': '📝',
                'Physician notes and diagnosis': '🩺',
                'Patient medical records': '📁',
              };
              const icon = docIcons[docName] || '📄';

              return (
                <div key={docName} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                  <button
                    onClick={() => toggleDoc(docName)}
                    className="w-full flex justify-between items-center p-3 text-left hover:bg-gray-700/50"
                  >
                    <span className="font-semibold flex items-center gap-2">
                      <span className={isSubmitted ? 'text-green-400' : 'text-red-400'}>
                        {isSubmitted ? '✓' : '✗'}
                      </span>
                      <span className="text-white">{icon} {docName}</span>
                    </span>
                    <span className="text-gray-400 text-sm flex-shrink-0 ml-2">{open ? '▲ Hide' : '▼ View'}</span>
                  </button>
                  {open && (
                    <div className="p-4 border-t border-gray-700">
                      {renderContent()}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
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
      {showReasonModal && (
        <ReasonModal
          answer={pendingAnswer}
          claimType={scenario.claim_type}
          onSubmit={(reasons) => submitAnswer(pendingAnswer, reasons)}
          onCancel={() => {
            setShowReasonModal(false);
            setPendingAnswer(null);
          }}
        />
      )}
    </div>
  );
}

export default GameScreen;
