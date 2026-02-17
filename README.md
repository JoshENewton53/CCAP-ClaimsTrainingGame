# CCAP Claims Training Game

An interactive training application for insurance claims processing with user authentication, achievements, and AI-powered scenario generation.

## Features

- **User Authentication**: Login/registration system with persistent user accounts
- **Score Tracking**: User scores are saved to the database and persist across sessions
- **Achievements System**: Unlock achievements based on performance milestones
- **Streak Counter**: Track consecutive correct/incorrect answers
- **AI-Powered Scenarios**: Generate realistic insurance claim scenarios
- **Multiple Claim Types**: Medical, Dental, and Life insurance claims
- **Difficulty Levels**: Easy, Medium, and Hard scenarios with varying point values
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
- [AI Model Setup](MODEL_SETUP.md)
- [Backend API](backend/README.md)
- [Frontend](frontend/README.md)
