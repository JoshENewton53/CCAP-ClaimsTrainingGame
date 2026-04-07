import React, { useState } from 'react';

function ReasonModal({ answer, claimType, onSubmit, onCancel }) {
  const [selectedReasons, setSelectedReasons] = useState([]);

  const invalidReasons = [
    'Procedure code does not match diagnosis',
    'Service not covered by policy',
    'Pre-authorization not obtained',
    'Claim amount exceeds policy limits',
    'Patient not eligible at time of service',
    'Duplicate claim submission',
    'Service date outside policy coverage period',
    'Provider not in network',
    'Incorrect billing codes',
    'Missing required documentation',
    'Prior authorization for wrong procedure',
    'Prior authorization expired',
    'Insurance card expired',
    'Patient name does not match insurance records',
  ];

  const insufficientReasonsByType = {
    medical: [
      'Missing patient medical records',
      'Missing physician notes',
      'Missing itemized bill',
      'Missing insurance card copy',
      'Missing prior authorization',
      'Missing diagnostic images/X-rays',
      'Missing treatment plan',
      'Prior authorization pending',
      'Prior authorization expired',
    ],
    dental: [
      'Missing patient medical records',
      'Missing physician notes',
      'Missing itemized bill',
      'Missing insurance card copy',
      'Missing prior authorization',
      'Missing diagnostic images/X-rays',
      'Missing treatment plan',
      'Prior authorization pending',
      'Prior authorization expired',
    ],
    life: [
      'Missing death certificate',
      'Missing policy documents',
      'Missing beneficiary identification',
      'Missing physician notes',
      'Missing insurance card copy',
      'Missing prior authorization',
      'Prior authorization pending',
    ],
  };

  const reasons = answer === 'invalid'
    ? invalidReasons
    : (insufficientReasonsByType[claimType] || insufficientReasonsByType.medical);

  const toggleReason = (reason) => {
    setSelectedReasons(prev =>
      prev.includes(reason) ? prev.filter(r => r !== reason) : [...prev, reason]
    );
  };

  const isInvalid = answer === 'invalid';
  const accentColor = isInvalid ? 'red' : 'yellow';
  const accentClasses = {
    border: isInvalid ? 'border-red-500/40' : 'border-yellow-500/40',
    headerBorder: isInvalid ? 'border-red-500/30' : 'border-yellow-500/30',
    selectedBg: isInvalid ? 'bg-red-500/20 border-red-500 text-white' : 'bg-yellow-500/20 border-yellow-500 text-white',
    checkBg: isInvalid ? 'bg-red-500 border-red-500' : 'bg-yellow-500 border-yellow-500',
    submitBtn: isInvalid ? 'bg-red-500 hover:bg-red-400 text-white' : 'bg-yellow-500 hover:bg-yellow-400 text-black',
    badge: isInvalid ? 'bg-red-500/20 text-red-300 border-red-500/30' : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  };

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4">
      <div className={`bg-principal-dark rounded-xl shadow-2xl w-full max-w-xl border ${accentClasses.border}`}>

        {/* Header */}
        <div className={`p-5 border-b ${accentClasses.headerBorder}`}>
          <h2 className="text-xl font-bold text-white text-center">
            Why is this claim {isInvalid ? 'Invalid' : 'Insufficient'}?
          </h2>
          <p className="text-gray-400 text-sm text-center mt-1">
            Select all that apply — correct selections earn bonus points
          </p>
        </div>

        {/* Reason grid */}
        <div className="p-5 max-h-[55vh] overflow-y-auto">
          <div className="grid grid-cols-2 gap-2">
            {reasons.map((reason, index) => {
              const selected = selectedReasons.includes(reason);
              return (
                <button
                  key={index}
                  onClick={() => toggleReason(reason)}
                  className={`text-left p-3 rounded-lg border-2 transition-all text-sm ${
                    selected
                      ? accentClasses.selectedBg
                      : 'bg-gray-800/60 border-gray-700 text-gray-300 hover:border-gray-500'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div className={`mt-0.5 w-4 h-4 rounded flex-shrink-0 border-2 flex items-center justify-center ${
                      selected ? accentClasses.checkBg : 'border-gray-600'
                    }`}>
                      {selected && <span className="text-black font-bold text-xs">✓</span>}
                    </div>
                    <span className="leading-snug">{reason}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className={`p-5 border-t ${accentClasses.headerBorder} flex items-center gap-3`}>
          <button
            onClick={onCancel}
            className="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSubmit(selectedReasons)}
            className={`flex-1 py-2.5 font-bold rounded-lg transition-colors ${accentClasses.submitBtn}`}
          >
            Submit
          </button>
          {selectedReasons.length > 0 && (
            <span className={`text-xs px-2 py-1 rounded border font-semibold ${accentClasses.badge}`}>
              {selectedReasons.length} selected
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default ReasonModal;
