import React, { useEffect, useState } from 'react';
import './AdminDashboard.css';
import API_BASE from './config';

const CLAIM_TYPES = ['medical', 'dental', 'life'];
const DIFFICULTIES = ['easy', 'medium', 'hard'];

function AccuracyBar({ value, color = 'bg-principal-blue' }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-gray-300 w-10 text-right">{value}%</span>
    </div>
  );
}

function TraineeRow({ trainee, onClick, selected }) {
  const accuracyColor =
    trainee.accuracy >= 75 ? 'text-green-400' :
    trainee.accuracy >= 50 ? 'text-yellow-400' : 'text-red-400';

  return (
    <tr
      className={`border-b border-gray-700 cursor-pointer transition-colors ${selected ? 'bg-principal-blue/20' : 'hover:bg-gray-800'}`}
      onClick={onClick}
    >
      <td className="py-3 px-4 text-white font-semibold">{trainee.username}</td>
      <td className="py-3 px-4 text-white">{trainee.score}</td>
      <td className="py-3 px-4 text-yellow-400 font-bold">Lv {trainee.level}</td>
      <td className="py-3 px-4 text-gray-300">{trainee.total_attempts}</td>
      <td className={`py-3 px-4 font-bold ${accuracyColor}`}>{trainee.accuracy}%</td>
      <td className="py-3 px-4">
        {CLAIM_TYPES.map(t => (
          <span key={t} className="inline-block mr-2 text-xs text-gray-400">
            {t[0].toUpperCase()}: <span className="text-white">{trainee.by_type[t]?.accuracy ?? '—'}%</span>
          </span>
        ))}
      </td>
    </tr>
  );
}

const ANSWERS = ['valid', 'invalid', 'insufficient'];
const ANSWER_COLORS = { valid: 'bg-green-600', invalid: 'bg-red-600', insufficient: 'bg-yellow-500' };
const ANSWER_SHORT = { valid: 'Valid', invalid: 'Invalid', insufficient: 'Insuff.' };

