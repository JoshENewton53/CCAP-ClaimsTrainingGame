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
          {result.reason_bonus > 0 && (
            <p className="text-yellow-300 font-bold text-lg mt-2">🎉 Bonus: +{result.reason_bonus} points for reasoning!</p>
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
                <div>
                  <span className="text-gray-700 font-semibold">AI Confidence:</span>
                  <span className="text-indigo-900 font-bold ml-2 text-lg">
                    {(result.ai_confidence.confidence * 100).toFixed(1)}%
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
