"""
ML Configuration and Model Management
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(Enum):
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    EMOTION_DETECTION = "emotion_detection"
    CRISIS_DETECTION = "crisis_detection"
    MOOD_PREDICTION = "mood_prediction"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class ModelConfig:
    name: str
    model_type: ModelType
    model_path: str
    tokenizer_path: Optional[str] = None
    config_path: Optional[str] = None
    version: str = "1.0.0"
    is_active: bool = True
    requires_gpu: bool = False
    max_sequence_length: int = 512
    batch_size: int = 32

class MLConfig:
    """
    Centralized configuration for ML models and services.
    """
    
    def __init__(self):
        self.base_model_dir = Path(os.getenv("ML_MODEL_DIR", "./models"))
        self.cache_dir = Path(os.getenv("ML_CACHE_DIR", "./cache"))
        self.logs_dir = Path(os.getenv("ML_LOGS_DIR", "./logs"))
        
        # Create directories if they don't exist
        self.base_model_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.models = self._initialize_model_configs()
        
        # ML service settings
        self.max_workers = int(os.getenv("ML_MAX_WORKERS", "4"))
        self.cache_ttl_seconds = int(os.getenv("ML_CACHE_TTL", "300"))  # 5 minutes
        self.enable_gpu = os.getenv("ML_ENABLE_GPU", "false").lower() == "true"
        
        # Crisis detection settings
        self.crisis_threshold = float(os.getenv("CRISIS_THRESHOLD", "0.7"))
        self.auto_alert_enabled = os.getenv("AUTO_ALERT_ENABLED", "true").lower() == "true"
        
        # Model training settings
        self.min_training_samples = int(os.getenv("MIN_TRAINING_SAMPLES", "50"))
        self.model_update_interval_hours = int(os.getenv("MODEL_UPDATE_INTERVAL", "24"))
        
        # Feature extraction settings
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "2048"))
        self.feature_cache_size = int(os.getenv("FEATURE_CACHE_SIZE", "1000"))
    
    def _initialize_model_configs(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations."""
        configs = {}
        
        # Sentiment Analysis Model
        configs["sentiment_roberta"] = ModelConfig(
            name="Mental Health Sentiment Analyzer",
            model_type=ModelType.SENTIMENT_ANALYSIS,
            model_path="cardiffnlp/twitter-roberta-base-sentiment-latest",
            version="2.0.0",
            max_sequence_length=512
        )
        
        # Emotion Detection Model
        configs["emotion_distilroberta"] = ModelConfig(
            name="Emotion Detection Model",
            model_type=ModelType.EMOTION_DETECTION,
            model_path="j-hartmann/emotion-english-distilroberta-base",
            version="1.5.0",
            max_sequence_length=512
        )
        
        # Mental Health Specific Model (if available)
        configs["mental_health_bert"] = ModelConfig(
            name="Mental Health BERT",
            model_type=ModelType.CRISIS_DETECTION,
            model_path="mental/mental-bert-base-uncased",  # Hypothetical specialized model
            version="1.0.0",
            is_active=False,  # Enable when available
            max_sequence_length=512
        )
        
        # Custom Crisis Detection Model
        configs["crisis_detector"] = ModelConfig(
            name="Crisis Detection Model",
            model_type=ModelType.CRISIS_DETECTION,
            model_path=str(self.base_model_dir / "crisis_detector"),
            version="1.0.0",
            is_active=True
        )
        
        # Mood Prediction Model
        configs["mood_predictor"] = ModelConfig(
            name="Mood Prediction Model",
            model_type=ModelType.MOOD_PREDICTION,
            model_path=str(self.base_model_dir / "mood_predictor"),
            version="1.0.0",
            is_active=True
        )
        
        return configs
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        return self.models.get(model_name)
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelConfig]:
        """Get all models of a specific type."""
        return [config for config in self.models.values() 
                if config.model_type == model_type and config.is_active]
    
    def get_active_models(self) -> List[ModelConfig]:
        """Get all active models."""
        return [config for config in self.models.values() if config.is_active]

