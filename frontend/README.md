# Frontend - React Application

React frontend for the CCAP Claims Training Game with authentication, game interface, and achievements.

## Features

- **Authentication**: Login and registration screens
- **Game Interface**: Interactive claim scenario evaluation
- **Achievements System**: 17 unlockable achievement badges
- **Score Tracking**: Real-time score, XP, level, and streak display
- **Client Profile**: View client information and policy details including exclusions and dependents
- **Code Reference**: Search and match procedure/diagnosis codes
- **Policy Guide**: Reference policy rules by claim type
- **Death Certificate Review**: Life insurance mode — review generated PDF death certs and identify errors
- **Leaderboard**: Top 100 users ranked by score
- **Account Page**: User profile with XP bar, level, bio, and AI-generated performance report
- **Admin Dashboard**: Trainee roster, accuracy rates, and confusion matrix (Admin1 only)
- **Onboarding**: Tutorial intro screen on first login
- **Responsive Design**: Black and blue themed UI with Principal branding

## Components

- `App.js` - Main application routing and authentication flow
- `Login.js` - Login/registration form
- `StartGame.js` - Claim type and difficulty selection
- `GameScreen.js` - Main game interface with scenario display and verdict submission
- `FeedbackModal.js` - Answer feedback and achievement notifications
- `ReasonModal.js` - Reason selection when marking a claim Invalid or Insufficient
- `Achievements.js` - Achievement gallery modal
- `ClientProfile.js` - Client information sidebar (name, policy, coverage, exclusions, dependents)
- `PolicyGuide.js` - Policy rules reference
- `CodeMatcher.js` - Code reference lookup tool
- `DeathCertificateReview.js` - Life insurance PDF review with error checklist
- `Account.js` - User profile, XP bar, level, and AI performance report
- `Leaderboard.js` - Top 100 users ranking table
- `AdminDashboard.js` - Admin-only analytics and trainee performance dashboard
- `IntroPage.js` - Onboarding tutorial shown on first login

## Setup

```bash
cd frontend
npm install
npm start
```

App runs on `http://localhost:3000`

## API Integration

The frontend communicates with the backend API at `http://localhost:5000` (configurable via `REACT_APP_API_URL`). Key endpoints used:
- Authentication: login, register, logout, session check
- Scenario generation and submission
- Profile get/update
- Achievements retrieval
- Leaderboard
- Death certificate generate, validate, and error options
- AI hints (`/api/ai/hint`)
- Admin stats (`/api/admin/stats`)

## Styling

- Black and blue gradient theme
- White text for readability
- Cyan (`#00d4ff`) accent color
- Principal logo in header
- Responsive design for mobile and desktop
