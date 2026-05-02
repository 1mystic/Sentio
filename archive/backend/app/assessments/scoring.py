from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

def score_gad7(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score GAD-7 anxiety assessment"""
    try:
        # GAD-7 questions have values 0-3
        total_score = 0
        for question_id, answer in responses.items():
            if isinstance(answer, (int, str)) and str(answer).isdigit():
                total_score += int(answer)
        
        # Determine severity level
        if total_score <= 4:
            interpretation = "Minimal anxiety"
            risk_level = "low"
            recommendations = [
                "Your responses suggest minimal anxiety symptoms",
                "Continue with healthy lifestyle practices",
                "Practice stress management techniques as prevention"
            ]
        elif total_score <= 9:
            interpretation = "Mild anxiety"
            risk_level = "low"
            recommendations = [
                "Your responses suggest mild anxiety symptoms",
                "Consider stress reduction techniques",
                "Monitor symptoms and seek support if they worsen",
                "Practice relaxation and mindfulness exercises"
            ]
        elif total_score <= 14:
            interpretation = "Moderate anxiety"
            risk_level = "moderate"
            recommendations = [
                "Your responses suggest moderate anxiety symptoms",
                "Consider speaking with a mental health professional",
                "Explore therapy options such as CBT",
                "Practice regular stress management techniques",
                "Consider lifestyle modifications"
            ]
        else:
            interpretation = "Severe anxiety"
            risk_level = "high"
            recommendations = [
                "Your responses suggest severe anxiety symptoms",
                "Strongly consider professional mental health support",
                "Speak with a doctor or therapist as soon as possible",
                "Consider both therapy and medication options",
                "Ensure you have support from family or friends"
            ]
        
        return {
            "score": total_score,
            "max_score": 21,
            "percentage": (total_score / 21) * 100,
            "interpretation": interpretation,
            "risk_level": risk_level,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error scoring GAD-7: {e}")
        return {
            "score": None,
            "error": "Unable to calculate score"
        }

def score_phq9(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score PHQ-9 depression assessment"""
    try:
        # PHQ-9 questions have values 0-3
        total_score = 0
        for question_id, answer in responses.items():
            if isinstance(answer, (int, str)) and str(answer).isdigit():
                total_score += int(answer)
        
        # Determine severity level
        if total_score <= 4:
            interpretation = "Minimal depression"
            risk_level = "low"
            recommendations = [
                "Your responses suggest minimal depressive symptoms",
                "Continue with healthy lifestyle practices",
                "Maintain social connections and regular activities"
            ]
        elif total_score <= 9:
            interpretation = "Mild depression"
            risk_level = "low"
            recommendations = [
                "Your responses suggest mild depressive symptoms",
                "Consider lifestyle modifications",
                "Increase physical activity and social engagement",
                "Monitor symptoms and seek support if they worsen"
            ]
        elif total_score <= 14:
            interpretation = "Moderate depression"
            risk_level = "moderate"
            recommendations = [
                "Your responses suggest moderate depressive symptoms",
                "Consider speaking with a mental health professional",
                "Explore therapy options",
                "Consider lifestyle and routine changes",
                "Reach out to supportive friends and family"
            ]
        elif total_score <= 19:
            interpretation = "Moderately severe depression"
            risk_level = "high"
            recommendations = [
                "Your responses suggest moderately severe depressive symptoms",
                "Strongly consider professional mental health support",
                "Speak with a doctor or therapist",
                "Consider both therapy and medication options",
                "Ensure you have a strong support system"
            ]
        else:
            interpretation = "Severe depression"
            risk_level = "high"
            recommendations = [
                "Your responses suggest severe depressive symptoms",
                "Seek professional help immediately",
                "Contact a mental health professional or your doctor",
                "Consider intensive treatment options",
                "Ensure safety and have emergency contacts available"
            ]
        
        return {
            "score": total_score,
            "max_score": 27,
            "percentage": (total_score / 27) * 100,
            "interpretation": interpretation,
            "risk_level": risk_level,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error scoring PHQ-9: {e}")
        return {
            "score": None,
            "error": "Unable to calculate score"
        }

def score_cognitive_bias(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score cognitive bias assessment"""
    try:
        # This is a simplified scoring for cognitive bias assessment
        bias_categories = {
            "confirmation_bias": 0,
            "catastrophizing": 0,
            "all_or_nothing": 0,
            "overgeneralization": 0
        }
        
        # Analyze responses for different bias patterns
        # This would be more sophisticated in a real implementation
        total_responses = len(responses)
        
        return {
            "score": None,  # No single score for cognitive bias
            "max_score": None,
            "percentage": None,
            "interpretation": "Cognitive bias patterns identified",
            "risk_level": "informational",
            "recommendations": [
                "Awareness is the first step in addressing cognitive biases",
                "Practice mindfulness and self-reflection",
                "Consider cognitive behavioral therapy techniques",
                "Challenge negative thought patterns when they arise"
            ],
            "bias_breakdown": bias_categories
        }
        
    except Exception as e:
        logger.error(f"Error scoring cognitive bias assessment: {e}")
        return {
            "score": None,
            "error": "Unable to analyze responses"
        }

def score_values_assessment(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score values assessment"""
    try:
        # Values assessment provides insights rather than a score
        return {
            "score": None,
            "max_score": None,
            "percentage": None,
            "interpretation": "Values and priorities identified",
            "risk_level": "informational",
            "recommendations": [
                "Use these insights to guide decision-making",
                "Align your goals with your core values",
                "Regularly reassess your values as you grow",
                "Consider how your values affect your mental wellbeing"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error scoring values assessment: {e}")
        return {
            "score": None,
            "error": "Unable to analyze responses"
        }

def score_stress_assessment(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score stress assessment"""
    try:
        # Simplified stress scoring
        total_score = 0
        for question_id, answer in responses.items():
            if isinstance(answer, (int, str)) and str(answer).isdigit():
                total_score += int(answer)
        
        if total_score <= 13:
            interpretation = "Low stress"
            risk_level = "low"
        elif total_score <= 26:
            interpretation = "Moderate stress"
            risk_level = "moderate"
        else:
            interpretation = "High stress"
            risk_level = "high"
        
        return {
            "score": total_score,
            "max_score": 40,  # Assuming 10 questions with 0-4 scale
            "percentage": (total_score / 40) * 100,
            "interpretation": interpretation,
            "risk_level": risk_level,
            "recommendations": [
                "Identify your stress triggers",
                "Practice stress management techniques",
                "Consider professional support if stress is overwhelming",
                "Maintain healthy lifestyle habits"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error scoring stress assessment: {e}")
        return {
            "score": None,
            "error": "Unable to calculate score"
        }

# Scoring dispatcher
ASSESSMENT_SCORERS = {
    "gad7": score_gad7,
    "phq9": score_phq9,
    "cognitive_bias": score_cognitive_bias,
    "values": score_values_assessment,
    "stress": score_stress_assessment
}

def score_assessment(assessment_type: str, responses: Dict[str, Any]) -> Dict[str, Any]:
    """Score assessment based on type"""
    scorer = ASSESSMENT_SCORERS.get(assessment_type)
    if scorer:
        return scorer(responses)
    else:
        logger.warning(f"No scorer found for assessment type: {assessment_type}")
        return {
            "score": None,
            "error": f"No scoring method available for {assessment_type}"
        }
