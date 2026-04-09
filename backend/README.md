# Backend - Flask API

Flask backend for the CCAP Claims Training Game with authentication, game logic, and AI integration.

## Features

- **Authentication API**: User registration, login, logout, and session management
- **Game API**: Scenario generation and answer submission
- **Achievements API**: Track and retrieve user achievements
- **Leaderboard**: Top 100 users ranked by score
- **Profile API**: User profile, bio, and stats management
- **Death Certificate API**: Life insurance PDF scenario generation and validation
- **AI Hints**: Progressive hint system via Claude API
- **Database**: SQLite with users, scenarios, attempts, and achievements tables
- **AI Integration**: Claude API for narrative generation and feedback; XGBoost for claim classification
- **Itemized Bill Generation**: Realistic bills with trainable errors — upcoding, unbundling, amount mismatch, and date errors (medical/dental)
- **Policy-Level Errors**: Trainable invalid scenarios — lapsed policy, late filing, exclusions, and coverage mismatch

## API Endpoints

### Health
- `GET /api/health` - Health check

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/me` - Get current user info

### Game
- `POST /api/scenario/generate` - Generate new claim scenario
- `POST /api/scenario/submit` - Submit answer and get feedback
- `GET /api/reference/codes` - Get reference code mappings

### Profile
- `GET /api/profile` - Get current user's profile and stats
- `POST /api/profile/update` - Update bio or profile picture

### Achievements & Leaderboard
- `GET /api/achievements` - Get all achievements with unlock status
- `GET /api/leaderboard` - Get top 100 users ranked by score

### Death Certificate (Life Insurance)
- `POST /api/death-certificate/generate` - Generate a life insurance death certificate scenario
- `POST /api/death-certificate/validate` - Validate the user's error checklist submission
- `GET /api/death-certificate/error-options` - Get available checklist options

### AI
- `POST /api/ai/hint` - Get a progressive hint for the current scenario
- `GET /api/ai/performance` - Get AI model performance metrics
- `GET /api/ai/test-flan` - Test Flan-T5 model availability

### Admin
- `GET /api/admin/stats` - Get trainee roster, accuracy rates, and confusion matrix (Admin1 only)

## Setup

```bash
cd backend
pip install -r requirements.txt
python init_db.py
python app.py
```

Server runs on `http://localhost:5000`

## Database Schema

### users
- id, username, password_hash, score, current_streak, xp, level, bio, profile_picture

### scenarios
- id, claim_type, difficulty, scenario_json, correct_answer, created_at

### attempts
- id, user_id, scenario_id, user_answer, is_correct, feedback_text, points_earned, created_at

### achievements
- id, user_id, achievement_key, unlocked_at

## Configuration

- Database: `data.db` (SQLite)
- Secret Key: Auto-generated on startup
- CORS: Enabled for frontend communication
