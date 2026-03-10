# CCAP Claims Training Game - Midterm Presentation
**Date**: Thursday, February 26, 2024  
**Time**: 2:00–3:15 PM  
**Presenter**: Josh Newton

---

## 1. Project Overview (2 minutes)

### What is it?
An interactive web-based training application for insurance claims processing that combines gamification with AI-powered scenario generation.

### Target Users
- New insurance claims processors
- Training departments at insurance companies
- Claims processing teams needing skill refreshers

### Core Value Proposition
Transforms dry insurance training into an engaging, game-like experience with immediate feedback and achievement tracking.

---

## 2. Current Features - What's Working (3 minutes)

### ✅ Completed Features

**User Authentication System**
- Login and registration functionality
- Persistent user accounts stored in database
- Session management

**Game Mechanics**
- Multiple claim types: Medical, Dental, Life insurance
- Three difficulty levels (Easy, Medium, Hard)
- Point system with varying rewards
- Streak counter for consecutive answers
- Score tracking across sessions

**Achievements System**
- Performance-based milestone unlocking
- Visual achievement badges
- Progress tracking

**AI Integration**
- AI-powered scenario generation
- Realistic insurance claim scenarios
- Dynamic content creation

**User Interface**
- Black and blue themed design with Principal branding
- Responsive React frontend
- Interactive game flow

**Backend Infrastructure**
- Flask REST API
- Database persistence
- User data management

---

## 3. Live Demonstration (5-7 minutes)

### Demo Script

**Part 1: User Authentication**
1. Show registration page
2. Create a new user account
3. Log in with credentials
4. Show persistent session

**Part 2: Game Flow**
1. Select claim type (Medical/Dental/Life)
2. Choose difficulty level
3. Display AI-generated scenario
4. Make claim decision (Approve/Deny)
5. Show immediate feedback
6. Display score update

**Part 3: Progress Tracking**
1. Show current score
2. Display streak counter
3. Demonstrate achievement unlocking
4. Show score persistence (logout/login)

**Part 4: Multiple Scenarios**
1. Play through 2-3 different scenarios
2. Show variety in claim types
3. Demonstrate difficulty differences

### Demo Backup Plan
- Screenshots prepared in case of technical issues
- Video recording as fallback
- Local environment ready (not dependent on network)

---

## 4. Technical Architecture (2 minutes)

### Technology Stack

**Frontend**
- React 18.2.0
- React Router DOM 6.14.1 (navigation)
- Axios 1.4.0 (HTTP client)
- Tailwind CSS 3.4.19 (utility-first styling)
- PostCSS 8.5.6 & Autoprefixer 10.4.24
- Custom CSS with gradient backgrounds
- React Scripts 5.0.1 (build tooling)

**Backend**
- Python 3.10+
- Flask (web framework)
- Flask-CORS (cross-origin resource sharing)
- SQLite3 (database - built into Python)
- Hashlib (password hashing)

**AI/ML Stack**
- PyTorch (deep learning framework)
- Transformers (Hugging Face)
  - GPT-2 model for scenario generation
  - GPT-2 tokenizer
- Scikit-learn (classification models)
- Pandas & NumPy (data processing)
- Pickle (model serialization)

**APIs & Services**
- Custom REST API endpoints:
  - `/api/auth/*` - Authentication (register, login, logout)
  - `/api/scenario/*` - Scenario generation & submission
  - `/api/leaderboard` - User rankings
  - `/api/achievements` - Achievement tracking
  - `/api/profile/*` - User profile management
  - `/api/reference/codes` - Code reference lookup
  - `/api/death-certificate/*` - Life insurance document review

**Data & Reference**
- JSON-based code mappings (CPT, ICD-10, CDT codes)
- Custom insurance claims datasets
- Reference data for medical/dental/life claims

**Deployment**
- Docker containerization
- Docker Compose orchestration
- Environment-based configuration
- Multi-stage builds for optimization

**Additional Libraries**
- ReportLab (PDF generation for documents)
- Base64 encoding (profile pictures)
- Session management (Flask sessions)

