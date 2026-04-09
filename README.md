# CCAP Claims Training Game

An interactive training application for insurance claims processing with user authentication, achievements, and AI-powered scenario generation.

## Features

- **User Authentication**: Login/registration system with persistent user accounts
- **Score Tracking**: Scores, XP, and levels saved to the database and persist across sessions
- **Achievements System**: 17 unlockable achievements based on performance milestones
- **Streak Counter**: Track consecutive correct answers
- **AI-Powered Scenarios**: Claude API generates realistic claim narratives and educational feedback
- **Multiple Claim Types**: Medical, Dental, and Life Insurance claims
- **Difficulty Levels**: Easy, Medium, and Hard scenarios with varying point values and error injection
- **Death Certificate Review**: Life insurance mode with generated PDF death certificates and error identification
- **Itemized Bill Errors**: Trainable billing errors — upcoding, unbundling, amount mismatch, date errors
- **Policy-Level Errors**: Trainable invalid scenarios — lapsed policy, late filing, exclusions, coverage mismatch
- **Progressive Hints**: AI hint system provides increasingly specific clues without revealing the answer
- **Leaderboard**: Top 100 users ranked by score
- **Admin Dashboard**: Trainee roster, accuracy rates, false approval rate, and confusion matrix
- **Interactive UI**: Black and blue themed interface with Principal branding

## Project Structure

- **frontend/**: React application with user interface
- **backend/**: Flask API with authentication and game logic
- **ai_models/**: AI model training scripts (models not included - see MODEL_SETUP.md)
- **datasets/**: Insurance claims datasets for training

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js and npm
- (Optional) Docker and Docker Compose

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

### Option 2: Manual Setup

See [RUNNING.md](RUNNING.md) for detailed instructions.

## Default Admin Account

- **Username**: Admin1
- **Password**: Password

## AI Models

AI models are not included in this repository due to file size constraints. See [MODEL_SETUP.md](MODEL_SETUP.md) for instructions on training or obtaining models.

## Documentation

- [Running the Application](RUNNING.md)
- [Application Summary](APP_SUMMARY.md)
- [AI Model Setup](MODEL_SETUP.md)
- [AI Usage and Validation](AI_USAGE_AND_VALIDATION.md)
- [Death Certificate Feature](DEATH_CERT_FEATURE.md)
- [Backend API](backend/README.md)
- [Frontend](frontend/README.md)
