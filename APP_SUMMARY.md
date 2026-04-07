# CCAP Claims Training Game — Application Summary

## Overview

**CCAP Claims Training Game** is a gamified, interactive training application for insurance claims processors. Built for Principal insurance, it simulates real-world claim evaluation scenarios to help trainees learn to correctly classify insurance claims as **Valid**, **Invalid**, or **Insufficient**. Game mechanics — scoring, levels, achievements, streaks, and leaderboards — make the training experience engaging and competitive.

The app supports three insurance claim types:
- Medical Insurance
- Dental Insurance
- Life Insurance (with death certificate review)

---

## Technology Stack

### Frontend — JavaScript / Node.js / React

The frontend is **heavily JavaScript-based**, built entirely with React 18 and compiled via Node.js. There is no TypeScript — every component, hook, and utility is pure JavaScript.

| Technology | Role |
|------------|------|
| **React 18.2** | UI framework, component architecture |
| **React Router DOM 6.14** | Client-side routing between screens |
| **Axios 1.4** | HTTP client for all REST API communication |
| **Tailwind CSS 3.4** | Utility-first styling |
| **Node.js 18 (Alpine)** | Build-time runtime (multi-stage Docker) |
| **Nginx (Alpine)** | Production static file server |

The frontend spans roughly **1,900+ lines of JavaScript** across its components, with major files like `GameScreen.js` (~340 lines) and `AdminDashboard.js` (~461 lines).

### Backend — Python / Flask

The backend is a Python Flask REST API that handles all game logic, authentication, data persistence, and AI integration.

| Technology | Role |
|------------|------|
| **Flask 3.1.2** | Web framework and REST API |
| **SQLite3** | Lightweight relational database |
| **Gunicorn 23.0** | Production WSGI server (2 workers) |
| **Anthropic Claude API** | AI-generated claim narratives and feedback |
| **Flan-T5 (google/flan-t5-base)** | Local fallback model for feedback generation |
| **ReportLab 4.4** | PDF generation for death certificates |
| **Pandas / NumPy** | Data handling for scenario generation |
| **Python-dotenv** | Environment variable management |

### Deployment

- **Docker** — both services are containerized
- **Docker Compose** — orchestrates `ccap_backend` (port 5000) and `ccap_frontend` (port 80)
- **Database** — SQLite file at `backend/data.db`, auto-initialized on first run

---

## Key Screens and Components

| Component | Description |
|-----------|-------------|
| `Login.js` | User registration and login |
| `StartGame.js` | Select claim type (Medical/Dental/Life) and difficulty (Easy/Medium/Hard) |
| `GameScreen.js` | Core game loop — displays claim scenario, verdict buttons, streak counter |
| `ClientProfile.js` | Sidebar showing policyholder and policy details |
| `CodeMatcher.js` | Interactive lookup tool for procedure and diagnosis codes |
| `DeathCertificateReview.js` | Life insurance view — displays generated PDF death certificates with intentional errors |
| `FeedbackModal.js` | Post-submission feedback from Claude AI; shows newly earned achievements |
| `ReasonModal.js` | Prompts user to select specific reasons when marking a claim Invalid or Insufficient |
| `PolicyGuide.js` | Reference panel showing claim requirements by type |
| `Achievements.js` | Gallery of 17 unlockable achievement badges |
| `Account.js` | User profile with XP bar, level, bio, AI performance report |
| `Leaderboard.js` | Top 100 users ranked by score |
| `AdminDashboard.js` | Analytics dashboard for Admin1 — trainee roster, accuracy rates, confusion matrix |
| `IntroPage.js` | Tutorial/onboarding screen on first login |

---

## Game Mechanics

### Core Claim Evaluation Loop
1. User selects claim type and difficulty
2. Backend generates a realistic claim scenario (Claude AI writes the narrative)
3. Frontend displays claim details, document status, policy info
4. User selects: **Valid**, **Invalid**, or **Insufficient**
5. If Invalid/Insufficient, user selects specific reasons
6. Backend evaluates the answer and Claude AI generates educational feedback

### Scoring and Progression

| Difficulty | Correct | Incorrect |
|------------|---------|-----------|
| Easy | +50 pts | -25 pts |
| Medium | +100 pts | -50 pts |
| Hard | +200 pts | -100 pts |

- **Levels**: Every 100 XP earns a level (Level = XP ÷ 100 + 1)
- **Streaks**: Consecutive correct answers tracked
- **Achievements**: Unlock at score milestones, level milestones, streak counts, and claim-type-specific goals

### Difficulty Scaling
- **Easy**: 80–100% of required documents submitted; straightforward scenarios
- **Medium**: 60–80% of documents; minor discrepancies
- **Hard**: 40–70% of documents; intentional mismatches (wrong procedure codes, out-of-coverage dates, policy violations)

### Life Insurance / Death Certificate Validation
A specialized game mode where users review generated PDF death certificates and identify up to 8 error types: name mismatch, date inconsistency, missing signature, invalid cause code, jurisdiction mismatch, age mismatch, state mismatch, or expired certification.

---

## AI Integration

Claude AI (`claude-haiku-4-5`) is the primary AI engine powering two core features:

1. **Claim Narrative Generation** — Claude writes 2–3 paragraph realistic claim stories with patient/policyholder details, medical context, and scenario complexity matching the selected difficulty.
2. **Educational Feedback** — After each submission, Claude generates 3–4 sentences of tailored, instructional feedback explaining why the answer is correct or incorrect.

A local **Flan-T5** model serves as a graceful fallback if the Claude API is unavailable. Custom pickle-based ML models (`claim_classifier.pkl`, `scenario_generator`) handle claim classification and synthetic data generation.

---

## Authentication and Administration

- **Session-based auth** using Flask sessions and SHA-256 password hashing
- **Admin account** (`Admin1`) unlocks a dedicated analytics dashboard with:
  - Full trainee roster with accuracy percentages
  - Confusion matrix (correct vs. predicted verdicts)
  - False approval rate monitoring
  - Per-trainee performance breakdowns by claim type

---

## Frontend API Communication

The JavaScript frontend communicates with the Flask backend via RESTful HTTP using **Axios** for most requests and native `fetch()` for others. The API base URL is configurable via the `REACT_APP_API_URL` environment variable (default: `http://localhost:5000`). Authentication state is maintained via credentials-included session cookies.

Key endpoints include `/api/scenario/generate`, `/api/scenario/submit`, `/api/achievements`, `/api/leaderboard`, `/api/death-certificate/generate`, and `/api/ai/hint`.

---

## Summary

CCAP Claims Training Game is a full-stack educational platform that pairs a **React/JavaScript/Node.js frontend** with a Python Flask backend. The frontend is the dominant layer in terms of code volume and user interaction, relying entirely on JavaScript for all component logic, state management, and API communication. Claude AI provides the narrative intelligence that makes each training scenario feel realistic, while gamification mechanics keep trainees engaged and progressing.