### Project Structure
```
CCAP-ClaimsTraingGame/
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.js         # Main application
│   │   └── App.css        # Tailwind + custom styles
│   ├── package.json       # Dependencies
│   └── tailwind.config.js # Tailwind configuration
├── backend/
│   ├── app.py             # Flask application
│   ├── ai_service.py      # AI model integration
│   ├── death_certificate_service.py
│   ├── itemized_bill_service.py
│   ├── requirements.txt   # Python dependencies
│   ├── data.db            # SQLite database
│   └── reference_data/    # Code mappings JSON
├── ai_models/
│   ├── models/            # Trained models
│   │   ├── claim_classifier.pkl
│   │   └── scenario_generator/
│   └── training scripts
├── datasets/              # Insurance claims data
└── docker-compose.yml     # Container orchestration
```

### Database Schema
- **users**: id, username, password_hash, score, current_streak, xp, level, bio, profile_picture
- **scenarios**: id, claim_type, difficulty, scenario_json, correct_answer, created_at
- **attempts**: id, user_id, scenario_id, user_answer, is_correct, feedback_text, points_earned, created_at
- **achievements**: id, user_id, achievement_key, unlocked_at

---

## 5. Challenges & Solutions (2 minutes)

### Challenge 1: AI Model Integration
**Problem**: AI models too large for repository  
**Solution**: Created MODEL_SETUP.md with training instructions; models generated locally

### Challenge 2: User Data Persistence
**Problem**: Scores not saving between sessions  
**Solution**: Implemented database-backed user accounts with proper session management

### Challenge 3: Scenario Variety
**Problem**: Repetitive training scenarios  
**Solution**: AI-powered generation creates unique scenarios dynamically

### Challenge 4: [Add your specific challenge]
**Problem**: [Describe issue]  
**Solution**: [How you addressed it]

---

## 6. What's Next - Remaining Work (2 minutes)

### High Priority (Before Final)
- [ ] Enhanced AI model accuracy
- [ ] Additional claim types (Auto, Property)
- [ ] Leaderboard system
- [ ] Admin dashboard for tracking trainee progress
- [ ] Detailed performance analytics

### Medium Priority
- [ ] Multiplayer/competitive mode
- [ ] Time-based challenges
- [ ] Hint system for difficult scenarios
- [ ] Export training reports
- [ ] Mobile responsiveness improvements

### Nice-to-Have
- [ ] Social features (share achievements)
- [ ] Custom scenario creation by admins
- [ ] Integration with LMS platforms
- [ ] Multi-language support

---

## 7. Timeline to Completion (1 minute)

### Weeks 8-10
- Refine AI models
- Add 2 more claim types
- Implement leaderboard

### Weeks 11-12
- Admin dashboard
- Performance analytics
- Bug fixes and polish

### Weeks 13-14
- Final testing
- Documentation completion
- Deployment preparation

### Week 15
- Final presentation preparation
- Demo refinement

---

## 8. Questions to Address (1 minute)

### Anticipated Questions

**Q: How accurate are the AI-generated scenarios?**  
A: [Discuss model training, validation, and accuracy metrics]

**Q: Can this scale to multiple organizations?**  
A: [Discuss multi-tenancy plans, database design]

**Q: What makes this better than traditional training?**  
A: Immediate feedback, gamification, engagement metrics, personalized difficulty

**Q: How do you ensure claim scenarios are realistic?**  
A: [Discuss dataset sources, domain expert validation]

---

## 9. Feedback Requested

### Specific Areas for Input

1. **Feature Priority**: Which remaining features would be most valuable?
2. **User Experience**: Is the game flow intuitive?
3. **Difficulty Balance**: Are the difficulty levels appropriately challenging?
4. **Achievement System**: Are milestones motivating?
5. **Visual Design**: Does the UI effectively convey the training purpose?

---

## 10. Presentation Checklist

### Before Class
- [ ] Test live demo in presentation environment
- [ ] Prepare backup screenshots/video
- [ ] Charge laptop fully
- [ ] Test projector connection
- [ ] Have demo account credentials ready
- [ ] Clear browser cache/cookies
- [ ] Close unnecessary applications
- [ ] Disable notifications
- [ ] Print presentation notes

