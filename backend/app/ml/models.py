"""
Advanced ML models for mental health analysis and prediction.
This module provides comprehensive AI-powered insights for user mental health status.
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertForSequenceClassification
)
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import pandas as pd
import re
from textblob import TextBlob
import spacy
from collections import defaultdict

logger = logging.getLogger(__name__)

class MentalHealthAnalyzer:
    """
    Advanced mental health analysis using multiple ML models.
    Combines sentiment analysis, emotion detection, risk assessment, and behavioral patterns.
    """
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.risk_model = None
        self.mood_predictor = None
        self.nlp = None
        self.scaler = StandardScaler()
        self.load_models()
    
    def load_models(self):
        """Load all pre-trained models and pipelines."""
        try:
            # Sentiment Analysis (fine-tuned for mental health)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Emotion Detection
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                tokenizer="j-hartmann/emotion-english-distilroberta-base"
            )
            
            # Load spaCy for NLP processing
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Initialize risk assessment model (to be trained)
            self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Initialize mood prediction model
            self.mood_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            logger.info("All ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

class SentimentAnalyzer:
    """Enhanced sentiment analysis specifically for mental health contexts."""
    
    def __init__(self):
        self.mental_health_keywords = {
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'stress', 'overwhelmed'],
            'depression': ['sad', 'hopeless', 'empty', 'worthless', 'tired', 'exhausted'],
            'positive': ['happy', 'grateful', 'accomplished', 'peaceful', 'confident', 'hopeful'],
            'crisis': ['suicide', 'kill myself', 'end it all', 'no point', 'can\'t go on']
        }
        
        self.severity_weights = {
            'mild': 1.0,
            'moderate': 2.0,
            'severe': 3.0,
            'crisis': 5.0
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive sentiment analysis with mental health focus.
        """
        if not text or len(text.strip()) == 0:
            return self._empty_result()
        
        try:
            # Basic sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Mental health keyword analysis
            mh_scores = self._analyze_mental_health_keywords(text.lower())
            
            # Risk assessment
            risk_level = self._assess_risk_level(text.lower(), mh_scores)
            
            # Emotional intensity
            intensity = self._calculate_emotional_intensity(text)
            
            # Temporal analysis (if timestamp patterns exist)
            temporal_patterns = self._analyze_temporal_patterns(text)
            
            return {
                'sentiment': {
                    'polarity': polarity,
                    'subjectivity': subjectivity,
                    'label': self._polarity_to_label(polarity)
                },
                'mental_health': mh_scores,
                'risk_assessment': risk_level,
                'emotional_intensity': intensity,
                'temporal_patterns': temporal_patterns,
                'recommendations': self._generate_recommendations(mh_scores, risk_level),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._empty_result()
    
    def _analyze_mental_health_keywords(self, text: str) -> Dict[str, float]:
        """Analyze mental health specific keywords and their frequency."""
        scores = {}
        
        for category, keywords in self.mental_health_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            scores[category] = count / len(keywords) if keywords else 0.0
        
        return scores
    
    def _assess_risk_level(self, text: str, mh_scores: Dict[str, float]) -> Dict[str, Any]:
        """Assess risk level based on content analysis."""
        risk_score = 0.0
        
        # Crisis keywords have highest weight
        if mh_scores.get('crisis', 0) > 0:
            risk_score += 5.0
        
        # Depression and anxiety indicators
        risk_score += mh_scores.get('depression', 0) * 2.0
        risk_score += mh_scores.get('anxiety', 0) * 1.5
        
        # Positive indicators reduce risk
        risk_score -= mh_scores.get('positive', 0) * 1.0
        
        risk_score = max(0, risk_score)  # Ensure non-negative
        
        if risk_score >= 4.0:
            level = 'high'
        elif risk_score >= 2.0:
            level = 'moderate'
        elif risk_score >= 1.0:
            level = 'low'
        else:
            level = 'minimal'
        
        return {
            'level': level,
            'score': risk_score,
            'requires_intervention': level in ['high', 'moderate']
        }
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity based on linguistic features."""
        # Count exclamation marks, all caps, repetitive punctuation
        exclamations = text.count('!')
        all_caps_words = len([word for word in text.split() if word.isupper() and len(word) > 1])
        repetitive_punct = len(re.findall(r'[!?]{2,}', text))
        
        intensity = (exclamations * 0.3 + all_caps_words * 0.5 + repetitive_punct * 0.7)
        return min(intensity / len(text.split()) if text.split() else 0, 1.0)
    
    def _analyze_temporal_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze temporal patterns in the text."""
        time_references = {
            'past': ['yesterday', 'last week', 'before', 'used to', 'remember when'],
            'present': ['now', 'today', 'currently', 'right now', 'at the moment'],
            'future': ['tomorrow', 'next week', 'will', 'going to', 'plan to']
        }
        
        patterns = {}
        text_lower = text.lower()
        
        for period, keywords in time_references.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            patterns[period] = count
        
        return patterns
    
    def _generate_recommendations(self, mh_scores: Dict[str, float], risk_level: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on analysis."""
        recommendations = []
        
        if risk_level['level'] == 'high':
            recommendations.extend([
                "Consider reaching out to a mental health professional immediately",
                "Contact a crisis helpline if you're having thoughts of self-harm",
                "Reach out to a trusted friend or family member"
            ])
        
        if mh_scores.get('anxiety', 0) > 0.3:
            recommendations.extend([
                "Try breathing exercises or meditation",
                "Consider grounding techniques (5-4-3-2-1 method)",
                "Practice progressive muscle relaxation"
            ])
        
        if mh_scores.get('depression', 0) > 0.3:
            recommendations.extend([
                "Engage in physical activity, even a short walk",
                "Try to maintain social connections",
                "Consider mood tracking to identify patterns"
            ])
        
        if mh_scores.get('positive', 0) > 0.5:
            recommendations.append("Continue the positive practices that are working for you")
        
        return recommendations
    
    def _polarity_to_label(self, polarity: float) -> str:
        """Convert polarity score to human-readable label."""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            'sentiment': {'polarity': 0.0, 'subjectivity': 0.0, 'label': 'neutral'},
            'mental_health': {},
            'risk_assessment': {'level': 'minimal', 'score': 0.0, 'requires_intervention': False},
            'emotional_intensity': 0.0,
            'temporal_patterns': {},
            'recommendations': [],
            'analysis_timestamp': datetime.utcnow().isoformat()
        }

class BehavioralPatternAnalyzer:
    """Analyze user behavioral patterns from journal entries and app usage."""
    
    def __init__(self):
        self.pattern_features = [
            'entry_frequency', 'entry_length', 'time_of_day', 'day_of_week',
            'sentiment_variance', 'topic_diversity', 'response_time'
        ]
    
    def analyze_patterns(self, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze behavioral patterns from user interaction data.
        """
        if not user_data:
            return {'patterns': {}, 'insights': [], 'recommendations': []}
        
        try:
            df = pd.DataFrame(user_data)
            
            patterns = {
                'frequency_analysis': self._analyze_frequency(df),
                'temporal_analysis': self._analyze_temporal_patterns(df),
                'content_analysis': self._analyze_content_patterns(df),
                'engagement_analysis': self._analyze_engagement(df)
            }
            
            insights = self._generate_insights(patterns)
            recommendations = self._generate_behavioral_recommendations(patterns)
            
            return {
                'patterns': patterns,
                'insights': insights,
                'recommendations': recommendations,
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in behavioral pattern analysis: {str(e)}")
            return {'patterns': {}, 'insights': [], 'recommendations': []}
    
    def _analyze_frequency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze frequency patterns in user entries."""
        if 'created_at' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        daily_counts = df.groupby('date').size()
        
        return {
            'avg_daily_entries': daily_counts.mean(),
            'max_daily_entries': daily_counts.max(),
            'consistency_score': 1 - (daily_counts.std() / daily_counts.mean() if daily_counts.mean() > 0 else 0),
            'active_days_percentage': len(daily_counts) / 30 * 100  # Assume 30-day analysis window
        }
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal patterns in user behavior."""
        if 'created_at' not in df.columns:
            return {}
        
        df['hour'] = pd.to_datetime(df['created_at']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek
        
        return {
            'peak_hours': df['hour'].value_counts().head(3).to_dict(),
            'peak_days': df['day_of_week'].value_counts().head(3).to_dict(),
            'night_entries_percentage': len(df[df['hour'].between(22, 6)]) / len(df) * 100
        }
    
    def _analyze_content_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in content characteristics."""
        if 'content' not in df.columns:
            return {}
        
        df['word_count'] = df['content'].str.split().str.len()
        df['sentiment_score'] = df['content'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
        
        return {
            'avg_word_count': df['word_count'].mean(),
            'word_count_trend': self._calculate_trend(df['word_count'].tolist()),
            'sentiment_stability': 1 - df['sentiment_score'].std(),
            'avg_sentiment': df['sentiment_score'].mean()
        }
    
    def _analyze_engagement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        # This would include metrics like session duration, feature usage, etc.
        return {
            'session_consistency': 0.8,  # Placeholder - would calculate from actual session data
            'feature_diversity': 0.7,   # Placeholder - variety of features used
            'completion_rate': 0.9      # Placeholder - percentage of started activities completed
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return 'stable'
        
        slope = np.polyfit(range(len(values)), values, 1)[0]
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from behavioral patterns."""
        insights = []
        
        freq = patterns.get('frequency_analysis', {})
        temporal = patterns.get('temporal_analysis', {})
        content = patterns.get('content_analysis', {})
        
        if freq.get('consistency_score', 0) > 0.8:
            insights.append("You maintain excellent consistency in your journaling habits")
        elif freq.get('consistency_score', 0) < 0.4:
            insights.append("Your journaling frequency varies significantly - consider setting a routine")
        
        if temporal.get('night_entries_percentage', 0) > 30:
            insights.append("You tend to journal late at night - this might indicate sleep pattern changes")
        
        if content.get('sentiment_stability', 0) < 0.3:
            insights.append("Your emotional state shows high variability - consider mood tracking")
        
        return insights
    
    def _generate_behavioral_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on behavioral patterns."""
        recommendations = []
        
        freq = patterns.get('frequency_analysis', {})
        content = patterns.get('content_analysis', {})
        
        if freq.get('consistency_score', 0) < 0.5:
            recommendations.append("Try setting a daily reminder to maintain consistent journaling")
        
        if content.get('avg_word_count', 0) < 50:
            recommendations.append("Consider writing longer entries for better emotional processing")
        
        if content.get('avg_sentiment', 0) < -0.3:
            recommendations.append("Your entries show consistently negative sentiment - consider speaking with a counselor")
        
        return recommendations

class MoodPredictor:
    """Predict future mood states based on historical data and patterns."""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = [
            'day_of_week', 'hour_of_day', 'previous_mood', 'sentiment_trend',
            'entry_frequency', 'sleep_quality', 'activity_level'
        ]
    
    def prepare_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare features for mood prediction."""
        features = []
        
        for entry in data:
            feature_vector = [
                entry.get('day_of_week', 0),
                entry.get('hour_of_day', 12),
                entry.get('previous_mood', 0.0),
                entry.get('sentiment_trend', 0.0),
                entry.get('entry_frequency', 1.0),
                entry.get('sleep_quality', 3.0),
                entry.get('activity_level', 3.0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the mood prediction model."""
        try:
            if len(training_data) < 10:
                logger.warning("Insufficient training data for mood prediction")
                return False
            
            X = self.prepare_features(training_data)
            y = [entry.get('mood_score', 0.0) for entry in training_data]
            
            self.model.fit(X, y)
            self.is_trained = True
            
            logger.info(f"Mood prediction model trained with {len(training_data)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training mood prediction model: {str(e)}")
            return False
    
    def predict_mood(self, current_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict mood for the next period."""
        if not self.is_trained:
            return {'prediction': 0.0, 'confidence': 0.0, 'factors': []}
        
        try:
            feature_vector = self.prepare_features([current_features])
            prediction = self.model.predict(feature_vector)[0]
            
            # Calculate feature importance for explanation
            feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'prediction': float(prediction),
                'confidence': min(0.95, max(0.1, abs(prediction) / 5.0)),  # Simple confidence estimate
                'factors': [factor[0] for factor in top_factors],
                'prediction_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in mood prediction: {str(e)}")
            return {'prediction': 0.0, 'confidence': 0.0, 'factors': []}

class CrisisDetector:
    """Detect crisis situations and provide immediate intervention recommendations."""
    
    def __init__(self):
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'no point living',
            'can\'t go on', 'want to die', 'better off dead',
            'life is meaningless', 'give up', 'hopeless'
        ]
        
        self.severity_indicators = {
            'high': ['plan', 'method', 'tonight', 'today', 'right now'],
            'medium': ['thinking about', 'considering', 'sometimes'],
            'low': ['wondered', 'thought about', 'curious']
        }
        
        self.protective_factors = [
            'family', 'friends', 'pets', 'children', 'responsibilities',
            'future plans', 'goals', 'hope', 'support'
        ]
    
    def detect_crisis(self, text: str, user_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Detect crisis indicators in text and user history.
        """
        text_lower = text.lower()
        
        # Crisis keyword detection
        crisis_indicators = [kw for kw in self.crisis_keywords if kw in text_lower]
        
        # Severity assessment
        severity = self._assess_severity(text_lower)
        
        # Protective factors
        protective = [pf for pf in self.protective_factors if pf in text_lower]
        
        # Historical pattern analysis
        historical_risk = self._analyze_historical_risk(user_history) if user_history else 0.0
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(
            len(crisis_indicators), severity, len(protective), historical_risk
        )
        
        return {
            'is_crisis': risk_score > 0.7,
            'risk_score': risk_score,
            'severity': severity,
            'crisis_indicators': crisis_indicators,
            'protective_factors': protective,
            'immediate_actions': self._get_immediate_actions(risk_score),
            'resources': self._get_crisis_resources(),
            'detection_timestamp': datetime.utcnow().isoformat()
        }
    
    def _assess_severity(self, text: str) -> str:
        """Assess severity level of crisis indicators."""
        for level, indicators in self.severity_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level
        return 'low'
    
    def _analyze_historical_risk(self, history: List[Dict]) -> float:
        """Analyze historical risk patterns."""
        if not history:
            return 0.0
        
        recent_entries = [entry for entry in history 
                         if (datetime.utcnow() - datetime.fromisoformat(entry.get('created_at', '2020-01-01'))).days <= 7]
        
        if not recent_entries:
            return 0.0
        
        # Check for declining sentiment trend
        sentiments = [entry.get('sentiment_score', 0.0) for entry in recent_entries]
        trend = np.polyfit(range(len(sentiments)), sentiments, 1)[0] if len(sentiments) > 1 else 0
        
        return max(0.0, -trend * 2)  # Negative trend increases risk
    
    def _calculate_risk_score(self, crisis_count: int, severity: str, protective_count: int, historical_risk: float) -> float:
        """Calculate overall risk score."""
        base_score = crisis_count * 0.3
        
        severity_multiplier = {'high': 2.0, 'medium': 1.5, 'low': 1.0}.get(severity, 1.0)
        base_score *= severity_multiplier
        
        # Protective factors reduce risk
        base_score -= protective_count * 0.1
        
        # Add historical risk
        base_score += historical_risk * 0.2
        
        return min(1.0, max(0.0, base_score))
    
    def _get_immediate_actions(self, risk_score: float) -> List[str]:
        """Get immediate action recommendations based on risk score."""
        if risk_score > 0.8:
            return [
                "Contact emergency services immediately (911)",
                "Reach out to a crisis helpline",
                "Don't leave the person alone",
                "Remove any means of self-harm",
                "Get professional help immediately"
            ]
        elif risk_score > 0.5:
            return [
                "Contact a mental health professional",
                "Reach out to a trusted friend or family member",
                "Call a crisis helpline for support",
                "Consider going to an emergency room",
                "Don't ignore these feelings"
            ]
        else:
            return [
                "Consider talking to someone you trust",
                "Reach out to a counselor or therapist",
                "Use coping strategies you've learned",
                "Engage in self-care activities"
            ]
    
    def _get_crisis_resources(self) -> List[Dict[str, str]]:
        """Get crisis resources and helplines."""
        return [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "description": "24/7 crisis support"
            },
            {
                "name": "Crisis Text Line",
                "phone": "Text HOME to 741741",
                "description": "24/7 text-based crisis support"
            },
            {
                "name": "SAMHSA National Helpline",
                "phone": "1-800-662-4357",
                "description": "Treatment referral and information service"
            }
        ]

# Initialize global instances
mental_health_analyzer = MentalHealthAnalyzer()
sentiment_analyzer = SentimentAnalyzer()
behavioral_analyzer = BehavioralPatternAnalyzer()
mood_predictor = MoodPredictor()
crisis_detector = CrisisDetector()
