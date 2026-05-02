from typing import Dict, List, Any, Tuple
import re
import logging
from datetime import datetime

# For now, we'll use a simple rule-based sentiment analysis
# In production, you'd use transformers or other ML libraries

logger = logging.getLogger(__name__)

# Simple sentiment word lists
POSITIVE_WORDS = {
    'happy', 'joy', 'excited', 'grateful', 'love', 'amazing', 'wonderful', 
    'fantastic', 'great', 'good', 'positive', 'optimistic', 'peaceful', 
    'calm', 'content', 'satisfied', 'pleased', 'delighted', 'cheerful',
    'confident', 'hopeful', 'motivated', 'inspired', 'blessed', 'thankful'
}

NEGATIVE_WORDS = {
    'sad', 'angry', 'frustrated', 'worried', 'anxious', 'depressed', 
    'upset', 'disappointed', 'stressed', 'overwhelmed', 'tired', 'exhausted',
    'lonely', 'scared', 'afraid', 'nervous', 'irritated', 'annoyed',
    'hopeless', 'worthless', 'guilty', 'ashamed', 'regret', 'pain'
}

EMOTION_KEYWORDS = {
    'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'fear', 'stress'],
    'depression': ['sad', 'hopeless', 'empty', 'worthless', 'numb'],
    'anger': ['angry', 'frustrated', 'irritated', 'mad', 'furious'],
    'joy': ['happy', 'joyful', 'excited', 'elated', 'cheerful'],
    'love': ['love', 'affection', 'care', 'adore', 'cherish'],
    'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed'],
    'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'relaxed'],
    'confidence': ['confident', 'strong', 'capable', 'empowered']
}

THEME_KEYWORDS = {
    'work': ['work', 'job', 'career', 'office', 'boss', 'colleague', 'meeting'],
    'relationships': ['friend', 'family', 'partner', 'spouse', 'relationship', 'love'],
    'health': ['health', 'exercise', 'sleep', 'diet', 'doctor', 'medical'],
    'personal_growth': ['growth', 'learning', 'goal', 'achievement', 'progress'],
    'stress': ['stress', 'pressure', 'overwhelmed', 'deadline', 'busy'],
    'self_care': ['meditation', 'relaxation', 'hobby', 'break', 'vacation']
}

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of text using simple rule-based approach
    In production, replace with ML model like transformers
    """
    try:
        if not text or not text.strip():
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0
            }
        
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0
            }
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = 'neutral'
            confidence = 0.1
        else:
            sentiment_score = (positive_count - negative_count) / len(words)
            confidence = min(total_sentiment_words / len(words), 1.0)
            
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
        
        return {
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': sentiment_label,
            'confidence': round(confidence, 3)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {
            'sentiment_score': 0.0,
            'sentiment_label': 'neutral',
            'confidence': 0.0
        }

def extract_emotions(text: str) -> List[str]:
    """Extract emotions mentioned in text"""
    try:
        words = re.findall(r'\b\w+\b', text.lower())
        detected_emotions = []
        
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(keyword in text.lower() for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions[:5]  # Limit to top 5 emotions
        
    except Exception as e:
        logger.error(f"Error extracting emotions: {e}")
        return []

def extract_themes(text: str) -> List[str]:
    """Extract key themes from text"""
    try:
        detected_themes = []
        
        for theme, keywords in THEME_KEYWORDS.items():
            if any(keyword in text.lower() for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes[:3]  # Limit to top 3 themes
        
    except Exception as e:
        logger.error(f"Error extracting themes: {e}")
        return []

def generate_suggestions(sentiment_data: Dict[str, Any], emotions: List[str]) -> List[str]:
    """Generate helpful suggestions based on sentiment and emotions"""
    try:
        suggestions = []
        
        sentiment_score = sentiment_data.get('sentiment_score', 0)
        sentiment_label = sentiment_data.get('sentiment_label', 'neutral')
        
        # Base suggestions on sentiment
        if sentiment_label == 'negative' or sentiment_score < -0.2:
            suggestions.extend([
                "Consider practicing a mindfulness exercise",
                "Take some deep breaths and focus on the present moment",
                "Reach out to a friend or family member for support"
            ])
        elif sentiment_label == 'positive':
            suggestions.extend([
                "Notice and savor this positive moment",
                "Consider sharing your good feelings with someone",
                "Reflect on what contributed to these positive feelings"
            ])
        
        # Emotion-specific suggestions
        if 'anxiety' in emotions:
            suggestions.append("Try the 4-7-8 breathing technique to calm anxiety")
        
        if 'depression' in emotions:
            suggestions.append("Consider gentle movement or spending time in nature")
        
        if 'anger' in emotions:
            suggestions.append("Take a break and try progressive muscle relaxation")
        
        if 'gratitude' in emotions:
            suggestions.append("Write down three things you're grateful for today")
        
        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))[:4]
        
        if not suggestions:
            suggestions = [
                "Continue journaling regularly to track your emotional patterns",
                "Practice self-compassion and be kind to yourself"
            ]
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return ["Continue reflecting on your thoughts and feelings"]

def analyze_journal_entry(text: str) -> Dict[str, Any]:
    """Complete analysis of journal entry"""
    try:
        # Get sentiment analysis
        sentiment_data = analyze_sentiment(text)
        
        # Extract emotions and themes
        emotions = extract_emotions(text)
        themes = extract_themes(text)
        
        # Generate suggestions
        suggestions = generate_suggestions(sentiment_data, emotions)
        
        return {
            'sentiment_score': sentiment_data['sentiment_score'],
            'sentiment_label': sentiment_data['sentiment_label'],
            'sentiment_confidence': sentiment_data['confidence'],
            'key_themes': themes,
            'emotional_indicators': emotions,
            'suggestions': suggestions
        }
        
    except Exception as e:
        logger.error(f"Error analyzing journal entry: {e}")
        return {
            'sentiment_score': 0.0,
            'sentiment_label': 'neutral',
            'sentiment_confidence': 0.0,
            'key_themes': [],
            'emotional_indicators': [],
            'suggestions': []
        }
