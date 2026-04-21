# CCAP Claims Training Game

A gamified, interactive training application for insurance claims processors. Built for Principal insurance, it simulates real-world claim evaluation scenarios to help trainees correctly classify claims as **Valid**, **Invalid**, or **Insufficient**. Game mechanics — scoring, levels, achievements, streaks, and leaderboards — make the training experience engaging and competitive.

---

## Features

### Core Game Loop
- **Three Claim Types**: Medical, Dental, and Life Insurance scenarios
- **Three Difficulty Levels**: Easy, Medium, and Hard with scaling point values and error complexity
- **Verdict System**: Users classify each claim as Valid, Invalid, or Insufficient
- **Reason Selection**: When marking Invalid or Insufficient, users select specific reasons from a structured list
- **Score Tracking**: Points, XP, and levels persist across sessions via SQLite

### AI-Powered Features
- **Claim Narrative Generation**: Claude AI writes a unique 2–3 sentence patient story for every scenario
- **Physician Notes**: Claude generates SOAP-format clinical notes; on hard difficulty, subtle discrepancies are embedded for analysts to catch
- **Medical Records**: Claude generates patient history summaries with optional pre-existing condition flags on hard cases
- **Educational Feedback**: After each submission, Claude generates 3–4 sentences of tailored instructional feedback
- **Progressive Hints**: Claude provides increasingly specific hints on request without revealing the answer
- **AI Confidence Scoring**: XGBoost classifier reports its probability distribution across all three verdict classes after submission
- **Performance Analytics**: AI-powered analysis of user attempt history identifies weak areas by claim type

### Billing and Document Review
- **Itemized Bill Errors**: Trainable billing errors — upcoding, unbundling, amount mismatch, date errors — injected probabilistically on Medium/Hard
- **Policy-Level Errors**: Trainable invalid scenarios — lapsed policy, late filing, exclusions, coverage mismatch
- **Document Status Panel**: Submitted and missing documents vary by difficulty
- **Code Reference Tool**: Interactive lookup for procedure and diagnosis code validation

### Life Insurance Mode
- **Death Certificate Review**: AI-generated PDF death certificates with up to 8 injected error types
- **Error Identification**: Users identify name mismatches, date inconsistencies, missing signatures, invalid cause codes, jurisdiction mismatches, and more

### Gamification
- **Achievements System**: 17 unlockable badges triggered by score milestones, level milestones, streak counts, and claim-type-specific goals
- **Streak Counter**: Tracks consecutive correct answers
- **Leaderboard**: Top 100 users ranked by total score
- **Levels and XP**: Every 100 XP earns a level

### Administration
- **Admin Dashboard**: Full trainee roster with accuracy rates, false approval rate, and a confusion matrix by verdict type
- **Per-Trainee Breakdowns**: Accuracy rates broken down by claim type for each user

---

## Tech Stack

### Frontend

| Technology | Version | Role |
|---|---|---|
| React | 18.2 | UI framework and component architecture |
| React Router DOM | 6.14 | Client-side routing |
| Axios | 1.4 | HTTP client for REST API communication |
| Tailwind CSS | 3.4 | Utility-first styling |
| Node.js (Alpine) | 18 | Build-time runtime (multi-stage Docker) |
| Nginx (Alpine) | latest | Production static file server with API proxy |

The frontend is pure JavaScript (no TypeScript). All component logic, state management, and API communication is handled in JavaScript. The API base URL is configurable via the `REACT_APP_API_URL` environment variable.

### Backend

| Technology | Version | Role |
|---|---|---|
| Flask | 3.1.2 | Web framework and REST API |
| Flask-CORS | 6.0.2 | Cross-origin request handling |
| Gunicorn | 23.0.0 | Production WSGI server (2 workers) |
| SQLite3 | stdlib | Persistent relational database |
| Anthropic Python SDK | ≥0.40.0 | Claude API client for all AI features |
| ReportLab | 4.4.10 | Programmatic PDF generation for death certificates |
| Pandas / NumPy | 2.3 | Data handling for scenario and bill generation |
| Python-dotenv | ≥1.0.0 | Environment variable management |

### AI and Machine Learning

| Component | Role |
|---|---|
| **Claude API** (`claude-haiku-4-5`) | Primary LLM — scenario narratives, physician notes, medical records, educational feedback, progressive hints |
| **XGBoost Classifier** | Trained claim classification model — determines the ground-truth correct answer and produces confidence scores |
| **Sentence Transformers** | Text embeddings used to build hybrid feature vectors during XGBoost training |
| **scikit-learn** | LabelEncoder for categorical features, evaluation metrics |

### Deployment

| Component | Role |
|---|---|
| Docker | Containerizes both backend and frontend services |
| Docker Compose | Orchestrates `ccap_backend` (port 5000) and `ccap_frontend` (port 80) |
| Nginx | Serves static React build and proxies `/api/` requests to the Flask backend |
| AWS | Production hosting — EC2 instance running Docker Compose |

---

## Claude API Integration

The application uses `claude-haiku-4-5` via the Anthropic Python SDK. The Claude client is lazy-initialized on first use and reused for all requests. All Claude features degrade gracefully: if the API key is missing or a call fails, the app falls back to rule-based generation and hardcoded feedback.

