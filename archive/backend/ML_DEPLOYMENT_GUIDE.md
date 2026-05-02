# ML Backend Setup and Deployment Guide

## Overview

This ML backend provides comprehensive mental health analysis capabilities including:

- **Sentiment Analysis**: Advanced sentiment detection tailored for mental health contexts
- **Crisis Detection**: Real-time identification of crisis situations with immediate alerts
- **Behavioral Pattern Analysis**: User behavior pattern detection and insights
- **Mood Prediction**: Predictive modeling for future mood states
- **Personalized Recommendations**: AI-driven recommendations based on user analysis
- **Risk Assessment**: Continuous monitoring and risk level evaluation

## Key ML Components Included

### 1. Sentiment Analysis Models
- **Primary Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Emotion Detection**: `j-hartmann/emotion-english-distilroberta-base`
- **Mental Health Keywords**: Custom keyword analysis for anxiety, depression, crisis indicators
- **Temporal Pattern Analysis**: Time-based sentiment tracking

### 2. Crisis Detection System
- **Multi-layered Detection**: Keyword analysis, severity assessment, context evaluation
- **Risk Scoring**: Quantitative risk assessment with intervention thresholds
- **Immediate Alerts**: Automated crisis response with resource recommendations
- **Protective Factor Analysis**: Identification of positive coping mechanisms

### 3. Behavioral Analytics
- **Pattern Recognition**: Journal frequency, temporal patterns, content analysis
- **Engagement Metrics**: User interaction patterns and consistency scoring
- **Trend Analysis**: Long-term behavioral trend identification
- **Personalized Insights**: Custom insights based on individual patterns

### 4. Predictive Models
- **Mood Prediction**: Future mood state prediction using historical data
- **Risk Forecasting**: Early warning system for concerning pattern development
- **Recommendation Engine**: Personalized intervention and activity suggestions

## Installation Requirements

### Core Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Download NLTK data (optional, for enhanced text processing)
python -c "import nltk; nltk.download('vader_lexicon')"
```

### Model Downloads
The system will automatically download required Hugging Face models on first use:
- `cardiffnlp/twitter-roberta-base-sentiment-latest` (~500MB)
- `j-hartmann/emotion-english-distilroberta-base` (~250MB)

### Environment Variables
```bash
# ML Configuration
ML_MODEL_DIR=./models
ML_CACHE_DIR=./cache
ML_LOGS_DIR=./logs
ML_MAX_WORKERS=4
ML_CACHE_TTL=300
ML_ENABLE_GPU=false

# Crisis Detection
CRISIS_THRESHOLD=0.7
AUTO_ALERT_ENABLED=true

# Model Training
MIN_TRAINING_SAMPLES=50
MODEL_UPDATE_INTERVAL=24

