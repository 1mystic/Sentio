"""Seed validated assessments into the assessments table.

Usage:
    python db/seed_assessments.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import get_supabase

LIKERT5 = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LIKERT5_FREQ = ["Never", "Rarely", "Sometimes", "Often", "Always"]
LIKERT5_AGREE = ["Strongly Disagree", "Disagree", "Somewhat Disagree", "Somewhat Agree", "Agree", "Strongly Agree"]

ASSESSMENTS = [
    # ─────────────────────────────────────────────
    # 1. Cognitive Bias Inventory (custom, 15 Qs)
    # ─────────────────────────────────────────────
    {
        "slug": "cognitive-bias-inventory",
        "title": "Cognitive Bias Inventory",
        "description": (
            "A 15-item screening tool that identifies susceptibility across five key "
            "cognitive bias clusters: confirmation, anchoring, availability, overconfidence, "
            "and social conformity. Takes approximately 8 minutes."
        ),
        "validated_tool": "Sentio CBI (custom)",
        "research_citation": (
            "Items adapted from Cognitive Bias Questionnaire (Hamlin & Hamlin, 2018) "
            "and the Bias in Reasoning Scale (Bruine de Bruin et al., 2007)."
        ),
        "questions": [
            {
                "id": 1,
                "text": "When I research a topic, I tend to look for sources that agree with what I already think.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "confirmation_bias",
            },
            {
                "id": 2,
                "text": "I find it difficult to change my opinion on a topic even when presented with strong counter-evidence.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "confirmation_bias",
            },
            {
                "id": 3,
                "text": "I actively seek out viewpoints that challenge my existing beliefs.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": "confirmation_bias",
            },
            {
                "id": 4,
                "text": "The first price I see for something strongly influences what I consider a fair price later.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "anchoring_bias",
            },
            {
                "id": 5,
                "text": "When negotiating, the initial number mentioned tends to pull my final agreement in its direction.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "anchoring_bias",
            },
            {
                "id": 6,
                "text": "I can easily ignore the first option I'm shown and evaluate each option on its own merits.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": "anchoring_bias",
            },
            {
                "id": 7,
                "text": "After hearing news stories about a type of accident, I start to believe that type of accident is more common than it actually is.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "availability_heuristic",
            },
            {
                "id": 8,
                "text": "Dramatic or emotional stories influence my sense of how likely an event is, even when I know statistics tell a different story.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "availability_heuristic",
            },
            {
                "id": 9,
                "text": "I rely on statistics and data rather than memorable stories when estimating how common something is.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": "availability_heuristic",
            },
            {
                "id": 10,
                "text": "I am confident that my judgements are more accurate than those of most people around me.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "overconfidence_bias",
            },
            {
                "id": 11,
                "text": "I rarely find out that I was more wrong about something than I expected to be.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "overconfidence_bias",
            },
            {
                "id": 12,
                "text": "I regularly acknowledge uncertainty in my predictions and factor in the chance I am wrong.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": "overconfidence_bias",
            },
            {
                "id": 13,
                "text": "When many people around me hold a certain opinion, I find it hard not to adopt that opinion myself.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "bandwagon_effect",
            },
            {
                "id": 14,
                "text": "I have changed my publicly stated position on something mainly because others disagreed with me, even though I hadn't been given new evidence.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": "bandwagon_effect",
            },
            {
                "id": 15,
                "text": "I feel comfortable holding an opinion that is unpopular among my peers if I believe the evidence supports it.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": "bandwagon_effect",
            },
        ],
        "scoring_algorithm": {
            "method": "sum",
            "max_score": 75,
            "reverse_items": [3, 6, 9, 12, 15],
            "subscales": {
                "confirmation": [1, 2, 3],
                "anchoring": [4, 5, 6],
                "availability": [7, 8, 9],
                "overconfidence": [10, 11, 12],
                "social_conformity": [13, 14, 15],
            },
            "interpretation": {
                "low": {"range": [0, 25], "label": "Low susceptibility", "description": "You show strong resistance to these common cognitive biases."},
                "medium": {"range": [26, 50], "label": "Moderate susceptibility", "description": "You are affected by some of these biases in certain contexts."},
                "high": {"range": [51, 75], "label": "High susceptibility", "description": "These biases appear to have a significant influence on your thinking patterns."},
            },
        },
        "target_biases": [
            "confirmation-bias",
            "anchoring-bias",
            "availability-heuristic",
            "overconfidence-bias",
            "bandwagon-effect",
        ],
        "estimated_minutes": 8,
        "category": "general",
    },

    # ─────────────────────────────────────────────
    # 2. Need for Cognition Scale (NCS — short form, 12 Qs)
    # ─────────────────────────────────────────────
    {
        "slug": "need-for-cognition-scale",
        "title": "Need for Cognition Scale",
        "description": (
            "A validated 12-item short form of the Need for Cognition Scale (NCS-18) "
            "measuring the extent to which individuals enjoy and are motivated to engage "
            "in effortful thinking. Higher scores indicate greater intrinsic motivation "
            "to think deeply. Takes approximately 7 minutes."
        ),
        "validated_tool": "NCS-18 Short Form (Cacioppo & Petty, adapted)",
        "research_citation": (
            "Cacioppo, J. T., & Petty, R. E. (1982). The need for cognition. "
            "Journal of Personality and Social Psychology, 42(1), 116–131. "
            "Short form adapted from Cacioppo et al. (1984)."
        ),
        "questions": [
            {
                "id": 1,
                "text": "I would prefer complex to simple problems.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": None,
            },
            {
                "id": 2,
                "text": "I like to have the responsibility of handling a situation that requires a lot of thinking.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": None,
            },
            {
                "id": 3,
                "text": "Thinking is not my idea of fun.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 4,
                "text": "I would rather do something that requires little thought than something that is sure to challenge my thinking abilities.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 5,
                "text": "I try to anticipate and avoid situations where there is likely a chance I will have to think in depth about something.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 6,
                "text": "I find satisfaction in deliberating hard and for long hours.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": None,
            },
            {
                "id": 7,
                "text": "I only think as hard as I have to.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 8,
                "text": "I prefer to think about small, daily projects to long-term ones.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 9,
                "text": "I like tasks that require little thought once I have learned them.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
            {
                "id": 10,
                "text": "The idea of relying on thought to make my way to the top appeals to me.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": None,
            },
            {
                "id": 11,
                "text": "I really enjoy a task that involves coming up with new solutions to problems.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": False,
                "bias_signal": None,
            },
            {
                "id": 12,
                "text": "Learning new ways to think doesn't excite me very much.",
                "type": "likert5",
                "options": LIKERT5,
                "reverse_scored": True,
                "bias_signal": None,
            },
        ],
        "scoring_algorithm": {
            "method": "sum",
            "max_score": 60,
            "reverse_items": [3, 4, 5, 7, 8, 9, 12],
            "subscales": {
                "engagement": [1, 2, 6, 10, 11],
                "avoidance": [3, 4, 5, 7, 8, 9, 12],
            },
            "interpretation": {
                "low": {"range": [12, 32], "label": "Low need for cognition", "description": "You tend to prefer intuitive, quick thinking and may be more susceptible to heuristic-driven biases."},
                "medium": {"range": [33, 45], "label": "Moderate need for cognition", "description": "You engage in deliberate thinking selectively depending on context and motivation."},
                "high": {"range": [46, 60], "label": "High need for cognition", "description": "You actively enjoy and seek out cognitively demanding tasks and deep analytical thinking."},
            },
        },
        "target_biases": [
            "confirmation-bias",
            "availability-heuristic",
            "emotional-reasoning",
        ],
        "estimated_minutes": 7,
        "category": "cognitive_style",
    },

    # ─────────────────────────────────────────────
    # 3. Metacognitive Awareness Inventory (MAI — short form, 15 Qs)
    # ─────────────────────────────────────────────
    {
        "slug": "metacognitive-awareness-inventory",
        "title": "Metacognitive Awareness Inventory",
        "description": (
            "A 15-item short form of the Metacognitive Awareness Inventory (MAI) "
            "measuring two broad components of metacognition: knowledge about cognition "
            "(what you know about how you think) and regulation of cognition (how well "
            "you monitor and control your thinking). Takes approximately 9 minutes."
        ),
        "validated_tool": "MAI Short Form (Schraw & Dennison, 1994, adapted)",
        "research_citation": (
            "Schraw, G., & Dennison, R. S. (1994). Assessing metacognitive awareness. "
            "Contemporary Educational Psychology, 19(4), 460–475."
        ),
        "questions": [
            {
                "id": 1,
                "text": "I know what kind of information is most important to learn.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "metacognitive_knowledge",
            },
            {
                "id": 2,
                "text": "I understand my intellectual strengths and weaknesses.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "metacognitive_knowledge",
            },
            {
                "id": 3,
                "text": "I know how to organise information effectively.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "metacognitive_knowledge",
            },
            {
                "id": 4,
                "text": "I think about what I really need to learn before I begin a task.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "metacognitive_knowledge",
            },
            {
                "id": 5,
                "text": "I set specific goals before I begin a task.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "planning_regulation",
            },
            {
                "id": 6,
                "text": "I consider several alternatives to a problem before I answer.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "planning_regulation",
            },
            {
                "id": 7,
                "text": "I ask myself periodically if I am meeting my goals.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "monitoring_regulation",
            },
            {
                "id": 8,
                "text": "I monitor my thinking when I am working on a problem.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "monitoring_regulation",
            },
            {
                "id": 9,
                "text": "I notice when I make errors in reasoning.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "monitoring_regulation",
            },
            {
                "id": 10,
                "text": "I can motivate myself to learn when I need to.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "monitoring_regulation",
            },
            {
                "id": 11,
                "text": "I stop and re-read information when I don't understand it.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "evaluation_regulation",
            },
            {
                "id": 12,
                "text": "I change strategies when I realise I am not making progress toward a goal.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "evaluation_regulation",
            },
            {
                "id": 13,
                "text": "I review what I have learned after a task to check my understanding.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "evaluation_regulation",
            },
            {
                "id": 14,
                "text": "I summarise what I have learned after finishing a piece of work.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "evaluation_regulation",
            },
            {
                "id": 15,
                "text": "I learn more from my mistakes when I take time to analyse them.",
                "type": "likert5",
                "options": LIKERT5_FREQ,
                "reverse_scored": False,
                "bias_signal": "evaluation_regulation",
            },
        ],
        "scoring_algorithm": {
            "method": "sum",
            "max_score": 75,
            "reverse_items": [],
            "subscales": {
                "knowledge_of_cognition": [1, 2, 3, 4],
                "planning": [5, 6],
                "monitoring": [7, 8, 9, 10],
                "evaluation": [11, 12, 13, 14, 15],
            },
            "interpretation": {
                "low": {"range": [15, 35], "label": "Low metacognitive awareness", "description": "You may have limited insight into your own thinking processes, making you more vulnerable to unexamined cognitive biases."},
                "medium": {"range": [36, 55], "label": "Moderate metacognitive awareness", "description": "You have a reasonable level of self-awareness about your thinking and can improve further with practice."},
                "high": {"range": [56, 75], "label": "High metacognitive awareness", "description": "You actively monitor and regulate your own thinking, which provides a strong foundation for debiasing."},
            },
        },
        "target_biases": [
            "overconfidence-bias",
            "blind-spot-bias",
            "dunning-kruger-effect",
            "hindsight-bias",
        ],
        "estimated_minutes": 9,
        "category": "metacognition",
    },
]


def main() -> None:
    supabase = get_supabase()
    result = (
        supabase.table("assessments")
        .upsert(ASSESSMENTS, on_conflict="slug")
        .execute()
    )
    count = len(result.data) if result.data else 0
    print(f"Seeded {count} assessments successfully.")


if __name__ == "__main__":
    main()
