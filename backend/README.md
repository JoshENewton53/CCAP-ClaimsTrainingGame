# Backend - Flask API

Flask backend for the CCAP Claims Training Game with authentication, game logic, and AI integration.

## Features

- **Authentication API**: User registration, login, logout, and session management
- **Game API**: Scenario generation and answer submission
- **Achievements API**: Track and retrieve user achievements
- **Database**: SQLite with users, scenarios, attempts, and achievements tables
- **AI Integration**: Interfaces with AI models for scenario generation and classification

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/me` - Get current user info

### Game
- `POST /api/scenario/generate` - Generate new claim scenario
- `POST /api/scenario/submit` - Submit answer and get feedback
- `GET /api/reference/codes` - Get reference code mappings

### Achievements
- `GET /api/achievements` - Get all achievements with unlock status

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
- id, username, password_hash, score, current_streak

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