### What Claude generates per scenario

| Feature | Claude call | Prompt inputs |
|---|---|---|
| Claim narrative | `generate_claim_story()` | Claim type, procedure, diagnosis, patient name, age, difficulty |
| Physician notes | `generate_physician_notes()` | Above + optional discrepancy instruction on hard/invalid cases |
| Medical records | `generate_medical_record()` | Above + optional pre-existing condition instruction on hard/invalid cases |
| Educational feedback | `generate_claim_feedback()` | Full scenario data + user answer + correct answer + rule explanation |
| Progressive hints | `generate_ai_hint()` | Hidden scenario fields (DOB, injury date, code mappings) not shown to the user |

### Hint progression
The first hint request returns a vague directional pointer (e.g., "Look carefully at the patient's date of birth in the Client Profile"). Each subsequent request becomes more specific with actual values from the scenario. The answer itself is never stated.

### Fallback behavior
- No `ANTHROPIC_API_KEY` or API failure → narrative uses rule-based generation; feedback uses rule explanation string directly
- XGBoost classifier missing → `classify_with_rules()` uses difficulty-based heuristics
- Death certificate PDF failure → UI displays a warning and continues without the certificate
- Itemized bill failure → UI displays a warning and continues without the bill

---

## AWS Deployment

The application is deployed on AWS using Docker Compose on an EC2 instance.

**Architecture:**
- EC2 instance runs `docker-compose up` to start both containers
- Nginx (port 80) serves the React static build and proxies `/api/*` requests to Flask (port 5000) within the Docker network
- `REACT_APP_API_URL` environment variable configures the frontend API base URL at build time
- `ANTHROPIC_API_KEY` environment variable is set on the EC2 instance for Claude API access

**Nginx proxy config (production):**
```nginx
location /api/ {
    proxy_pass http://backend:5000;
    proxy_read_timeout 120s;
}

location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}
```

To deploy an updated build:
```bash
docker-compose down
docker-compose up --build -d
```

---

## Project Structure

```
CCAP-ClaimsTraingGame/
├── frontend/                    # React application
│   ├── src/
│   │   ├── App.js               # Root component and routing
│   │   ├── GameScreen.js        # Core game loop
│   │   ├── AdminDashboard.js    # Admin analytics panel
│   │   ├── DeathCertificateReview.js
│   │   ├── ClientProfile.js     # Policyholder sidebar
│   │   ├── CodeMatcher.js       # Procedure/diagnosis code tool
│   │   ├── FeedbackModal.js     # Post-submission Claude feedback
│   │   ├── ReasonModal.js       # Reason selection for invalid/insufficient
│   │   ├── Achievements.js      # Achievement gallery
│   │   ├── Leaderboard.js
│   │   ├── Account.js           # User profile and AI performance report
│   │   └── config.js            # API base URL configuration
│   ├── Dockerfile               # Multi-stage: Node build → Nginx serve
│   └── nginx.conf               # API proxy configuration
├── backend/
│   ├── app.py                   # Flask app and all API endpoints
│   ├── claude_service.py        # Claude API integration
│   ├── ai_service.py            # XGBoost classifier and AI analytics
│   ├── death_certificate_service.py
│   ├── itemized_bill_service.py
│   ├── pdf_generator.py
│   ├── init_db.py               # Database initialization
│   ├── reference_data/          # Code mappings, required documents
│   ├── requirements.txt
│   └── Dockerfile
├── ai_models/                   # XGBoost training scripts (model not included)
├── datasets/                    # Training data for XGBoost classifier
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js and npm
- Docker and Docker Compose (recommended)
- Anthropic API key (for Claude-powered features)

### Option 1: Docker Compose (Recommended)

```bash
export ANTHROPIC_API_KEY=your-key-here
docker-compose up --build
```

The app will be available at `http://localhost`.

### Option 2: Manual Setup

See [RUNNING.md](RUNNING.md) for step-by-step local development instructions.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Recommended | Enables all Claude AI features. App falls back to rule-based logic if unset. |
| `REACT_APP_API_URL` | Optional | API base URL for the frontend. Defaults to empty string (same host). Set to the EC2 public URL for AWS deployments. |

---

## Default Admin Account

- **Username**: `Admin1`
- **Password**: `Password`

---

## Scoring

| Difficulty | Correct | Incorrect |
|---|---|---|
| Easy | +50 pts | -25 pts |
| Medium | +100 pts | -50 pts |
| Hard | +200 pts | -100 pts |

Levels: every 100 XP earns a level (Level = XP ÷ 100 + 1).

---

## AI Models

The XGBoost classifier is not included in this repository due to file size. See [MODEL_SETUP.md](MODEL_SETUP.md) for instructions on training or obtaining it. The application runs fully without it — rule-based fallback logic handles all claim classification automatically.

---

## Documentation

- [Running the Application](RUNNING.md)
- [Application Summary](APP_SUMMARY.md)
- [AI Model Setup](MODEL_SETUP.md)
- [AI Usage and Validation](AI_USAGE_AND_VALIDATION.md)
- [Death Certificate Feature](DEATH_CERT_FEATURE.md)
- [Backend API](backend/README.md)
