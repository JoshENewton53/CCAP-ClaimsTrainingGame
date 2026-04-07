import React, { useState, useEffect } from 'react';
import './Account.css';
import API_BASE from './config';

function Account({ user, onClose, onUpdate }) {
  const [bio, setBio] = useState('');
  const [profilePicture, setProfilePicture] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [performance, setPerformance] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/profile`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setBio(data.bio || '');
        if (data.profile_picture) setPreviewUrl(`data:image/jpeg;base64,${data.profile_picture}`);
      })
      .catch(err => console.error(err));

    fetch(`${API_BASE}/api/ai/performance`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setPerformance(data))
      .catch(err => console.error(err));
  }, []);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfilePicture(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('bio', bio);
    if (profilePicture) {
      formData.append('profile_picture', profilePicture);
    }

    try {
      const response = await fetch(`${API_BASE}/api/profile/update`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      
      if (response.ok) {
        alert('Profile updated successfully!');
        onUpdate();
      } else {
        alert('Failed to update profile');
      }
    } catch (err) {
      console.error(err);
      alert('Error updating profile');
    } finally {
      setLoading(false);
    }
  };

  const xpToNextLevel = ((user.level || 1) * 100);
  const currentLevelXp = (user.xp || 0) % 100;
  const xpProgress = (currentLevelXp / 100) * 100;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-principal-dark rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-principal-blue/30" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-gradient-to-r from-principal-dark to-principal-darker p-6 border-b border-principal-blue/30">
          <h2 className="text-3xl font-bold text-white text-center">👤 Account</h2>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Profile Picture */}
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-700 border-4 border-principal-blue mb-4">
              {previewUrl ? (
                <img src={previewUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-6xl text-gray-400">
                  👤
                </div>
              )}
            </div>
            <label className="bg-principal-blue hover:bg-blue-400 text-black px-4 py-2 rounded-lg font-semibold cursor-pointer transition-colors">
              Upload Picture
              <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
            </label>
          </div>

          {/* User Stats */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-principal-blue/30">
            <h3 className="text-xl font-bold text-principal-blue mb-3">Stats</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-gray-400 text-sm">Username</div>
                <div className="text-white font-bold text-lg">{user.username}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Level</div>
                <div className="text-yellow-400 font-bold text-lg">{user.level || 1}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Score</div>
                <div className="text-principal-blue font-bold text-lg">{user.score}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Streak</div>
                <div className={`font-bold text-lg ${user.current_streak >= 0 ? 'text-principal-blue' : 'text-red-400'}`}>
                  {user.current_streak}
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="text-gray-400 text-sm mb-2">XP Progress</div>
              <div className="w-full h-4 bg-gray-700 rounded-full overflow-hidden border border-green-400/30">
                <div 
                  className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-500"
                  style={{ width: `${xpProgress}%` }}
                />
              </div>
              <div className="text-green-400 text-sm mt-1">{currentLevelXp} / 100 XP</div>
            </div>
          </div>

          {/* Bio */}
          <div className="bg-gray-800/50 rounded-lg p-4 border border-principal-blue/30">
            <h3 className="text-xl font-bold text-principal-blue mb-3">Bio</h3>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell us about yourself..."
              className="w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600 focus:border-principal-blue focus:outline-none resize-none"
              rows="4"
              maxLength="500"
            />
            <div className="text-gray-400 text-sm mt-1">{bio.length}/500 characters</div>
          </div>

          {/* AI Performance Report */}
          {performance && (
            <div className="bg-gray-800/50 rounded-lg p-4 border border-principal-blue/30">
              <h3 className="text-xl font-bold text-principal-blue mb-3">🤖 AI Performance Report</h3>
              {performance.total_attempts < 5 ? (
                <p className="text-gray-400 text-sm">Complete at least 5 scenarios to unlock your personalized report.</p>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-gray-400 text-sm">Overall Accuracy</span>
                    <span className={`font-bold text-lg ${
                      performance.overall_accuracy >= 0.8 ? 'text-green-400' :
                      performance.overall_accuracy >= 0.6 ? 'text-yellow-400' : 'text-red-400'
                    }`}>{(performance.overall_accuracy * 100).toFixed(0)}%</span>
                  </div>
                  {performance.weak_areas.length > 0 && (
                    <div className="mb-2">
                      <div className="text-red-400 text-sm font-semibold mb-1">⚠ Needs Work</div>
                      {performance.weak_areas.map(area => (
                        <div key={area} className="text-gray-300 text-sm ml-2">• {area}</div>
                      ))}
                    </div>
                  )}
                  {performance.strong_areas.length > 0 && (
                    <div className="mb-2">
                      <div className="text-green-400 text-sm font-semibold mb-1">✓ Strong Areas</div>
                      {performance.strong_areas.map(area => (
                        <div key={area} className="text-gray-300 text-sm ml-2">• {area}</div>
                      ))}
                    </div>
                  )}
                  <div className="mt-3 p-3 bg-principal-blue/10 rounded-lg border border-principal-blue/20">
                    <p className="text-principal-blue text-sm">{performance.recommendation}</p>
                  </div>
                  {performance.ai_summary && (
                    <div className="mt-3 p-3 bg-indigo-900/30 rounded-lg border border-indigo-500/40">
                      <div className="text-indigo-300 text-xs font-semibold mb-1">
                        AI Study Plan (local Flan-T5 model)
                      </div>
                      <p className="text-indigo-100 text-sm whitespace-pre-line">
                        {performance.ai_summary}
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={loading}
            className="w-full bg-principal-blue hover:bg-blue-400 disabled:bg-gray-600 text-black font-bold py-3 rounded-lg transition-colors shadow-lg"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
        
        <div className="sticky bottom-0 bg-principal-dark p-6 border-t border-principal-blue/30">
          <button 
            onClick={onClose}
            className="w-full bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default Account;
