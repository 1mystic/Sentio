# Mindfluence Backend

FastAPI-based backend for the Mindfluence mental health application.

## Features

- **Authentication & User Management**: JWT-based auth with Supabase integration
- **Assessments**: Mental health assessment APIs with ML-powered insights
- **Journal**: CRUD operations for journal entries with sentiment analysis
- **Community**: Discussion forums and peer support features
- **Learning Modules**: Interactive educational content management
- **Resources**: Mental health resources and professional directory
- **Self-Help Tools**: Interactive tools and exercises APIs
- **Analytics**: User progress tracking and insights generation
- **ML Models**: Sentiment analysis, mood prediction, and personalized recommendations

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT
- **ML/AI**: Hugging Face Transformers, scikit-learn
- **Deployment**: Vercel/Railway (serverless)
- **Storage**: Supabase Storage
- **Cache**: Redis (optional)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── dependencies.py        # Common dependencies
│   │
│   ├── auth/                  # Authentication module
│   │   ├── __init__.py
│   │   ├── router.py          # Auth routes
│   │   ├── models.py          # Auth models
│   │   └── utils.py           # Auth utilities
│   │
│   ├── users/                 # User management
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── assessments/           # Mental health assessments
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── scoring.py         # Assessment scoring logic
│   │
│   ├── journal/               # Journal functionality
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── sentiment.py       # Sentiment analysis
│   │
│   ├── community/             # Community features
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── modules/               # Learning modules
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── resources/             # Mental health resources
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── tools/                 # Self-help tools
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── analytics/             # Analytics and insights
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── models.py
│   │   └── insights.py        # ML-powered insights
│   │
│   ├── ml/                    # Machine learning models
│   │   ├── __init__.py
│   │   ├── sentiment_analyzer.py
│   │   ├── mood_predictor.py
│   │   ├── recommendation_engine.py
│   │   └── models/            # Saved ML models
│   │
│   ├── database/              # Database configuration
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations/
│   │
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── email.py
│       ├── security.py
│       └── helpers.py
│
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel deployment config
├── Dockerfile               # Docker configuration
└── README.md               # This file
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user

### Users
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `DELETE /users/account` - Delete user account

### Assessments
- `GET /assessments` - List available assessments
- `GET /assessments/{id}` - Get assessment details
- `POST /assessments/{id}/submit` - Submit assessment responses
- `GET /assessments/results` - Get user's assessment results
- `GET /assessments/results/{id}` - Get specific assessment result

### Journal
- `GET /journal/entries` - Get user's journal entries
- `POST /journal/entries` - Create new journal entry
- `GET /journal/entries/{id}` - Get specific entry
- `PUT /journal/entries/{id}` - Update journal entry
- `DELETE /journal/entries/{id}` - Delete journal entry
- `GET /journal/analytics` - Get journal analytics

### Community
- `GET /community/posts` - Get community posts
- `POST /community/posts` - Create new post
- `GET /community/posts/{id}` - Get specific post
- `POST /community/posts/{id}/comments` - Add comment
- `GET /community/threads` - Get discussion threads

### Modules
- `GET /modules` - List learning modules
- `GET /modules/{id}` - Get module details
- `POST /modules/{id}/progress` - Update module progress
- `GET /modules/{id}/content` - Get module content

### Resources
- `GET /resources/professionals` - Search mental health professionals
- `GET /resources/educational` - Get educational materials
- `GET /resources/crisis` - Get crisis resources
- `GET /resources/tools` - Get self-help tools

### Tools
- `POST /tools/breathing/session` - Log breathing exercise session
- `POST /tools/mood/log` - Log mood entry
- `POST /tools/thought-record` - Save thought record
- `GET /tools/progress` - Get tools usage progress

### Analytics
- `GET /analytics/dashboard` - Get dashboard analytics
- `GET /analytics/insights` - Get ML-powered insights
- `GET /analytics/progress` - Get progress tracking data
- `GET /analytics/recommendations` - Get personalized recommendations

## Getting Started

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Configure your environment variables
   ```

3. **Database Setup**
   ```bash
   # Supabase project setup
   # Run migrations if needed
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **API Documentation**
   - Visit `http://localhost:8000/docs` for interactive API docs
   - Visit `http://localhost:8000/redoc` for alternative documentation

## Deployment

### Vercel (Recommended)
```bash
vercel --prod
```

### Railway
```bash
railway login
railway deploy
```

## Environment Variables

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Models
HUGGINGFACE_API_KEY=your_hf_api_key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.
