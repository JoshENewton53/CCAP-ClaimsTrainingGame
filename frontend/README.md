# Frontend - React Application

React frontend for the CCAP Claims Training Game with authentication, game interface, and achievements.

## Features

- **Authentication**: Login and registration screens
- **Game Interface**: Interactive claim scenario evaluation
- **Achievements System**: View unlocked and locked achievements
- **Score Tracking**: Real-time score and streak display
- **Client Profile**: View client information and policy details
- **Code Reference**: Search and match procedure/diagnosis codes
- **Policy Guide**: Reference policy rules by claim type
- **Responsive Design**: Black and blue themed UI with Principal branding

## Components

- `App.js` - Main application with authentication flow
- `Login.js` - Login/registration form
- `StartGame.js` - Claim type and difficulty selection
- `GameScreen.js` - Main game interface with scenario display
- `FeedbackModal.js` - Answer feedback and achievement notifications
- `Achievements.js` - Achievement gallery modal
- `ClientProfile.js` - Client information sidebar
- `PolicyGuide.js` - Policy rules reference
- `CodeMatcher.js` - Code reference lookup tool

## Setup

```bash
cd frontend
npm install
npm start
```

App runs on `http://localhost:3000`

## API Integration

The frontend communicates with the backend API at `http://localhost:5000`:
- Authentication endpoints for login/register
- Scenario generation and submission
- Achievement retrieval

## Styling

- Black and blue gradient theme
- White text for readability
- Cyan (`#00d4ff`) accent color
- Principal logo in header
- Responsive design for mobile and desktop