class FeatureConfig:
    """
    Configuration for feature extraction and processing.
    """
    
    # Text preprocessing settings
    TEXT_PREPROCESSING = {
        "remove_urls": True,
        "remove_mentions": True,
        "remove_hashtags": False,
        "normalize_whitespace": True,
        "lowercase": True,
        "remove_punctuation": False,
        "remove_numbers": False,
        "min_length": 10,
        "max_length": 2048
    }
    
    # Sentiment analysis features
    SENTIMENT_FEATURES = {
        "polarity": True,
        "subjectivity": True,
        "compound_score": True,
        "positive_ratio": True,
        "negative_ratio": True,
        "neutral_ratio": True
    }
    
    # Linguistic features
    LINGUISTIC_FEATURES = {
        "word_count": True,
        "sentence_count": True,
        "avg_sentence_length": True,
        "lexical_diversity": True,
        "readability_score": True,
        "emotional_intensity": True
    }
    
    # Temporal features
    TEMPORAL_FEATURES = {
        "hour_of_day": True,
        "day_of_week": True,
        "is_weekend": True,
        "time_since_last_entry": True,
        "entry_frequency": True
    }
    
    # Behavioral features
    BEHAVIORAL_FEATURES = {
        "session_duration": True,
        "typing_speed": True,
        "pause_patterns": True,
        "edit_frequency": True,
        "completion_rate": True
    }
    
    # Mental health specific features
    MENTAL_HEALTH_FEATURES = {
        "anxiety_keywords": True,
        "depression_keywords": True,
        "crisis_keywords": True,
        "positive_coping": True,
        "social_support": True,
        "hope_statements": True
    }

class AlertConfig:
    """
    Configuration for crisis alerts and interventions.
    """
    
    # Risk level thresholds
    RISK_THRESHOLDS = {
        "minimal": 0.0,
        "low": 0.3,
        "moderate": 0.5,
        "high": 0.7,
        "crisis": 0.85
    }
    
    # Alert channels
    ALERT_CHANNELS = {
        "email": True,
        "sms": True,
        "push_notification": True,
        "dashboard_alert": True,
        "emergency_contact": False  # Only for highest risk
    }
    
    # Response timeframes (in minutes)
    RESPONSE_TIMEFRAMES = {
        "crisis": 5,      # Immediate response required
        "high": 30,       # Response within 30 minutes
        "moderate": 120,  # Response within 2 hours
        "low": 1440       # Response within 24 hours
    }
    
    # Crisis resources
    CRISIS_RESOURCES = [
        {
            "name": "National Suicide Prevention Lifeline",
            "phone": "988",
            "text": "Text 'HELLO' to 741741",
            "website": "https://suicidepreventionlifeline.org/",
            "availability": "24/7",
            "languages": ["English", "Spanish"]
        },
        {
            "name": "Crisis Text Line",
            "phone": None,
            "text": "Text 'HOME' to 741741",
            "website": "https://www.crisistextline.org/",
            "availability": "24/7",
            "languages": ["English", "Spanish"]
        }
    ]

class ModelPerformanceConfig:
    """
    Configuration for model performance monitoring and evaluation.
    """
    
    # Performance metrics to track
    METRICS = {
        "accuracy": True,
        "precision": True,
        "recall": True,
        "f1_score": True,
        "auc_roc": True,
        "confusion_matrix": True,
        "response_time": True,
        "throughput": True
    }
    
    # Evaluation intervals
    EVALUATION_SCHEDULE = {
        "real_time_monitoring": True,
        "daily_summary": True,
        "weekly_detailed_report": True,
        "monthly_model_review": True
    }
    
    # Performance thresholds for alerts
    PERFORMANCE_THRESHOLDS = {
        "min_accuracy": 0.80,
        "min_precision": 0.75,
        "min_recall": 0.70,
        "max_response_time_ms": 1000,
        "min_throughput_per_second": 10
    }
    
    # A/B testing configuration
    AB_TESTING = {
        "enabled": True,
        "traffic_split": 0.1,  # 10% of traffic for new model testing
        "min_sample_size": 100,
        "max_test_duration_days": 7
    }

# Global configuration instances
ml_config = MLConfig()
feature_config = FeatureConfig()
alert_config = AlertConfig()
performance_config = ModelPerformanceConfig()

def get_ml_config() -> MLConfig:
    """Get the global ML configuration."""
    return ml_config

def get_feature_config() -> FeatureConfig:
    """Get the global feature configuration."""
    return feature_config

def get_alert_config() -> AlertConfig:
    """Get the global alert configuration."""
    return alert_config

def get_performance_config() -> ModelPerformanceConfig:
    """Get the global performance configuration."""
    return performance_config
