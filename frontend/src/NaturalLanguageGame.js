import React, { useState } from 'react';
import axios from 'axios';

const DECISION_OPTIONS = ['valid', 'invalid', 'insufficient'];

function ResultPanel({ result, onNext }) {
  const allCorrect = result.decision_correct && result.proc_correct && result.diag_correct;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-xl w-full overflow-y-auto max-h-[85vh]">
        <div className={`p-6 text-center rounded-t-lg ${allCorrect ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-red-400 to-red-600'} text-white`}>
          <h2 className="text-3xl font-bold mb-1">{allCorrect ? '✓ Excellent!' : result.decision_correct ? '~ Partial Credit' : '✗ Incorrect'}</h2>
          <p className="text-2xl font-semibold">{result.points_earned >= 0 ? '+' : ''}{result.points_earned} points</p>
          <p className="text-lg mt-1 text-green-100">+{result.xp_earned} XP &nbsp;·&nbsp; Level {result.level}</p>
        </div>

        <div className="p-6 space-y-4">
          {/* Extraction scorecard */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <h3 className="font-bold text-gray-800 mb-2">Extraction Results:</h3>
            {[
              { label: 'Procedure Type', correct: result.proc_correct, yours: result.user_procedure, answer: result.correct_procedure_category },
              { label: 'Diagnosis Category', correct: result.diag_correct, yours: result.user_diagnosis, answer: result.correct_diagnosis_category },
              { label: 'Claim Decision', correct: result.decision_correct, yours: result.user_answer, answer: result.correct_answer },
            ].map(row => (
              <div key={row.label} className="flex items-start gap-2 text-sm">
                <span className={`mt-0.5 font-bold ${row.correct ? 'text-green-500' : 'text-red-500'}`}>{row.correct ? '✓' : '✗'}</span>
                <div>
                  <span className="font-semibold text-gray-700">{row.label}: </span>
                  {!row.correct && <span className="text-red-600">You said "{row.yours}" — </span>}
                  <span className={row.correct ? 'text-green-700 font-semibold' : 'text-gray-800'}>
                    Correct: "{row.answer}"
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Feedback */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <h3 className="font-bold text-blue-800 mb-1">Feedback:</h3>
            <p className="text-gray-700 text-sm leading-relaxed">{result.feedback_text}</p>
          </div>
        </div>

        <div className="p-6 border-t border-gray-200">
          <button
            onClick={onNext}
            className="w-full bg-principal-blue hover:bg-blue-400 text-black font-bold py-4 rounded-lg transition-colors text-xl"
          >
            Next Scenario
          </button>
        </div>
      </div>
    </div>
  );
}

export default function NaturalLanguageGame({ scenario, onComplete }) {
  const [userProcedure, setUserProcedure] = useState('');
  const [userDiagnosis, setUserDiagnosis] = useState('');
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const canSubmit = userProcedure && userDiagnosis && userAnswer && !loading;

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/api/scenario/nl-submit', {
        scenario_id: scenario.id,
        user_procedure: userProcedure,
        user_diagnosis: userDiagnosis,
        user_answer: userAnswer,
      }, { withCredentials: true });
      setResult({ ...res.data, user_procedure: userProcedure, user_diagnosis: userDiagnosis, user_answer: userAnswer });
    } catch (err) {
      alert('Submission failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => onComplete(result);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-principal-dark rounded-lg border border-principal-blue/20 p-5">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-2xl font-bold text-white">📄 Natural Language Claim</h2>
          <div className="flex items-center gap-3">
            {scenario.has_red_flag && (
              <span className="bg-orange-500/20 border border-orange-500 text-orange-300 text-xs font-bold px-3 py-1 rounded-full">
                ⚠ May contain red flags
              </span>
            )}
            <span className={`px-4 py-2 rounded-lg font-bold text-sm ${
              scenario.difficulty === 'easy' ? 'bg-green-500 text-white' :
              scenario.difficulty === 'medium' ? 'bg-yellow-500 text-black' : 'bg-red-500 text-white'
            }`}>
              {scenario.difficulty.toUpperCase()} — up to {scenario.max_points} pts
            </span>
          </div>
        </div>
        <p className="text-gray-400 text-sm">
          Read the claim note below. Extract the key details using the dropdowns, then make your decision.
        </p>
      </div>

      {/* Claim paragraph */}
      <div className="bg-gray-900 border border-gray-600 rounded-lg p-6">
        <h3 className="text-principal-blue font-bold mb-3 text-lg">Claim Submission Note:</h3>
        <p className="text-gray-100 leading-relaxed text-base italic">"{scenario.paragraph}"</p>
      </div>

      {/* Extraction form */}
      <div className="bg-principal-dark rounded-lg border border-principal-blue/20 p-6 space-y-5">
        <h3 className="text-white font-bold text-lg">Step 1 — Extract the Details</h3>

        <div>
          <label className="block text-principal-blue font-semibold mb-2">
            What type of procedure was performed?
          </label>
          <select
            value={userProcedure}
            onChange={e => setUserProcedure(e.target.value)}
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none"
          >
            <option value="">— Select procedure type —</option>
            {scenario.procedure_categories.map(cat => (
              <option key={cat.label} value={cat.label}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-principal-blue font-semibold mb-2">
            What is the primary diagnosis / reason for visit?
          </label>
          <select
            value={userDiagnosis}
            onChange={e => setUserDiagnosis(e.target.value)}
            className="w-full px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-principal-blue focus:outline-none"
          >
            <option value="">— Select diagnosis category —</option>
            {scenario.diagnosis_categories.map(cat => (
              <option key={cat.label} value={cat.label}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div>
          <h3 className="text-white font-bold text-lg mb-3">Step 2 — Make Your Decision</h3>
          <div className="grid grid-cols-3 gap-3">
            {DECISION_OPTIONS.map(opt => (
              <button
                key={opt}
                onClick={() => setUserAnswer(opt)}
                className={`py-3 rounded-lg font-bold capitalize transition-colors border-2 ${
                  userAnswer === opt
                    ? opt === 'valid' ? 'bg-green-500 border-green-400 text-white'
                      : opt === 'invalid' ? 'bg-red-500 border-red-400 text-white'
                      : 'bg-yellow-500 border-yellow-400 text-black'
                    : 'bg-gray-800 border-gray-600 text-gray-300 hover:border-gray-400'
                }`}
              >
                {opt === 'insufficient' ? 'Insufficient Info' : opt.charAt(0).toUpperCase() + opt.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Scoring breakdown hint */}
        <div className="bg-gray-800 rounded-lg p-3 text-xs text-gray-400 space-y-1">
          <p className="font-semibold text-gray-300">Point breakdown:</p>
          <p>• Correct decision: {Math.round(scenario.max_points * 0.6)} pts &nbsp;·&nbsp; Correct procedure: {Math.round(scenario.max_points * 0.2)} pts &nbsp;·&nbsp; Correct diagnosis: {Math.round(scenario.max_points * 0.2)} pts</p>
        </div>

        <button
          onClick={handleSubmit}
          disabled={true}
          className="w-full bg-principal-blue hover:bg-blue-400 disabled:bg-gray-600 disabled:cursor-not-allowed text-black font-bold py-4 rounded-lg transition-colors text-xl"
        >
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </div>

      {result && <ResultPanel result={result} onNext={handleNext} />}
    </div>
  );
}