### During Presentation
- [ ] Speak clearly and at moderate pace
- [ ] Make eye contact with audience
- [ ] Show enthusiasm for the project
- [ ] Keep demo moving (don't get stuck debugging)
- [ ] Watch time (aim for 10-12 minutes total)
- [ ] Invite questions throughout
- [ ] Take notes on feedback

### Demo Credentials
- **Username**: Admin1
- **Password**: Password
- **Backup User**: [Create test account]

---

## 11. Key Talking Points

### Opening Hook
"Imagine learning insurance claims processing through a game instead of a 200-page manual. That's what we've built."

### Technical Highlight
"We've integrated AI to generate unlimited unique training scenarios, making every session fresh and challenging."

### Impact Statement
"This transforms weeks of boring training into engaging, measurable skill development."

### Closing
"We've proven the concept works. The next phase is scaling features and refining the experience based on your feedback today."

---

## Appendix: Technical Details (If Asked)

### Complete API Endpoints

**Authentication**
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - User login with credentials
- `POST /api/auth/logout` - End user session
- `GET /api/auth/me` - Get current user info

**Game Flow**
- `POST /api/scenario/generate` - Generate AI-powered scenario
- `POST /api/scenario/submit` - Submit answer and get feedback
- `GET /api/reference/codes` - Get code reference data (CPT/ICD-10/CDT)

**User Progress**
- `GET /api/leaderboard` - Get top 100 users by score
- `GET /api/achievements` - Get user's achievement progress
- `GET /api/profile` - Get user profile data
- `POST /api/profile/update` - Update bio and profile picture

**Life Insurance Features**
- `POST /api/death-certificate/generate` - Generate death certificate scenario
- `POST /api/death-certificate/validate` - Validate certificate review
- `GET /api/death-certificate/error-options` - Get possible error types

**Health Check**
- `GET /api/health` - Server health status

### AI Models in Detail

**Scenario Generator**
- Model: GPT-2 (Hugging Face Transformers)
- Purpose: Generate realistic insurance claim descriptions
- Training: Fine-tuned on insurance claims datasets
- Fallback: Rule-based generation with templates
- Output: Natural language claim scenarios

**Claim Classifier**
- Model: Scikit-learn classifier (saved as .pkl)
- Purpose: Classify claims as valid/invalid/insufficient
- Features: claim_amount, patient_age, claim_type, procedure_code, diagnosis_code
- Validation: Business rules overlay for accuracy
- Confidence scoring: Probability distribution across classes

**Business Rule Engine**
- Code matching validation (procedure ↔ diagnosis)
- Age verification (claim age vs. profile DOB)
- Pre-existing condition detection (injury date vs. policy start)
- Critical document verification
- Amount threshold checks

### CSS & Styling Details

**Tailwind CSS Configuration**
- Utility-first CSS framework
- Custom theme configuration
- Responsive breakpoints
- JIT (Just-In-Time) compilation

**Custom CSS Features**
- Linear gradient backgrounds: `#000000 → #1a1a2e → #0f3460`
- Principal branding colors:
  - Primary blue: `#00d4ff`
  - Gold accents: `#ffd700`
  - Success green: `#00ff88`
  - Error red: `#ff4757`
- Card shadows with blue glow: `rgba(0, 212, 255, 0.2)`
- Dark theme: `#1a1a2e` backgrounds
- Responsive design with flexbox

**Typography**
- Font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial`
- White text on dark backgrounds
- Font weights: 400 (normal), 600 (semibold), 700 (bold)

### Database Schema
- Users table (id, username, password_hash, created_at)
- Scores table (user_id, score, timestamp)
- Achievements table (user_id, achievement_id, unlocked_at)

### Performance Metrics (To Measure)
- API response time: [Measure during demo]
- Scenario generation time: [Measure during demo]
- Concurrent users supported: [Test before presentation]
- Database query performance: [Monitor during demo]
- Frontend load time: [Test on presentation machine]

---

## Notes Section (Use During Presentation)

[Space for writing down feedback, questions, and suggestions during the presentation]

---

**Remember**: 
- Confidence is key
- The demo doesn't have to be perfect
- Focus on what works, acknowledge what doesn't
- This is about progress, not perfection
- Engage with feedback positively