function ConfusionMatrix({ confusion, totalAttempts, falseApprovalRate }) {
  if (!confusion || Object.keys(confusion).length === 0) {
    return <p className="text-gray-500 text-sm">No data yet.</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-principal-blue font-bold">Decision Confusion Matrix</h4>
        <span className={`text-xs font-bold px-2 py-1 rounded ${
          falseApprovalRate > 15 ? 'bg-red-500/20 text-red-400' :
          falseApprovalRate > 5  ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-green-500/20 text-green-400'
        }`}>
          False Approvals: {falseApprovalRate}%
        </span>
      </div>
      <p className="text-gray-500 text-xs mb-3">Rows = correct answer &nbsp;·&nbsp; Columns = what trainee answered</p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-gray-500 text-left pb-2 pr-2">Actual ↓ / Said →</th>
              {ANSWERS.map(a => (
                <th key={a} className="pb-2 px-2 text-center">
                  <span className={`px-2 py-0.5 rounded text-white font-bold ${ANSWER_COLORS[a]}`}>
                    {ANSWER_SHORT[a]}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ANSWERS.map(actual => {
              const row = confusion[actual] || {};
              const rowTotal = ANSWERS.reduce((s, a) => s + (row[a] || 0), 0);
              if (rowTotal === 0) return null;
              return (
                <tr key={actual} className="border-t border-gray-700">
                  <td className="py-2 pr-2">
                    <span className={`px-2 py-0.5 rounded text-white font-bold ${ANSWER_COLORS[actual]}`}>
                      {ANSWER_SHORT[actual]}
                    </span>
                    <span className="text-gray-500 ml-1">({rowTotal})</span>
                  </td>
                  {ANSWERS.map(predicted => {
                    const count = row[predicted] || 0;
                    const pct = rowTotal ? Math.round(count / rowTotal * 100) : 0;
                    const isCorrect = predicted === actual;
                    const isDangerous = actual !== 'valid' && predicted === 'valid' && count > 0;
                    return (
                      <td key={predicted} className="py-2 px-2 text-center">
                        <div className={`rounded px-2 py-1 font-bold ${
                          isCorrect ? 'bg-green-900/50 text-green-300' :
                          isDangerous ? 'bg-red-900/60 text-red-300' :
                          count > 0 ? 'bg-gray-700 text-gray-300' : 'text-gray-600'
                        }`}>
                          {count > 0 ? `${count} (${pct}%)` : '—'}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TrendChart({ weeklyTrend }) {
  if (!weeklyTrend || weeklyTrend.length === 0) {
    return <p className="text-gray-500 text-sm">Not enough data for trend (need activity in last 8 weeks).</p>;
  }

  const W = 280, H = 80, PAD = 8;
  const points = weeklyTrend.map(w => w.accuracy);
  const maxVal = 100;
  const stepX = points.length > 1 ? (W - PAD * 2) / (points.length - 1) : W - PAD * 2;

  const toX = i => PAD + i * stepX;
  const toY = v => H - PAD - ((v / maxVal) * (H - PAD * 2));

  const polyline = points.map((v, i) => `${toX(i)},${toY(v)}`).join(' ');
  const areaPath = [
    `M ${toX(0)},${toY(points[0])}`,
    ...points.slice(1).map((v, i) => `L ${toX(i + 1)},${toY(v)}`),
    `L ${toX(points.length - 1)},${H - PAD}`,
    `L ${toX(0)},${H - PAD}`,
    'Z'
  ].join(' ');

  // Trend direction
  const first = points[0];
  const last = points[points.length - 1];
  const trendDiff = last - first;
  const trendLabel = trendDiff > 5 ? '↑ Improving' : trendDiff < -5 ? '↓ Declining' : '→ Stable';
  const trendColor = trendDiff > 5 ? 'text-green-400' : trendDiff < -5 ? 'text-red-400' : 'text-yellow-400';

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-principal-blue font-bold">Accuracy Trend (Last 8 Weeks)</h4>
        <span className={`text-xs font-bold ${trendColor}`}>{trendLabel}</span>
      </div>
      <svg width={W} height={H} className="w-full" viewBox={`0 0 ${W} ${H}`}>
        {/* Grid lines at 25, 50, 75, 100 */}
        {[25, 50, 75, 100].map(v => (
          <g key={v}>
            <line x1={PAD} y1={toY(v)} x2={W - PAD} y2={toY(v)}
              stroke="#374151" strokeWidth="1" strokeDasharray="3,3" />
            <text x={PAD - 2} y={toY(v) + 3} fill="#6b7280" fontSize="8" textAnchor="end">{v}</text>
          </g>
        ))}
        {/* Area fill */}
        <path d={areaPath} fill="#3b82f620" />
        {/* Line */}
        <polyline points={polyline} fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinejoin="round" />
        {/* Dots */}
        {points.map((v, i) => (
          <circle key={i} cx={toX(i)} cy={toY(v)} r="3"
            fill={v >= 75 ? '#22c55e' : v >= 50 ? '#eab308' : '#ef4444'}
            stroke="#111" strokeWidth="1"
          />
        ))}
      </svg>
      {/* Week labels */}
      <div className="flex justify-between mt-1">
        {weeklyTrend.map((w, i) => (
          <span key={i} className="text-gray-600 text-xs" style={{ fontSize: '9px' }}>
            {w.week.slice(5)}
          </span>
        ))}
      </div>
    </div>
  );
}

function TraineeDetail({ trainee }) {
  if (!trainee) return null;

  const streakColor = trainee.current_streak >= 0 ? 'text-green-400' : 'text-red-400';

  return (
    <div className="bg-gray-900 border border-principal-blue/30 rounded-xl p-6 space-y-6 overflow-y-auto max-h-[85vh]">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-white">{trainee.username}</h3>
        <span className="bg-yellow-500 text-black px-3 py-1 rounded-lg font-bold">Level {trainee.level}</span>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'Score', value: trainee.score, color: 'text-principal-blue' },
          { label: 'Attempts', value: trainee.total_attempts, color: 'text-white' },
          { label: 'Correct', value: trainee.total_correct, color: 'text-green-400' },
          { label: 'Streak', value: trainee.current_streak, color: streakColor },
        ].map(s => (
          <div key={s.label} className="bg-gray-800 rounded-lg p-3 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-gray-400 text-xs mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Overall accuracy */}
      <div>
        <div className="flex justify-between mb-1">
          <span className="text-gray-300 font-semibold">Overall Accuracy</span>
          <span className="text-white font-bold">{trainee.accuracy}%</span>
        </div>
        <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${trainee.accuracy >= 75 ? 'bg-green-500' : trainee.accuracy >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${trainee.accuracy}%` }}
          />
        </div>
      </div>

      {/* Accuracy trend chart */}
      <div className="bg-gray-800 rounded-lg p-4">
        <TrendChart weeklyTrend={trainee.weekly_trend} />
      </div>

      {/* Confusion matrix */}
      <div className="bg-gray-800 rounded-lg p-4">
        <ConfusionMatrix
          confusion={trainee.confusion}
          totalAttempts={trainee.total_attempts}
          falseApprovalRate={trainee.false_approval_rate}
        />
      </div>

      {/* By claim type */}
      <div>
        <h4 className="text-principal-blue font-bold mb-3">Accuracy by Claim Type</h4>
        <div className="space-y-3">
          {CLAIM_TYPES.map(t => {
            const data = trainee.by_type[t];
            if (!data) return (
              <div key={t} className="flex items-center gap-3">
                <span className="w-16 text-gray-500 capitalize text-sm">{t}</span>
                <span className="text-gray-600 text-sm">No attempts</span>
              </div>
            );
            return (
              <div key={t}>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-300 capitalize text-sm">{t} <span className="text-gray-500">({data.total} attempts)</span></span>
                </div>
                <AccuracyBar
                  value={data.accuracy}
                  color={data.accuracy >= 75 ? 'bg-green-500' : data.accuracy >= 50 ? 'bg-yellow-500' : 'bg-red-500'}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* By difficulty */}
      <div>
        <h4 className="text-principal-blue font-bold mb-3">Accuracy by Difficulty</h4>
        <div className="space-y-3">
          {DIFFICULTIES.map(d => {
            const data = trainee.by_difficulty[d];
            const colors = { easy: 'bg-green-500', medium: 'bg-yellow-500', hard: 'bg-red-500' };
            if (!data) return (
              <div key={d} className="flex items-center gap-3">
                <span className="w-16 text-gray-500 capitalize text-sm">{d}</span>
                <span className="text-gray-600 text-sm">No attempts</span>
              </div>
            );
            return (
              <div key={d}>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-300 capitalize text-sm">{d} <span className="text-gray-500">({data.total} attempts)</span></span>
                </div>
                <AccuracyBar value={data.accuracy} color={colors[d]} />
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent activity */}
      {trainee.recent_activity.length > 0 && (
        <div>
          <h4 className="text-principal-blue font-bold mb-3">Recent Activity</h4>
          <div className="space-y-2">
            {trainee.recent_activity.map((a, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2 text-sm">
                <span className="capitalize text-gray-300">{a.claim_type} / {a.difficulty}</span>
                <span className={a.is_correct ? 'text-green-400 font-bold' : 'text-red-400 font-bold'}>
                  {a.is_correct ? '✓' : '✗'}
                </span>
                <span className={`font-semibold ${a.points_earned >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {a.points_earned >= 0 ? '+' : ''}{a.points_earned} pts
                </span>
                <span className="text-gray-500 text-xs">{new Date(a.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryCards({ trainees }) {
  const total = trainees.length;
  const avgScore = total ? Math.round(trainees.reduce((s, t) => s + t.score, 0) / total) : 0;
  const avgAccuracy = total ? Math.round(trainees.reduce((s, t) => s + t.accuracy, 0) / total) : 0;
  const totalAttempts = trainees.reduce((s, t) => s + t.total_attempts, 0);

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {[
        { label: 'Total Trainees', value: total, color: 'text-principal-blue' },
        { label: 'Avg Score', value: avgScore, color: 'text-white' },
        { label: 'Avg Accuracy', value: `${avgAccuracy}%`, color: avgAccuracy >= 70 ? 'text-green-400' : 'text-yellow-400' },
        { label: 'Total Attempts', value: totalAttempts, color: 'text-purple-400' },
      ].map(c => (
        <div key={c.label} className="bg-gray-900 border border-principal-blue/20 rounded-xl p-4 text-center">
          <div className={`text-3xl font-bold ${c.color}`}>{c.value}</div>
          <div className="text-gray-400 text-sm mt-1">{c.label}</div>
        </div>
      ))}
    </div>
  );
}

export default function AdminDashboard({ onLogout }) {
  const [trainees, setTrainees] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('score');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetch(`${API_BASE}/api/admin/stats`, { credentials: 'include' })
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(d => { setTrainees(d.trainees); setLoading(false); })
      .catch(e => { setError(String(e)); setLoading(false); });
  }, []);

  const sorted = [...trainees]
    .filter(t => t.username.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'score') return b.score - a.score;
      if (sortBy === 'accuracy') return b.accuracy - a.accuracy;
      if (sortBy === 'attempts') return b.total_attempts - a.total_attempts;
      if (sortBy === 'level') return b.level - a.level;
      return 0;
    });

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-principal-dark to-principal-darker">
      {/* Header */}
      <header className="border-b border-principal-blue/30 bg-black/50 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img src="/PrincipalLogo3.png" alt="Principal" className="h-10 w-auto" />
          <div>
            <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-gray-400 text-sm">Trainee Performance Overview</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg font-semibold transition-colors"
        >
          Logout
        </button>
      </header>

      <div className="p-8">
        {loading && <p className="text-gray-400 text-center mt-20">Loading trainee data...</p>}
        {error && <p className="text-red-400 text-center mt-20">Error: {error}</p>}

        {!loading && !error && (
          <>
            <SummaryCards trainees={trainees} />

            <div className="flex gap-8">
              {/* Left: trainee table */}
              <div className="flex-1 min-w-0">
                {/* Controls */}
                <div className="flex items-center gap-4 mb-4">
                  <input
                    type="text"
                    placeholder="Search trainee..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="bg-gray-800 border border-gray-600 text-white rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-principal-blue w-48"
                  />
                  <span className="text-gray-400 text-sm">Sort by:</span>
                  {['score', 'accuracy', 'attempts', 'level'].map(s => (
                    <button
                      key={s}
                      onClick={() => setSortBy(s)}
                      className={`px-3 py-1 rounded-lg text-sm font-semibold capitalize transition-colors ${sortBy === s ? 'bg-principal-blue text-black' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                      {s}
                    </button>
                  ))}
                </div>

                <div className="bg-gray-900 border border-principal-blue/20 rounded-xl overflow-hidden">
                  {sorted.length === 0 ? (
                    <p className="text-gray-500 text-center py-12">No trainees found.</p>
                  ) : (
                    <table className="w-full">
                      <thead className="bg-gray-800 border-b border-gray-700">
                        <tr>
                          {['Username', 'Score', 'Level', 'Attempts', 'Accuracy', 'By Type'].map(h => (
                            <th key={h} className="py-3 px-4 text-left text-principal-blue font-semibold text-sm">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {sorted.map(t => (
                          <TraineeRow
                            key={t.username}
                            trainee={t}
                            selected={selected?.username === t.username}
                            onClick={() => setSelected(selected?.username === t.username ? null : t)}
                          />
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>

              {/* Right: detail panel */}
              {selected && (
                <div className="w-96 shrink-0">
                  <TraineeDetail trainee={selected} />
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
