# Angelfund API

A RESTful backend API for the Angelfund platform -- an investor-startup matching service that connects angel investors with startups using machine learning-based compatibility scoring.

## Tech Stack

- **Language:** Python 3
- **Framework:** Flask
- **Database:** MongoDB (via MongoEngine ODM)
- **Authentication:** JWT (JSON Web Tokens)
- **Email:** AWS SES (Simple Email Service)
- **Storage:** AWS S3
- **ML Integration:** Custom ML matching server
- **Serialization:** Marshmallow

## Features

- Investor and startup registration with email confirmation
- Google OAuth sign-in support
- JWT-based authentication and session management
- ML-powered investor-startup matching and discovery
- Dashboard with invite/pass/connect workflows
- Profile management with S3 image uploads
- Password reset via email
- Referral system
- Angel group name search
- Connection history (passed, connected, pending)
- Monday notification preferences
- Profile visibility controls
- Admin-level email deletion endpoint

## Prerequisites

- Python 3.7+
- MongoDB 4.0+
- AWS account (for SES and S3)
- pip / virtualenv

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/Angelfund.git
cd Angelfund

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your actual configuration values
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URI` | MongoDB connection string |
| `SECRET_KEY` | Flask secret key for sessions |
| `JWT_SECRET_KEY` | Secret key for JWT token signing |
| `SERVER_DOMAIN` | Base URL of the running server |
| `AWS_ACCESS_KEY_ID` | AWS access key for SES and S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key |
| `AWS_REGION` | AWS region (default: us-east-1) |
| `EMAIL_SENDER` | From address for transactional emails |
| `ML_SERVER_URL` | URL of the ML matching server |
| `ML_SERVER_X_AUTH_KEY` | Auth key for ML server |
| `RITEKIT_API_KEY` | RiteKit API key for company logos |
| `INTERNAL_API_KEY` | API key for internal admin endpoints |

## How to Run

```bash
# Development
python app.py

# The server runs on http://127.0.0.1:5000
```

## API Endpoints

### Investor Endpoints (`/api/v1/investor`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/google-token` | Google OAuth sign-in |
| POST | `/login` | Email/password login |
| POST | `/register` | New investor registration |
| POST | `/logout` | Logout (JWT required) |
| POST | `/forgot-password` | Request password reset email |
| GET/POST | `/reset-link/<token>` | Password reset form |
| PATCH | `/update-info` | Update investor profile |
| GET/POST | `/dashboard` | Discover matches / respond to matches |
| GET | `/history-all` | All connection history |
| GET | `/history-connected` | Connected startups |
| GET | `/history-passed` | Passed startups |
| POST | `/history-profile-view` | View a startup profile |
| POST | `/referral-link` | Send referral email |
| POST | `/mime-files` | Upload profile picture |
| POST | `/profile-visibility` | Toggle profile visibility |
| POST | `/monday-notifications` | Set notification preferences |
| GET | `/change-password` | Request password change email |
| POST | `/verify-password` | Verify password for account deletion |
| POST | `/delete-account` | Delete user account |
| GET | `/jwt-token-check` | Validate JWT token |
| POST | `/angelgroup-name-search` | Search angel group names |

### Startup Endpoints (`/api/v1/startup`)

Similar set of endpoints for startup users (registration, login, dashboard, profile, etc.)

## Project Structure

```
Angelfund/
├── app.py                          # Application entry point
├── project/
│   ├── __init__.py                 # Flask app config, DB init, blueprints
│   ├── models.py                   # MongoEngine models
│   ├── investor/
│   │   ├── views.py                # Investor API routes
│   │   └── marshmallow_serialize.py
│   ├── startup/
│   │   ├── views.py                # Startup API routes
│   │   └── marshmallow_serialize.py
│   ├── error/
│   │   └── error_handler.py        # Error handling blueprint
│   └── templates/                  # HTML templates for password reset
├── common_utilities/
│   ├── __init__.py                 # Configuration constants (env-based)
│   ├── emails/                     # Email templates (SES)
│   ├── analytics/                  # User analytics utilities
│   ├── machine_learning/           # ML matching integration
│   ├── flask_jwt_extended/         # Custom JWT extension
│   ├── jwt/                        # JWT library utilities
│   ├── scripts/                    # Maintenance scripts
│   └── tests/                      # Utility tests
├── requirements.txt
├── appspec.yml                     # AWS CodeDeploy spec
├── bitbucket-pipelines.yml         # CI/CD pipeline
└── start.sh
```

## License

MIT License
