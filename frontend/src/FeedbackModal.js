import React from 'react';

function FeedbackModal({ result, onNext }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className={`p-6 text-center rounded-t-lg ${
          result.is_correct 
            ? 'bg-gradient-to-r from-green-400 to-green-600 text-white' 
            : 'bg-gradient-to-r from-red-400 to-red-600 text-white'
        }`}>
          <h2 className="text-3xl font-bold mb-2">{result.is_correct ? '✓ Correct!' : '✗ Incorrect'}</h2>
          <p className="text-2xl font-semibold">{result.points_earned > 0 ? '+' : ''}{result.points_earned} points</p>
          {result.reason_score && result.reason_score.max_bonus > 0 && (
            <p className="text-yellow-300 font-bold text-lg mt-2">
              {result.reason_bonus > 0 ? `🎉 +${result.reason_bonus} reasoning bonus!` : '❌ No reasoning bonus earned'}
            </p>
          )}
          {result.xp_earned && <p className="text-xl font-semibold text-green-100 mt-1">+{result.xp_earned} XP</p>}
          {result.level && <p className="text-lg font-bold text-yellow-300 mt-1">Level {result.level}</p>}
        </div>
        
        {result.new_achievements && result.new_achievements.length > 0 && (
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 text-white p-6">
            <h3 className="text-2xl font-bold mb-3">🏆 New Achievements Unlocked!</h3>
            <div className="space-y-2">
              {result.new_achievements.map((ach, idx) => (
                <div key={idx} className="bg-white/20 backdrop-blur px-4 py-3 rounded-lg">
                  <strong className="text-lg">{ach.name}</strong>: {ach.desc}
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Feedback:</h3>
            <p className="text-gray-700 leading-relaxed">{result.feedback_text}</p>
          </div>
          
          {result.ai_confidence && (
            <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded mb-6">
              <h3 className="text-lg font-bold text-indigo-800 mb-3 flex items-center">
                <span className="mr-2">🤖</span> AI Analysis
              </h3>
              <div className="space-y-3">
                {result.ai_confidence.source && (
                  <p className="text-xs text-indigo-700">
                    Source:{' '}
                    {result.ai_confidence.source === 'ml_with_rules_audit'
                      ? 'Hybrid ML model (XGBoost + embeddings) with business-rule audit'
                      : 'Business-rule engine'}
                  </p>
                )}
                <div className="flex items-center gap-3">
                  <div>
                    <span className="text-gray-700 font-semibold">AI Predicted:</span>
                    <span className={`ml-2 px-2 py-0.5 rounded font-bold text-white capitalize ${
                      result.ai_confidence.prediction === 'valid' ? 'bg-green-500' :
                      result.ai_confidence.prediction === 'invalid' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}>
                      {result.ai_confidence.prediction}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-700 font-semibold">Confidence:</span>
                    <span className="text-indigo-900 font-bold ml-2">
                      {(result.ai_confidence.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <span className={`ml-auto px-2 py-0.5 rounded text-sm font-bold ${
                    result.ai_confidence.ai_agreed
                      ? 'bg-green-100 text-green-700'
                      : 'bg-orange-100 text-orange-700'
                  }`}>
                    {result.ai_confidence.ai_agreed ? 'AI agreed with your answer' : 'AI disagreed with your answer'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-700 font-semibold block mb-2">Probability Distribution:</span>
                  <div className="space-y-2">
                    {Object.entries(result.ai_confidence.probabilities).map(([key, val]) => (
                      <div key={key} className="flex items-center">
                        <span className="text-gray-700 w-28 capitalize">{key}:</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                          <div
                            className={`h-full flex items-center justify-end pr-2 text-white text-sm font-bold ${
                              key === 'valid' ? 'bg-green-500' :
                              key === 'invalid' ? 'bg-red-500' : 'bg-yellow-500'
                            }`}
                            style={{ width: `${val * 100}%` }}
                          >
                            {val > 0.1 && `${(val * 100).toFixed(0)}%`}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                {result.ai_confidence.ai_reasoning && (
                  <div>
                    <span className="text-gray-700 font-semibold block mb-1">AI Reasoning:</span>
                    <p className="text-gray-600 italic">{result.ai_confidence.ai_reasoning}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {result.reason_score && result.reason_score.max_bonus > 0 && (
            <div className="bg-gray-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
              <h3 className="text-lg font-bold text-gray-800 mb-2">Reasoning Breakdown</h3>
              {result.reason_score.correct.length > 0 && (
                <div className="mb-2">
                  <span className="text-green-600 font-semibold">✓ Correct:</span>
                  <ul className="ml-4 mt-1 space-y-0.5">
                    {result.reason_score.correct.map((r, i) => <li key={i} className="text-green-700 text-sm">{r}</li>)}
                  </ul>
                </div>
              )}
              {result.reason_score.incorrect.length > 0 && (
                <div className="mb-2">
                  <span className="text-red-600 font-semibold">✗ Incorrect:</span>
                  <ul className="ml-4 mt-1 space-y-0.5">
                    {result.reason_score.incorrect.map((r, i) => <li key={i} className="text-red-700 text-sm">{r}</li>)}
                  </ul>
                </div>
              )}
              {result.reason_score.missed.length > 0 && (
                <div>
                  <span className="text-orange-600 font-semibold">⚠ Missed:</span>
                  <ul className="ml-4 mt-1 space-y-0.5">
                    {result.reason_score.missed.map((r, i) => <li key={i} className="text-orange-700 text-sm">{r}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-gray-800"><strong className="text-blue-700">Correct Answer:</strong> {result.correct_answer}</p>
          </div>
        </div>
        
        <div className="p-6 border-t border-gray-200">
          <button 
            onClick={onNext}
            className="w-full bg-principal-blue hover:bg-blue-400 text-black font-bold py-4 rounded-lg transition-colors shadow-lg text-xl"
          >
            Next Scenario
          </button>
        </div>
      </div>
    </div>
  );
}

export default FeedbackModal;
