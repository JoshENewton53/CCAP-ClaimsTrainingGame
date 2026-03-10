import React, { useState } from 'react';

function ReasonModal({ answer, onSubmit, onCancel }) {
  const [selectedReasons, setSelectedReasons] = useState([]);

  const reasons = answer === 'invalid' ? [
    'Missing required documentation',
    'Procedure code does not match diagnosis',
    'Service not covered by policy',
    'Pre-authorization not obtained',
    'Claim amount exceeds policy limits',
    'Patient not eligible at time of service',
    'Duplicate claim submission',
    'Service date outside policy coverage period',
    'Provider not in network',
    'Incorrect billing codes'
  ] : [
    'Missing patient medical records',
    'Missing physician notes',
    'Missing itemized bill',
    'Missing insurance card copy',
    'Missing prior authorization',
    'Missing diagnostic images/X-rays',
    'Missing treatment plan',
    'Missing death certificate',
    'Missing policy documents',
    'Missing beneficiary identification'
  ];

  const toggleReason = (reason) => {
    if (selectedReasons.includes(reason)) {
      setSelectedReasons(selectedReasons.filter(r => r !== reason));
    } else {
      setSelectedReasons([...selectedReasons, reason]);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-principal-dark rounded-lg shadow-2xl max-w-2xl w-full border border-principal-blue/30">
        <div className="bg-gradient-to-r from-principal-dark to-principal-darker p-6 border-b border-principal-blue/30">
          <h2 className="text-2xl font-bold text-white text-center">
            Why is this claim {answer === 'invalid' ? 'Invalid' : 'Insufficient'}?
          </h2>
          <p className="text-gray-400 text-center mt-2">Select all that apply</p>
        </div>
        
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          <div className="space-y-2">
            {reasons.map((reason, index) => (
              <button
                key={index}
                onClick={() => toggleReason(reason)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedReasons.includes(reason)
                    ? 'bg-principal-blue/20 border-principal-blue text-white'
                    : 'bg-gray-800/50 border-gray-700 text-gray-300 hover:border-gray-600'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                    selectedReasons.includes(reason)
                      ? 'bg-principal-blue border-principal-blue'
                      : 'border-gray-600'
                  }`}>
                    {selectedReasons.includes(reason) && (
                      <span className="text-black font-bold">✓</span>
                    )}
                  </div>
                  <span>{reason}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
        
        <div className="p-6 border-t border-principal-blue/30 flex gap-4">
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSubmit(selectedReasons)}
            disabled={selectedReasons.length === 0}
            className="flex-1 bg-principal-blue hover:bg-blue-400 disabled:bg-gray-600 text-black font-bold py-3 rounded-lg transition-colors"
          >
            Submit ({selectedReasons.length} selected)
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReasonModal;
