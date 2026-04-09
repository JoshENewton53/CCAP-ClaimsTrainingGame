# RUNNING THE CCAP CLAIMS TRAINING GAME

## Overview
This guide shows how to install and run the project locally with backend and frontend development servers.

## Prerequisites
- Python 3.10+ (3.11 recommended)
- Node.js and npm
- (Optional) Docker and Docker Compose

## Backend Setup (Flask)

### 1. Create and activate virtual environment

**Windows PowerShell:**
```powershell
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

This creates `data.db` with all required tables and the admin account:

```bash
python init_db.py
```

**Default Admin Account:**
- Username: `Admin1`
- Password: `Password`

### 4. Run the backend server

```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Frontend Setup (React)

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run the development server

```bash
npm start
```

The frontend will run on `http://localhost:3000` and automatically proxy API requests to the backend.

## Docker Compose (Alternative)

Run both backend and frontend with Docker:

```bash
docker-compose up --build
```

## AI Models Setup

The XGBoost classifier is not included in the repository due to file size. See [MODEL_SETUP.md](MODEL_SETUP.md) for instructions on:
- Training the classifier yourself
- Obtaining pre-trained models
- Running without AI models (the app falls back to rule-based logic automatically)

## Anthropic API Key

The app uses the Claude API for scenario narrative generation and feedback. To enable it, set the `ANTHROPIC_API_KEY` environment variable before starting the backend:

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Alternatively, create a `backend/.env` file:
```
ANTHROPIC_API_KEY=your-key-here
```

If the key is not set, the app will fall back to rule-based scenario generation.

## Database Management

### Reset Database

To reset the database (deletes all users, scores, and achievements):

```bash
cd backend
del data.db  # Windows
rm data.db   # Mac/Linux
python init_db.py
```

### View Database

Use any SQLite browser or:

```bash
sqlite3 backend/data.db
.tables
SELECT * FROM users;
```

## Troubleshooting

### PowerShell Execution Policy Error

Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 5000 Already in Use

Change the port in `backend/app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### CORS Errors

Ensure the backend is running and the frontend proxy is configured correctly in `frontend/package.json`.

### Missing AI Models

If the XGBoost classifier is missing, the app automatically falls back to rule-based claim classification. See [MODEL_SETUP.md](MODEL_SETUP.md) for model setup instructions.

## Key Files

- Backend API: `backend/app.py`
- Database Init: `backend/init_db.py`
- Frontend Entry: `frontend/src/App.js`
- Authentication: `frontend/src/Login.js`
- Achievements: `frontend/src/Achievements.js`