# Performance
MAX_TEXT_LENGTH=2048
FEATURE_CACHE_SIZE=1000
```

## API Endpoints

### 1. Journal Analysis
```http
POST /ml/analyze-journal
```
Analyzes journal entries for sentiment, mental health indicators, and crisis detection.

**Request:**
```json
{
  "entry_text": "I've been feeling really overwhelmed lately...",
  "entry_metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "session_duration": 300
  }
}
```

**Response:**
```json
{
  "user_id": "user123",
  "entry_analysis": {
    "sentiment": {
      "polarity": -0.3,
      "subjectivity": 0.8,
      "label": "negative"
    },
    "mental_health": {
      "anxiety": 0.6,
      "depression": 0.2,
      "positive": 0.1
    },
    "risk_assessment": {
      "level": "moderate",
      "score": 2.1,
      "requires_intervention": true
    },
    "recommendations": [
      "Consider breathing exercises or meditation",
      "Try grounding techniques (5-4-3-2-1 method)"
    ]
  },
  "crisis_assessment": {
    "is_crisis": false,
    "risk_score": 0.4,
    "severity": "medium"
  },
  "requires_attention": true
}
```

### 2. Pattern Analysis
```http
POST /ml/analyze-patterns
```
Analyzes user behavioral patterns and generates insights.

### 3. Mood Prediction
```http
POST /ml/predict-mood
```
Predicts future mood states based on current context and historical data.

### 4. Personalized Recommendations
```http
POST /ml/recommendations
```
Generates personalized recommendations based on analysis results.

### 5. Crisis Resources
```http
GET /ml/crisis-resources
```
Returns available crisis resources and helplines.

### 6. ML Insights Dashboard
```http
GET /ml/insights-dashboard
```
Comprehensive ML insights for user dashboard display.

## Deployment Considerations

### 1. Resource Requirements
- **Memory**: 4GB+ RAM (8GB recommended for production)
- **Storage**: 2GB+ for models and cache
- **CPU**: Multi-core recommended for concurrent processing
- **GPU**: Optional, but improves performance for large-scale deployments

### 2. Scalability
- **Horizontal Scaling**: FastAPI supports multiple worker processes
- **Model Caching**: Intelligent caching reduces model loading overhead
- **Background Processing**: Crisis detection and model training run asynchronously
- **Database Optimization**: Efficient queries for pattern analysis

### 3. Security & Privacy
- **Data Encryption**: All sensitive data encrypted in transit and at rest
- **User Anonymization**: Personal identifiers separated from analysis data
- **HIPAA Compliance**: Architecture supports healthcare compliance requirements
- **Audit Logging**: Comprehensive logging for crisis interventions

### 4. Monitoring & Alerts
- **Real-time Monitoring**: Model performance and response time tracking
- **Crisis Alerts**: Immediate notifications for high-risk situations
- **Performance Metrics**: Accuracy, precision, recall tracking
- **Health Checks**: System health monitoring and auto-recovery

## Production Deployment

### 1. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download models during build
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest')"

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Environment Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  ml-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - ML_ENABLE_GPU=false
    volumes:
      - ./models:/app/models
      - ./cache:/app/cache
    restart: unless-stopped
```

### 3. Load Balancing
```nginx
upstream ml_backend {
    server ml-backend-1:8000;
    server ml-backend-2:8000;
    server ml-backend-3:8000;
}

server {
    listen 80;
    location /ml/ {
        proxy_pass http://ml_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Model Training & Updates

### 1. Continuous Learning
```python
# Background model training
@app.on_event("startup")
async def schedule_model_updates():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_models,
        trigger="interval",
        hours=24,
        id="model_update"
    )
    scheduler.start()
```

### 2. A/B Testing
```python
# Model version testing
async def analyze_with_ab_testing(text: str, user_id: str):
    if user_id in test_group:
        return await new_model.analyze(text)
    else:
        return await current_model.analyze(text)
```

## Crisis Response Protocol

### 1. Immediate Response (Risk Score > 0.8)
- Automatic alert to designated emergency contacts
- Display crisis resources prominently
- Log incident for immediate follow-up
- Consider emergency service notification (with user consent)

### 2. Elevated Response (Risk Score 0.5-0.8)
- Gentle intervention suggestions
- Enhanced monitoring for 24-48 hours
- Therapist/counselor recommendations
- Safety planning resources

### 3. Preventive Response (Risk Score 0.3-0.5)
- Wellness activity suggestions
- Peer support recommendations
- Mood tracking encouragement
- Self-care reminders

## Testing & Validation

### 1. Unit Tests
```bash
pytest tests/ml/ -v
```

### 2. Integration Tests
```bash
pytest tests/integration/ -v
```

### 3. Model Performance Tests
```bash
python scripts/evaluate_models.py
```

## Compliance & Ethics

### 1. Data Handling
- Minimize data collection to essential analysis requirements
- Implement data retention policies
- Provide user data export/deletion capabilities
- Regular security audits

### 2. Bias Mitigation
- Regular model bias evaluation
- Diverse training data requirements
- Fairness metrics monitoring
- Inclusive algorithm design

### 3. Transparency
- Clear explanations of ML decisions
- User control over analysis features
- Open documentation of model limitations
- Regular algorithmic impact assessments

## Support & Maintenance

### 1. Model Updates
- Monthly model performance reviews
- Quarterly model version updates
- Annual comprehensive system audits
- Continuous security patches

### 2. Support Channels
- Technical documentation wiki
- Developer support forums
- Emergency escalation procedures
- Regular training for support staff

---

This ML backend represents a comprehensive approach to mental health technology, combining cutting-edge AI with responsible deployment practices and ethical considerations.
