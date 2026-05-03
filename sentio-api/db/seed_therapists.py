"""Seed 20 fictional but realistic Indian therapist profiles.

Usage:
    python db/seed_therapists.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import get_supabase

THERAPISTS = [
    {
        "name": "Dr. Priya Sharma",
        "initials": "PS",
        "credentials": ["M.Sc. Clinical Psychology", "NIMHANS Certified", "RCI Licensed"],
        "specializations": ["CBT", "Anxiety Disorders", "Cognitive Biases", "Work Stress"],
        "languages": ["English", "Hindi"],
        "bio": (
            "Dr. Priya Sharma has 8 years of experience helping professionals in Bangalore "
            "navigate anxiety, burnout, and distorted thinking patterns. She trained at "
            "NIMHANS and has worked extensively with clients in the tech industry. Her "
            "research focus is on how confirmation bias shapes decision-making in high-stakes "
            "work environments."
        ),
        "approach": (
            "I use evidence-based CBT techniques combined with mindfulness-based cognitive "
            "therapy (MBCT) to help clients identify and restructure unhelpful thinking "
            "patterns. Sessions are collaborative, structured, and goal-directed."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 800, "max": 1200, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 47,
        "experience_years": 8,
    },
    {
        "name": "Dr. Arjun Mehta",
        "initials": "AM",
        "credentials": ["M.D. Psychiatry", "DPM", "Fellow AIIMS Delhi"],
        "specializations": ["Depression", "OCD", "Loss Aversion", "Decision-Making Disorders"],
        "languages": ["English", "Hindi", "Gujarati"],
        "bio": (
            "Dr. Arjun Mehta is a consultant psychiatrist based in Ahmedabad with 12 years "
            "of clinical experience. An AIIMS Delhi fellow, he combines pharmacotherapy with "
            "psychoeducation and has a particular interest in the intersection of cognitive "
            "biases and mood disorders."
        ),
        "approach": (
            "My practice integrates psychiatric care with psychological education. I believe "
            "understanding the cognitive mechanisms behind emotional suffering empowers "
            "patients to participate actively in their own recovery. I use a biopsychosocial "
            "framework and tailor treatment to each individual."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1200, "max": 1800, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 83,
        "experience_years": 12,
    },
    {
        "name": "Ms. Kavitha Raghunathan",
        "initials": "KR",
        "credentials": ["M.A. Counselling Psychology", "RCI Licensed Psychologist"],
        "specializations": ["Relationship Issues", "Self-Esteem", "Labeling Bias", "Emotional Reasoning"],
        "languages": ["English", "Tamil", "Telugu"],
        "bio": (
            "Kavitha Raghunathan is a Chennai-based counselling psychologist with 6 years "
            "of practice. She specialises in helping individuals break free from rigid "
            "self-labeling and develop healthier relationship patterns. She has a warm, "
            "non-judgmental style that clients consistently describe as accessible and "
            "empowering."
        ),
        "approach": (
            "I draw primarily on person-centred therapy and Acceptance and Commitment "
            "Therapy (ACT) to help clients develop psychological flexibility. Rather than "
            "fighting unhelpful thoughts, I help clients change their relationship with them."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 700, "max": 1000, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.7,
        "review_count": 62,
        "experience_years": 6,
    },
    {
        "name": "Dr. Ritu Bose",
        "initials": "RB",
        "credentials": ["Ph.D. Psychology", "M.Phil. Clinical Psychology", "RCI Licensed"],
        "specializations": ["Trauma", "PTSD", "Catastrophizing", "Narrative Therapy"],
        "languages": ["English", "Bengali", "Hindi"],
        "bio": (
            "Dr. Ritu Bose is a Kolkata-based clinical psychologist with a doctorate from "
            "Calcutta University and 10 years of experience. She specialises in trauma "
            "recovery and works extensively with survivors of domestic violence and "
            "workplace harassment. Her research on cognitive distortions in PTSD has been "
            "published in Indian journals of psychiatry."
        ),
        "approach": (
            "I use Trauma-Focused CBT and narrative therapy to help clients rewrite their "
            "relationship with past experiences. I believe that people are the experts on "
            "their own lives, and my role is to help them access their own wisdom and "
            "resilience."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1000, "max": 1400, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 91,
        "experience_years": 10,
    },
    {
        "name": "Mr. Vikram Nair",
        "initials": "VN",
        "credentials": ["M.Sc. Applied Psychology", "Certified Executive Coach (ICF)"],
        "specializations": ["Workplace Stress", "Leadership Biases", "Groupthink", "Overconfidence"],
        "languages": ["English", "Malayalam", "Hindi"],
        "bio": (
            "Vikram Nair is a Kochi-based organisational psychologist and executive coach "
            "with 9 years of experience working with corporate leaders and teams. He has "
            "consulted for several Fortune 500 companies on decision-making quality and "
            "leadership debiasing. His sessions combine evidence-based psychology with "
            "practical workplace tools."
        ),
        "approach": (
            "I use a blend of cognitive coaching and behavioural science to help clients "
            "and teams make better decisions. My approach is solution-focused and pragmatic "
            "— I work with the specific biases most relevant to your professional context."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 1500, "max": 2500, "currency": "INR"},
        "availability": {"status": "busy", "next_slot": "2 weeks"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 38,
        "experience_years": 9,
    },
    {
        "name": "Dr. Sunita Desai",
        "initials": "SD",
        "credentials": ["M.D. Psychiatry", "Certified DBT Therapist"],
        "specializations": ["Borderline Personality", "All-or-Nothing Thinking", "DBT", "Emotional Regulation"],
        "languages": ["English", "Marathi", "Hindi"],
        "bio": (
            "Dr. Sunita Desai is a Pune-based psychiatrist with 14 years of clinical "
            "experience and one of Maharashtra's few certified Dialectical Behaviour "
            "Therapy (DBT) practitioners. She works with complex emotional and personality "
            "difficulties, including pervasive all-or-nothing thinking that undermines "
            "relationships and career."
        ),
        "approach": (
            "DBT is the backbone of my practice — I teach concrete, evidence-based skills "
            "for tolerating distress, regulating emotions, and improving relationships. "
            "I also use schema therapy to address deeper, long-standing patterns."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1200, "max": 1600, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 55,
        "experience_years": 14,
    },
    {
        "name": "Ms. Deepika Iyer",
        "initials": "DI",
        "credentials": ["M.Sc. Clinical Psychology", "RCI Licensed", "Mindfulness-Based Stress Reduction (MBSR) Certified"],
        "specializations": ["Anxiety", "Mindfulness", "Overgeneralization", "Academic Stress"],
        "languages": ["English", "Tamil", "Kannada"],
        "bio": (
            "Deepika Iyer is a Bengaluru-based psychologist with 5 years of experience "
            "specialising in young adults navigating academic pressure, career anxiety, "
            "and perfectionism. She is passionate about making mental health care "
            "accessible and approachable for first-generation therapy-goers."
        ),
        "approach": (
            "I use a client-centred approach integrating CBT and mindfulness practices. "
            "My sessions are conversational and non-clinical in feel, designed to normalise "
            "psychological struggles and build practical coping skills step by step."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 600, "max": 900, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.6,
        "review_count": 29,
        "experience_years": 5,
    },
    {
        "name": "Dr. Rahul Khanna",
        "initials": "RK",
        "credentials": ["Ph.D. Neuropsychology", "M.Phil. Medical & Social Psychology"],
        "specializations": ["Cognitive Rehabilitation", "Memory Biases", "Hindsight Bias", "Neuropsychological Assessment"],
        "languages": ["English", "Hindi", "Punjabi"],
        "bio": (
            "Dr. Rahul Khanna is a Delhi-based neuropsychologist with 11 years of "
            "experience in both clinical and research settings. He has published work on "
            "memory distortions and their relationship to decision-making in clinical "
            "populations. He sees both neurological patients and clients interested in "
            "optimising cognitive performance."
        ),
        "approach": (
            "I take a scientist-practitioner approach grounded in neuropsychological "
            "evidence. Assessments are thorough and personalised, and treatment plans "
            "are built around each client's specific cognitive profile rather than "
            "generic interventions."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1400, "max": 2000, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 44,
        "experience_years": 11,
    },
    {
        "name": "Ms. Ananya Chatterjee",
        "initials": "AC",
        "credentials": ["M.A. Counselling Psychology", "Gottman Level 2 Certified"],
        "specializations": ["Couples Therapy", "Communication Biases", "Fundamental Attribution Error", "Relationship Conflict"],
        "languages": ["English", "Bengali", "Hindi"],
        "bio": (
            "Ananya Chatterjee is a Kolkata-based couples therapist with 7 years of "
            "experience helping partners break destructive attribution patterns. She is "
            "one of few Gottman-certified therapists in West Bengal and has worked with "
            "over 200 couples. She is particularly skilled at helping couples identify "
            "the cognitive biases driving their conflicts."
        ),
        "approach": (
            "The Gottman Method is the foundation of my couples work, complemented by "
            "Emotionally Focused Therapy (EFT). I help partners understand the cognitive "
            "patterns — attribution errors, catastrophizing, mind-reading — that turn "
            "small conflicts into entrenched battles."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 1000, "max": 1500, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 73,
        "experience_years": 7,
    },
    {
        "name": "Dr. Sanjay Reddy",
        "initials": "SR",
        "credentials": ["M.D. Psychiatry", "Fellowship in Addiction Psychiatry", "RCI Licensed"],
        "specializations": ["Addiction", "Sunk Cost Fallacy", "Motivational Interviewing", "Impulse Control"],
        "languages": ["English", "Telugu", "Hindi"],
        "bio": (
            "Dr. Sanjay Reddy is a Hyderabad-based addiction psychiatrist with 13 years "
            "of experience. He integrates Motivational Interviewing with cognitive "
            "debiasing techniques and has written extensively on how the sunk-cost "
            "fallacy perpetuates addictive behaviour. He runs both individual and group "
            "therapy sessions."
        ),
        "approach": (
            "I use Motivational Interviewing to build intrinsic motivation for change, "
            "combined with CBT techniques that specifically target the cognitive biases — "
            "sunk cost thinking, availability heuristic — that keep people trapped in "
            "addictive cycles."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1100, "max": 1500, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.7,
        "review_count": 58,
        "experience_years": 13,
    },
    {
        "name": "Ms. Meera Pillai",
        "initials": "MP",
        "credentials": ["M.Sc. Psychology", "Art Therapy Diploma (RATA)"],
        "specializations": ["Art Therapy", "Trauma", "Self-Esteem", "Personalization"],
        "languages": ["English", "Malayalam", "Tamil"],
        "bio": (
            "Meera Pillai is a Trivandrum-based therapist who integrates art therapy with "
            "evidence-based psychological approaches. With 6 years of experience, she works "
            "primarily with clients who find traditional talk therapy difficult, including "
            "those with trauma histories and people exploring identity questions."
        ),
        "approach": (
            "Art therapy provides a non-verbal pathway to explore experiences that are "
            "difficult to articulate. I combine creative modalities with ACT and trauma-"
            "informed principles, creating a safe space where clients can express and "
            "process without judgment."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 700, "max": 1000, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.7,
        "review_count": 34,
        "experience_years": 6,
    },
    {
        "name": "Dr. Neha Agarwal",
        "initials": "NA",
        "credentials": ["Ph.D. Clinical Psychology", "Certified Schema Therapist", "RCI Licensed"],
        "specializations": ["Schema Therapy", "Personality Disorders", "Blind Spot Bias", "Self-Awareness"],
        "languages": ["English", "Hindi"],
        "bio": (
            "Dr. Neha Agarwal is a Lucknow-based clinical psychologist with a Ph.D. from "
            "Banaras Hindu University and 9 years of experience. She is one of India's "
            "few certified Schema Therapists and specialises in helping clients understand "
            "the deep-rooted schemas and cognitive patterns that drive repetitive life "
            "difficulties."
        ),
        "approach": (
            "Schema Therapy integrates CBT, attachment theory, and experiential techniques "
            "to address long-standing patterns. I work at a deeper level than symptom "
            "management — helping clients understand why they repeatedly encounter the "
            "same problems and how to change at the core schema level."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 900, "max": 1300, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 41,
        "experience_years": 9,
    },
    {
        "name": "Mr. Rohit Verma",
        "initials": "RV",
        "credentials": ["M.A. Psychology", "Certified CBT Practitioner (BABCP)"],
        "specializations": ["Social Anxiety", "Spotlight Effect", "Performance Anxiety", "CBT"],
        "languages": ["English", "Hindi", "Bhojpuri"],
        "bio": (
            "Rohit Verma is a Varanasi-based counsellor with 4 years of experience "
            "specialising in social anxiety and performance anxiety in students and "
            "young professionals. He has a particular interest in the spotlight effect "
            "and self-consciousness biases that amplify social anxiety."
        ),
        "approach": (
            "I use structured CBT with a focus on behavioural experiments — real-world "
            "tests that challenge anxiety-maintaining beliefs about how much others notice "
            "and judge us. Sessions are practical, evidence-based, and often include "
            "homework to build confidence between sessions."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 500, "max": 800, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.6,
        "review_count": 22,
        "experience_years": 4,
    },
    {
        "name": "Dr. Lakshmi Subramaniam",
        "initials": "LS",
        "credentials": ["M.D. Psychiatry", "DPM", "Fellow TNMSC"],
        "specializations": ["Geriatric Psychiatry", "Memory Biases", "Recency Bias", "Dementia Care"],
        "languages": ["English", "Tamil"],
        "bio": (
            "Dr. Lakshmi Subramaniam is a Chennai-based geriatric psychiatrist with 16 "
            "years of experience. She has a deep understanding of how memory biases evolve "
            "with age and has published research on recency and availability biases in "
            "older adults. She also counsels families navigating dementia care decisions."
        ),
        "approach": (
            "I take a holistic, family-inclusive approach to geriatric mental health. "
            "Treatment combines evidence-based pharmacotherapy with psychoeducation for "
            "patients and caregivers, with particular attention to cognitive biases that "
            "affect medical decision-making in later life."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1200, "max": 1600, "currency": "INR"},
        "availability": {"status": "busy", "next_slot": "2 weeks"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 102,
        "experience_years": 16,
    },
    {
        "name": "Ms. Pooja Malhotra",
        "initials": "PM",
        "credentials": ["M.Sc. Clinical Psychology", "RCI Licensed", "Positive Psychology Practitioner"],
        "specializations": ["Positive Psychology", "Optimism Bias", "Resilience", "Career Counselling"],
        "languages": ["English", "Hindi", "Punjabi"],
        "bio": (
            "Pooja Malhotra is an Amritsar-based psychologist with 7 years of experience "
            "helping clients build genuine resilience rather than toxic positivity. Her "
            "work addresses the optimism bias — helping clients remain hopeful while "
            "planning realistically for setbacks."
        ),
        "approach": (
            "I draw on Positive Psychology and CBT to help clients develop balanced "
            "thinking — neither catastrophizing nor unrealistic optimism. We work on "
            "building authentic strengths, realistic goal-setting, and sustainable "
            "wellbeing habits."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 700, "max": 1000, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.7,
        "review_count": 49,
        "experience_years": 7,
    },
    {
        "name": "Dr. Aditya Krishnamurthy",
        "initials": "AK",
        "credentials": ["Ph.D. Cognitive Psychology", "M.Phil. Neuropsychology", "RCI Licensed"],
        "specializations": ["Cognitive Enhancement", "Survivorship Bias", "Critical Thinking", "Research Professionals"],
        "languages": ["English", "Kannada", "Tamil"],
        "bio": (
            "Dr. Aditya Krishnamurthy is a Mysuru-based cognitive psychologist and "
            "researcher with 10 years of experience in academic and clinical settings. "
            "He works primarily with researchers, analysts, and academics who want to "
            "improve their reasoning quality and recognise biases such as survivorship "
            "bias in their work."
        ),
        "approach": (
            "My approach is educational and structured, grounded in cognitive psychology "
            "research. Sessions combine theoretical insight about bias mechanisms with "
            "applied practice using clients' real-world reasoning tasks. I also provide "
            "group workshops for research teams."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 1000, "max": 1400, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 31,
        "experience_years": 10,
    },
    {
        "name": "Ms. Farida Sheikh",
        "initials": "FS",
        "credentials": ["M.A. Counselling Psychology", "Certified Grief Counsellor", "RCI Licensed"],
        "specializations": ["Grief", "Loss", "Choice-Supportive Bias", "Life Transitions"],
        "languages": ["English", "Hindi", "Urdu"],
        "bio": (
            "Farida Sheikh is a Mumbai-based counsellor with 8 years of experience "
            "specialising in grief, loss, and major life transitions. She has a "
            "particular interest in how clients reconstruct memory of past choices "
            "during loss, including choice-supportive bias in bereavement narratives."
        ),
        "approach": (
            "I draw on narrative therapy and Complicated Grief Treatment (CGT) to help "
            "clients process loss without avoiding or suppressing grief. I believe "
            "that examining our stories about the past — including how we remember and "
            "reconstruct past decisions — is central to moving forward with integrity."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 800, "max": 1100, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.8,
        "review_count": 56,
        "experience_years": 8,
    },
    {
        "name": "Dr. Geeta Patel",
        "initials": "GP",
        "credentials": ["M.D. Psychiatry", "MRCPsych (UK)", "Certified Family Therapist"],
        "specializations": ["Family Therapy", "Systemic Biases", "In-Group Bias", "Intergenerational Patterns"],
        "languages": ["English", "Gujarati", "Hindi"],
        "bio": (
            "Dr. Geeta Patel is a Surat-based psychiatrist with a UK postgraduate "
            "qualification and 15 years of experience across NHS and private practice. "
            "She returned to India in 2018 and now focuses on family therapy, helping "
            "families recognise how in-group bias and intergenerational patterns shape "
            "their dynamics and conflicts."
        ),
        "approach": (
            "Systemic family therapy looks at the family as an interconnected system "
            "rather than focusing on individual pathology. I use circular questioning "
            "and reflective processes to help families see their patterns from new "
            "angles and find more helpful ways of relating."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 1300, "max": 1800, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "next week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.9,
        "review_count": 67,
        "experience_years": 15,
    },
    {
        "name": "Mr. Suresh Babu",
        "initials": "SB",
        "credentials": ["M.Sc. Psychology", "Rational Emotive Behaviour Therapy (REBT) Certified", "RCI Licensed"],
        "specializations": ["REBT", "Anger Management", "Framing Effect", "Workplace Conflict"],
        "languages": ["English", "Telugu", "Kannada"],
        "bio": (
            "Suresh Babu is a Vizag-based REBT therapist with 8 years of experience "
            "helping clients challenge irrational beliefs that fuel anger, frustration, "
            "and conflict. He works extensively with middle managers who need tools "
            "for emotional regulation in high-pressure workplaces."
        ),
        "approach": (
            "REBT directly challenges the irrational beliefs and cognitive distortions — "
            "including the framing effect and catastrophizing — that cause unnecessary "
            "emotional suffering. My sessions are direct, practical, and focused on "
            "changing specific thought patterns that are causing problems."
        ),
        "session_formats": ["online"],
        "price_range": {"min": 600, "max": 900, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.6,
        "review_count": 43,
        "experience_years": 8,
    },
    {
        "name": "Dr. Rashmi Kulkarni",
        "initials": "RK",
        "credentials": ["Ph.D. Health Psychology", "M.Sc. Clinical Psychology", "RCI Licensed"],
        "specializations": ["Health Psychology", "Illness Anxiety", "Planning Fallacy", "Chronic Pain"],
        "languages": ["English", "Marathi", "Hindi", "Kannada"],
        "bio": (
            "Dr. Rashmi Kulkarni is a Nagpur-based health psychologist with 11 years "
            "of experience working at the interface of physical and mental health. She "
            "helps clients with health anxiety, chronic illness adjustment, and the "
            "planning fallacy that affects health behaviour change — knowing what to do "
            "but consistently underestimating how long behaviour change takes."
        ),
        "approach": (
            "Health psychology integrates CBT with motivational interviewing and "
            "behaviour change theory. I help clients set realistic health goals, "
            "understand their cognitive barriers, and build sustainable habits rather "
            "than relying on willpower alone."
        ),
        "session_formats": ["online", "in-person"],
        "price_range": {"min": 900, "max": 1300, "currency": "INR"},
        "availability": {"status": "available", "next_slot": "this week"},
        "contact_info": {"email": "contact@sentio.app", "note": "Contact via Sentio platform"},
        "verified": True,
        "rating": 4.7,
        "review_count": 60,
        "experience_years": 11,
    },
]


def main() -> None:
    supabase = get_supabase()
    result = (
        supabase.table("therapists")
        .insert(THERAPISTS)
        .execute()
    )
    count = len(result.data) if result.data else 0
    print(f"Seeded {count} therapists successfully.")


if __name__ == "__main__":
    main()
