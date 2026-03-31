import React from 'react';

export default function IntroPage({ onContinue }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-principal-dark to-principal-darker flex items-center justify-center p-6">
      <div className="bg-principal-dark border border-principal-blue/40 rounded-xl shadow-2xl p-8 max-w-4xl text-white">
        <h1 className="text-4xl font-bold mb-4">Welcome to Claims Training Buddy</h1>
        <p className="text-lg text-gray-200 mb-4">
          This game helps you practice insurance claim triage and verification using realistic scenarios.
          You will read short claim notes, extract critical procedure/diagnosis categories, and decide if the claim is valid,
          invalid, or insufficient.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-2">What it was made to do</h2>
        <ul className="list-disc pl-5 text-gray-200 space-y-2">
          <li>Build familiarity with procedural and diagnostic mapping for medical claims.</li>
          <li>Strengthen decision-making under common red-flag conditions.</li>
          <li>Provide an engaging score/streak/xp progression to track improvement.</li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-2">How to play</h2>
        <ol className="list-decimal pl-5 text-gray-200 space-y-2">
          <li>Select a claim type and difficulty from the Start Game panel.</li>
          <li>Review the claim details and submitted documents.</li>
          <li>Choose claim outcome: Valid, Invalid, or Insufficient Info.</li>
          <li>Submit and review feedback, score, and achievements; then move to the next scenario.</li>
        </ol>

        <div className="mt-8">
          <button
            onClick={onContinue}
            className="bg-lime-500 hover:bg-lime-400 text-black font-bold px-6 py-3 rounded-lg shadow-lg transition-colors"
          >
            Got it, let's play
          </button>
        </div>
      </div>
    </div>
  );
}
