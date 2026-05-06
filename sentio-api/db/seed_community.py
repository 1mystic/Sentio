"""
Seed the community_topics table with default topics.
Run once: python sentio-api/db/seed_community.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import get_supabase

TOPICS = [
    {
        "title": "Bias Spotting",
        "slug": "bias-spotting",
        "description": "Share examples of biases you've caught in your own thinking this week.",
        "icon": "Eye",
        "color": "#9b94e8",
    },
    {
        "title": "Decision Help",
        "slug": "decision-help",
        "description": "Get perspective from the community on decisions you're wrestling with.",
        "icon": "Scale",
        "color": "#f59e0b",
    },
    {
        "title": "Journal Prompts",
        "slug": "journal-prompts",
        "description": "Share prompts that sparked meaningful reflection for you.",
        "icon": "BookOpen",
        "color": "#10b981",
    },
    {
        "title": "Wins & Breakthroughs",
        "slug": "wins",
        "description": "Celebrate moments when you caught a bias before it affected a decision.",
        "icon": "Zap",
        "color": "#ec4899",
    },
    {
        "title": "Questions & Confusion",
        "slug": "questions",
        "description": "Ask anything about cognitive biases, psychology, or how Sentio works.",
        "icon": "HelpCircle",
        "color": "#6366f1",
    },
]

def seed():
    supabase = get_supabase()
    for topic in TOPICS:
        existing = supabase.table("community_topics").select("id").eq("slug", topic["slug"]).execute()
        if existing.data:
            print(f"  skip (exists): {topic['slug']}")
            continue
        supabase.table("community_topics").insert(topic).execute()
        print(f"  inserted: {topic['slug']}")
    print("Done.")

if __name__ == "__main__":
    seed()
