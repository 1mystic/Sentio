"""
ML Service for integrating machine learning models with the FastAPI backend.
This service provides a high-level interface for all ML operations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from .models import (
    sentiment_analyzer, behavioral_analyzer, mood_predictor, 
    crisis_detector, mental_health_analyzer
)

logger = logging.getLogger(__name__)

class MLService:
    """
    Main ML service that coordinates all machine learning operations.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    async def analyze_journal_entry(self, entry_text: str, user_id: str, entry_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of a journal entry including sentiment, risk assessment, and recommendations.
        """
        try:
            # Run sentiment analysis
            sentiment_result = await self._run_in_executor(
                sentiment_analyzer.analyze_text, entry_text
            )
            
            # Run crisis detection
            crisis_result = await self._run_in_executor(
                crisis_detector.detect_crisis, entry_text
            )
            
            # Combine results
            analysis = {
                'user_id': user_id,
                'entry_analysis': sentiment_result,
                'crisis_assessment': crisis_result,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'requires_attention': crisis_result.get('is_crisis', False) or 
                                   sentiment_result.get('risk_assessment', {}).get('requires_intervention', False)
            }
            
            # Cache the result
            cache_key = f"journal_analysis_{user_id}_{hash(entry_text)}"
            self._cache_result(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in journal entry analysis: {str(e)}")
            return self._error_response("journal_analysis_error", str(e))
    
    async def analyze_user_patterns(self, user_id: str, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user behavioral patterns and generate insights.
        """
        try:
            cache_key = f"pattern_analysis_{user_id}"
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
            
            # Run behavioral pattern analysis
            pattern_result = await self._run_in_executor(
                behavioral_analyzer.analyze_patterns, user_data
            )
            
            # Add user-specific context
            pattern_result['user_id'] = user_id
            pattern_result['data_points'] = len(user_data)
            
            # Cache the result
            self._cache_result(cache_key, pattern_result)
            
            return pattern_result
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
            return self._error_response("pattern_analysis_error", str(e))
    
    async def predict_mood(self, user_id: str, current_context: Dict[str, Any], historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predict user's future mood based on current context and historical patterns.
        """
        try:
            # Train model if we have sufficient historical data
            if historical_data and len(historical_data) >= 10:
                await self._run_in_executor(mood_predictor.train, historical_data)
            
            # Make prediction
            prediction_result = await self._run_in_executor(
                mood_predictor.predict_mood, current_context
            )
            
            # Add context
            prediction_result['user_id'] = user_id
            prediction_result['context'] = current_context
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error in mood prediction: {str(e)}")
            return self._error_response("mood_prediction_error", str(e))
    
    async def generate_personalized_recommendations(self, user_id: str, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on analysis results.
        """
        try:
            recommendations = []
            
            # Extract key insights
            sentiment = analysis_results.get('entry_analysis', {}).get('sentiment', {})
            risk_level = analysis_results.get('entry_analysis', {}).get('risk_assessment', {}).get('level', 'minimal')
            patterns = analysis_results.get('patterns', {})
            
            # Crisis recommendations (highest priority)
            if analysis_results.get('crisis_assessment', {}).get('is_crisis', False):
                recommendations.extend(self._get_crisis_recommendations())
            
            # Mental health specific recommendations
            elif risk_level in ['moderate', 'high']:
                recommendations.extend(self._get_mental_health_recommendations(risk_level))
            
            # Pattern-based recommendations
            if patterns:
                recommendations.extend(self._get_pattern_recommendations(patterns))
            
            # General wellness recommendations
            recommendations.extend(self._get_wellness_recommendations(sentiment))
            
            # Personalize and rank recommendations
            personalized_recs = self._personalize_recommendations(user_id, recommendations)
            
            return personalized_recs[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def detect_concerning_patterns(self, user_id: str, recent_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect concerning patterns that might require intervention.
        """
        try:
            concerning_patterns = {
                'declining_mood_trend': False,
                'increased_crisis_indicators': False,
                'social_isolation_signs': False,
                'sleep_pattern_disruption': False,
                'decreased_engagement': False
            }
            
            if len(recent_entries) < 3:
                return {'patterns': concerning_patterns, 'severity': 'insufficient_data'}
            
            # Analyze mood trend
            mood_scores = [entry.get('sentiment_score', 0.0) for entry in recent_entries]
            if len(mood_scores) > 1:
                trend = self._calculate_trend(mood_scores)
                concerning_patterns['declining_mood_trend'] = trend < -0.2
            
            # Check for crisis indicators
            crisis_count = sum(1 for entry in recent_entries 
                             if entry.get('crisis_detected', False))
            concerning_patterns['increased_crisis_indicators'] = crisis_count > 0
            
            # Analyze social references
            social_mentions = sum(1 for entry in recent_entries 
                                if any(word in entry.get('content', '').lower() 
                                      for word in ['friends', 'family', 'social', 'together']))
            concerning_patterns['social_isolation_signs'] = social_mentions == 0 and len(recent_entries) > 5
            
            # Calculate overall severity
            severity_score = sum(1 for pattern in concerning_patterns.values() if pattern)
            severity = 'high' if severity_score >= 3 else 'moderate' if severity_score >= 2 else 'low'
            
            return {
                'user_id': user_id,
                'patterns': concerning_patterns,
                'severity': severity,
                'analysis_period': '7_days',
                'requires_intervention': severity in ['high', 'moderate'],
                'detected_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting concerning patterns: {str(e)}")
            return self._error_response("pattern_detection_error", str(e))
    
    async def get_ml_insights_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive ML insights for user dashboard.
        """
        try:
            dashboard = {
                'user_id': user_id,
                'generated_at': datetime.utcnow().isoformat(),
                'insights': {
                    'mood_summary': await self._get_mood_summary(user_id),
                    'pattern_insights': await self._get_pattern_insights(user_id),
                    'risk_assessment': await self._get_risk_assessment(user_id),
                    'progress_tracking': await self._get_progress_tracking(user_id),
                    'recommendations': await self._get_dashboard_recommendations(user_id)
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating ML insights dashboard: {str(e)}")
            return self._error_response("dashboard_error", str(e))
    
    # Helper methods
    
    async def _run_in_executor(self, func, *args):
        """Run a function in a thread executor to avoid blocking the event loop."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    def _cache_result(self, key: str, result: Dict[str, Any]):
        """Cache a result with TTL."""
        self.cache[key] = {
            'data': result,
            'timestamp': datetime.utcnow()
        }
    
    def _get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if still valid."""
        if key in self.cache:
            cached = self.cache[key]
            if (datetime.utcnow() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
            else:
                del self.cache[key]
        return None
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for a series of values."""
        try:
            import numpy as np
            if len(values) < 2:
                return 0.0
            return float(np.polyfit(range(len(values)), values, 1)[0])
        except:
            # Fallback calculation without numpy
            if len(values) < 2:
                return 0.0
            return (values[-1] - values[0]) / len(values)
    
    def _get_crisis_recommendations(self) -> List[Dict[str, Any]]:
        """Get crisis-specific recommendations."""
        return [
            {
                'type': 'crisis_intervention',
                'priority': 'urgent',
                'title': 'Immediate Professional Help',
                'description': 'Contact a mental health professional or crisis helpline immediately',
                'action': 'contact_crisis_line',
                'resources': ['988', 'Crisis Text Line: Text HOME to 741741']
            },
            {
                'type': 'safety_planning',
                'priority': 'high',
                'title': 'Safety Planning',
                'description': 'Create a safety plan with coping strategies and support contacts',
                'action': 'create_safety_plan'
            }
        ]
    
    def _get_mental_health_recommendations(self, risk_level: str) -> List[Dict[str, Any]]:
        """Get mental health specific recommendations."""
        base_recs = [
            {
                'type': 'professional_support',
                'priority': 'high' if risk_level == 'high' else 'medium',
                'title': 'Professional Support',
                'description': 'Consider speaking with a mental health professional',
                'action': 'find_therapist'
            },
            {
                'type': 'coping_strategies',
                'priority': 'medium',
                'title': 'Coping Techniques',
                'description': 'Practice evidence-based coping strategies',
                'action': 'access_coping_tools'
            }
        ]
        return base_recs
    
    def _get_pattern_recommendations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations based on behavioral patterns."""
        recommendations = []
        
        frequency = patterns.get('frequency_analysis', {})
        if frequency.get('consistency_score', 0) < 0.5:
            recommendations.append({
                'type': 'habit_building',
                'priority': 'medium',
                'title': 'Build Consistent Habits',
                'description': 'Establish a regular journaling routine',
                'action': 'set_reminders'
            })
        
        return recommendations
    
    def _get_wellness_recommendations(self, sentiment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get general wellness recommendations."""
        return [
            {
                'type': 'mindfulness',
                'priority': 'low',
                'title': 'Mindfulness Practice',
                'description': 'Try a 5-minute mindfulness meditation',
                'action': 'start_meditation'
            },
            {
                'type': 'physical_activity',
                'priority': 'low',
                'title': 'Physical Activity',
                'description': 'Take a short walk or do light exercise',
                'action': 'track_activity'
            }
        ]
    
    def _personalize_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Personalize recommendations based on user preferences and history."""
        # In a real implementation, this would use user preference data
        # For now, we'll just rank by priority
        priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        return sorted(recommendations, 
                     key=lambda x: priority_order.get(x.get('priority', 'low'), 0), 
                     reverse=True)
    
    async def _get_mood_summary(self, user_id: str) -> Dict[str, Any]:
        """Get mood summary for dashboard."""
        # Placeholder - would fetch actual user data
        return {
            'current_mood': 'neutral',
            'trend': 'stable',
            'weekly_average': 3.2,
            'mood_variance': 0.8
        }
    
    async def _get_pattern_insights(self, user_id: str) -> List[str]:
        """Get pattern insights for dashboard."""
        return [
            "You tend to journal more frequently on weekends",
            "Your mood is generally more positive in the morning",
            "You've been consistent with your journaling habit this week"
        ]
    
    async def _get_risk_assessment(self, user_id: str) -> Dict[str, Any]:
        """Get risk assessment for dashboard."""
        return {
            'current_level': 'low',
            'trending': 'stable',
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def _get_progress_tracking(self, user_id: str) -> Dict[str, Any]:
        """Get progress tracking data for dashboard."""
        return {
            'streak_days': 7,
            'total_entries': 23,
            'improvement_score': 0.75,
            'goals_met': 3,
            'goals_total': 4
        }
    
    async def _get_dashboard_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recommendations for dashboard."""
        return [
            {
                'title': 'Continue Your Streak',
                'description': 'You\'re doing great! Keep up your daily journaling habit.',
                'type': 'encouragement'
            },
            {
                'title': 'Try Gratitude Journaling',
                'description': 'Consider adding three things you\'re grateful for to today\'s entry.',
                'type': 'technique_suggestion'
            }
        ]
    
    def _error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'error': True,
            'error_type': error_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }

# Initialize the ML service
ml_service = MLService()
