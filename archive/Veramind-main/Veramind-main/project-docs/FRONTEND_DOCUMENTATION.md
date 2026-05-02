# Veramind Frontend: Complete Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Application Architecture](#application-architecture)
3. [User Flows](#user-flows)
4. [Pages & Components](#pages--components)
5. [UI/UX Design System](#uiux-design-system)
6. [Features & Functionality](#features--functionality)
7. [State Management](#state-management)
8. [Navigation Structure](#navigation-structure)

---

## 🎯 Overview


Veramind is a comprehensive mental health and self-discovery platform that provides users with tools for understanding cognitive patterns, managing anxiety, exploring career paths, and improving overall mental wellbeing through evidence-based assessments, journaling, educational modules, and community support.

### Core Purpose
- **Self-awareness**: Help users identify cognitive biases and thought patterns
- **Mental health management**: Provide tools for anxiety, stress, and mood tracking
- **Personal growth**: Guide users through structured learning modules
- **Community support**: Connect users with peers and professional resources


### Technology Stack
- **Framework**: Vue 3 with Vite (JavaScript only, no TypeScript)
- **Build Tool**: Vite (standalone)
- **Routing**: Vue Router (manual route definitions or automatic mapping via helper script)
- **UI Components**: Custom Vue components (no UI libraries)
- **Styling**: Vanilla CSS (assets/css/main.css)
- **State Management**: Vue composables, Pinia (optional)
- **Form Handling**: Native Vue form handling
- **Backend Integration**: Supabase (PostgreSQL + Real-time)

---

## 🏗️ Application Architecture

src/

### Directory Structure
```
src/
├── components/           # Reusable UI components (Vue SFCs)
│   ├── ui/              # Base UI components (custom)
│   ├── journal/         # Journal-specific components
│   ├── DashboardLayout.vue
│   ├── Navbar.vue
│   ├── Sidebar.vue
│   ├── Footer.vue
│   └── ProtectedRoute.vue
├── composables/         # Vue composables (hooks)
│   ├── useMobile.js
│   └── useToast.js
├── integrations/        # External service integrations
│   └── supabase/
│       ├── client.js
│       └── types.js
├── utils/               # Utility functions
│   └── utils.js
├── pages/               # Route page components
│   ├── index.vue
│   ├── signup.vue
│   ├── login.vue
│   ├── dashboard.vue
│   ├── assessments.vue
│   ├── assessment-detail.vue
│   ├── insights.vue
│   ├── journal.vue
│   ├── community.vue
│   ├── modules.vue
│   ├── module-detail.vue
│   ├── resources.vue
│   ├── educational-materials.vue
│   ├── self-help-tools.vue
│   ├── find-help.vue
│   ├── settings.vue
│   └── not-found.vue
├── services/            # API service functions
│   └── journalService.js
├── app.vue              # Main app component with routing
├── main.js              # Application entry point
└── assets/css/main.css  # Global styles
```


### Component Hierarchy
```
App
├── Public Routes
│   ├── Index (Landing Page)
│   ├── SignUp
│   └── Login
└── Protected Routes (wrapped in ProtectedRoute)
    └── DashboardLayout
        ├── Sidebar (persistent navigation)
        └── Main Content Area
            ├── Dashboard
            ├── Assessments
            ├── AssessmentDetail
            ├── Insights
            ├── Journal
            ├── Community
            ├── Modules
            ├── ModuleDetail
            ├── Resources
            ├── EducationalMaterials
            ├── SelfHelpTools
            ├── FindHelp
            └── Settings
```

---

## 👥 User Flows

### 1. **Authentication Flow**

#### Sign Up Journey
```
Landing Page → Click "Get Started" → Sign Up Form
├── Enter email, password, full name
├── Accept terms and conditions
├── Submit form
└── Success → Auto-redirect to Dashboard

Error Handling:
├── Email already exists → Show error message
├── Weak password → Show password requirements
└── Network error → Show retry option
```

#### Login Journey
```
Landing Page → Click "Sign In" → Login Form
├── Enter email and password
├── Submit credentials
└── Success → Redirect to Dashboard

Alternative Paths:
├── Forgot Password → Password reset flow
└── No account → Link to Sign Up
```

#### Protected Route Access
```
User attempts to access protected page
├── If authenticated → Allow access
└── If not authenticated → Redirect to Login
    └── After login → Redirect to originally requested page
```

---

### 2. **Dashboard Flow**

#### Initial Dashboard View
```
User logs in → Dashboard loads
├── Welcome message with user name
├── Quick Actions (3 cards)
│   ├── Start weekly check-in → Navigate to Assessments
│   ├── Continue active module → Navigate to Module detail
│   └── Write in journal → Navigate to Journal
├── Recent Insights
│   └── Anxiety level trends (chart visualization)
├── Active Modules (progress cards)
│   ├── Shows completion percentage
│   └── "Continue" button
└── Crisis Support Section (always visible)
```

#### Navigation from Dashboard
```
Dashboard serves as central hub
├── Quick actions → Direct feature access
├── "View all" links → Full feature pages
├── Module cards → Continue learning
├── Sidebar → Global navigation
└── Crisis banner → Immediate help resources
```

---

### 3. **Assessment Flow**

#### Assessment Discovery
```
Dashboard/Sidebar → Assessments Page
├── Two tabs: "Available" | "Completed"
├── Available Assessments
│   ├── Card grid layout (2 columns on desktop)
│   ├── Each card shows:
│   │   ├── Category badge
│   │   ├── Title and description
│   │   ├── Estimated time
│   │   └── "Start Assessment" button
│   └── Disclaimer about non-diagnostic nature
└── Completed Assessments
    ├── Shows completion date
    ├── Award badge icon
    └── Actions: "View Results" | "Take Again"
```

#### Taking an Assessment
```
Click "Start Assessment" → Assessment Detail Page
├── Assessment instructions and disclaimer
├── Question presentation
│   ├── Single question per screen (preferred UX)
│   ├── Multiple choice or scale responses
│   ├── Progress indicator
│   └── Navigation: "Previous" | "Next"
├── Review answers (optional)
└── Submit Assessment
    ├── Processing indicator
    └── Redirect to Results

Results Display:
├── Score interpretation
├── Severity level visualization
├── Personalized recommendations
├── Educational resources links
└── Option to save/download results
```

#### Assessment Types
1. **GAD-7 (Anxiety Screening)**
   - 7 questions, 4-point scale
   - Time: 2-3 minutes
   - Scoring: 0-21 scale
   
2. **PHQ-9 (Depression Screening)**
   - 9 questions, 4-point scale
   - Time: 3-4 minutes
   - Scoring: 0-27 scale

3. **Cognitive Bias Inventory**
   - 15-20 questions
   - Time: 5-7 minutes
   - Identifies thinking patterns

4. **Core Values Assessment**
   - Value ranking and prioritization
   - Time: 10-12 minutes
   - Guides career/life decisions

---

### 4. **Journal Flow**

#### Journal Main Page
```
Dashboard/Sidebar → Journal
├── Three tabs:
│   ├── Write (default)
│   ├── Past Entries
│   └── Calendar View
├── Date selector (calendar widget)
├── Journal prompt (rotatable)
└── Rich text editor area
```

#### Writing Flow
```
Write Tab Active
├── Select date (defaults to today)
├── Read prompt (click to rotate through options)
├── Write entry in editor
│   ├── Rich text formatting
│   ├── Auto-save drafts (future feature)
│   └── Character/word count
├── Click "Save Entry"
│   ├── Success toast notification
│   ├── Entry added to database
│   └── Editor clears (ready for next entry)
└── Optional: Add tags or mood rating

Prompts System:
├── "What's on your mind today?"
├── "What are three things you're grateful for today?"
├── "Describe a challenge you faced recently..."
├── "What values guided your decisions today?"
├── "Reflect on something that made you feel anxious..."
└── "What biases might have influenced your thinking today?"
```

#### Past Entries View
```
Past Entries Tab
├── Chronological list of entries
│   ├── Entry date and time
│   ├── Content preview (first 150 characters)
│   ├── Associated prompt
│   └── Click to expand full entry
├── Filter/Search options
│   ├── Date range filter
│   ├── Keyword search
│   └── Prompt filter
├── Empty state
│   └── "Write Your First Entry" CTA
└── Entry actions
    ├── Edit entry
    ├── Delete entry (with confirmation)
    └── Share/Export entry
```

#### Calendar View
```
Calendar Tab
├── Monthly calendar grid
├── Dates with entries highlighted (purple)
├── Click date → Opens entry in Write tab
├── Visual patterns
│   ├── Consistency tracking
│   └── Frequency visualization
└── Current date selection indicator
```

#### Journal Analytics (Future)
```
Insights Integration
├── Sentiment analysis of entries
├── Mood trend visualization
├── Common themes identification
├── Writing frequency patterns
└── Personalized insights
```

---

### 5. **Learning Modules Flow**

#### Module Discovery
```
Dashboard/Sidebar → Modules Page
├── Grid of available modules (2 columns)
├── Each module card displays:
│   ├── Icon and category color
│   ├── Title and description
│   ├── Progress percentage
│   └── "Start" or "Continue" button
└── Modules available:
    ├── Anxiety Toolkit
    ├── Cognitive Bias Awareness
    ├── Career Path Explorer
    └── Self-Compassion Builder
```

#### Module Progression
```
Click module card → Module Detail Page
├── Module overview
│   ├── Description and learning objectives
│   ├── Estimated time to complete
│   ├── Progress indicator
│   └── Difficulty level
├── Content sections/lessons
│   ├── Sequential unlocking
│   ├── Video content (if available)
│   ├── Interactive exercises
│   ├── Reading materials
│   └── Quiz/knowledge checks
├── Navigation
│   ├── Previous lesson
│   ├── Next lesson
│   ├── Lesson list (sidebar)
│   └── Mark as complete
└── Completion tracking
    ├── Lesson completion checkmarks
    ├── Overall module progress
    ├── Certificate/badge on completion
    └── Recommendations for next module
```

#### Example: Anxiety Toolkit Module
```
Module Structure:
├── Introduction to Anxiety
│   ├── What is anxiety?
│   ├── Types of anxiety disorders
│   └── When to seek help
├── Understanding Your Anxiety
│   ├── Physical symptoms
│   ├── Cognitive symptoms
│   └── Behavioral patterns
├── Coping Strategies
│   ├── Breathing exercises (interactive)
│   ├── Progressive muscle relaxation
│   ├── Cognitive restructuring
│   └── Mindfulness techniques
├── Lifestyle Management
│   ├── Sleep hygiene
│   ├── Exercise and anxiety
│   ├── Nutrition impact
│   └── Social support
└── Creating Your Action Plan
    ├── Identifying triggers
    ├── Personal coping toolkit
    ├── Crisis plan
    └── Progress tracking
```

---

### 6. **Community Flow**

#### Community Main Page
```
Dashboard/Sidebar → Community
├── Two main tabs:
│   ├── Discussions (default)
│   └── Support Groups
├── Discussion board features
│   ├── Thread list
│   ├── Filter/sort options
│   ├── Search functionality
│   └── "New Post" button
└── Community guidelines (always visible)
```

#### Discussion Interactions
```
Discussions Tab
├── Thread List View
│   ├── Thread title
│   ├── Author info (name, avatar)
│   ├── Post timestamp
│   ├── Tags/categories
│   ├── Message count
│   ├── Last activity time
│   └── Click to view full thread
├── Create New Post
│   ├── Title input
│   ├── Content editor
│   ├── Tag selection
│   ├── Anonymity toggle
│   └── Submit button
└── Thread Detail View
    ├── Original post
    ├── Reply thread
    ├── Like/dislike buttons
    ├── Reply button
    ├── Report/flag option
    └── Bias check tool (AI-powered)
```

#### Bias Checking Feature
```
Any message/post → "Check for Bias" button
├── AI analysis of content
├── Identifies potential cognitive biases:
│   ├── All-or-nothing thinking
│   ├── Overgeneralization
│   ├── Catastrophizing
│   ├── Social comparison bias
│   └── Confirmation bias
├── Results displayed
│   ├── Bias type identified
│   ├── Explanation
│   ├── Suggested reframe
│   └── Educational resources
└── User can:
    ├── Edit post based on feedback
    ├── Dismiss suggestion
    └── Learn more about bias
```

#### Support Groups
```
Support Groups Tab
├── Group categories:
│   ├── Anxiety support
│   ├── Depression support
│   ├── Career transitions
│   ├── LGBTQ+ mental health
│   ├── Student mental health
│   └── General wellness
├── Group card displays:
│   ├── Group name and description
│   ├── Member count
│   ├── Activity level
│   ├── Privacy setting (open/closed)
│   └── "Join Group" button
└── Group Detail (after joining)
    ├── Group discussions
    ├── Scheduled events
    ├── Member directory
    ├── Group resources
    └── Moderation tools
```

---

### 7. **Resources Flow**

#### Resources Hub
```
Dashboard/Sidebar → Resources
├── Crisis Support Banner (prominent)
│   ├── Emergency hotlines
│   ├── Crisis text line
│   └── Immediate help resources
├── Three main categories (cards):
│   ├── Educational Materials
│   ├── Self-Help Tools
│   └── Find Help (Professional Directory)
└── Each category card:
    ├── Icon and description
    ├── Preview of contents
    └── "Browse" / "Access" button
```

---

#### 7.1 Educational Materials Flow

```
Resources → Educational Materials
├── Article library interface
│   ├── Search bar (keyword search)
│   ├── Category filter buttons
│   │   ├── All
│   │   ├── Anxiety
│   │   ├── Depression
│   │   ├── Stress
│   │   ├── Mindfulness
│   │   ├── Resilience
│   │   └── Sleep
│   ├── Difficulty filter
│   │   ├── Beginner
│   │   ├── Intermediate
│   │   └── Advanced
│   └── Sort options
│       ├── Most Recent
│       ├── Most Popular
│       └── Shortest First
├── Article cards (grid layout)
│   ├── Title and description
│   ├── Category badge
│   ├── Read time estimate
│   ├── Author name
│   ├── Difficulty indicator
│   ├── Tags
│   └── "Read More" button
└── Empty state with search suggestion
```

#### Article Reading Experience
```
Click "Read More" → Full Article View
├── Back to library button
├── Article header
│   ├── Title
│   ├── Author and credentials
│   ├── Publication date
│   ├── Category and tags
│   └── Read time
├── Article content
│   ├── Rich text formatting
│   ├── Section headings
│   ├── Bullet points and lists
│   ├── Images/diagrams (if applicable)
│   └── Callout boxes for key points
├── Interactive features
│   ├── Bookmark/save article
│   ├── Share via link
│   ├── Download as PDF
│   └── Print option
├── Engagement metrics
│   ├── Reading progress indicator
│   └── Time spent tracking
└── Related content
    ├── Suggested articles
    ├── Related modules
    └── Related tools
```

#### Article Categories & Examples

**Anxiety Category:**
- Understanding Anxiety: A Comprehensive Guide
- Managing Panic Attacks
- Social Anxiety in Daily Life
- Anxiety and Physical Health

**Depression Category:**
- Depression: Recognizing Signs and Seeking Help
- Seasonal Affective Disorder
- Managing Low Motivation
- Depression and Relationships

**Stress Category:**
- Stress Management Techniques
- Work-Life Balance Strategies
- Chronic Stress and Health
- Acute vs. Chronic Stress

**Mindfulness Category:**
- Mindfulness and Mental Health
- Introduction to Meditation
- Mindful Eating Practices
- Present Moment Awareness

**Resilience Category:**
- Building Emotional Resilience
- Bouncing Back from Setbacks
- Growth Mindset Development
- Resilience in Adversity

---

#### 7.2 Self-Help Tools Flow

```
Resources → Self-Help Tools
├── Tool categories (card grid)
│   ├── Breathing Exercises
│   ├── Thought Challenging
│   ├── Mindfulness Meditation
│   └── Mood Tracking
├── Each tool card shows:
│   ├── Icon and color coding
│   ├── Title and description
│   ├── Category badge
│   ├── Duration estimate
│   ├── Difficulty level
│   ├── Sub-tools available
│   └── "Start" button
└── Tool usage tracking
    ├── Frequency of use
    ├── Favorite tools
    └── Effectiveness ratings
```

#### Breathing Exercises Tool
```
Click "Breathing Exercises" → Interactive Tool
├── Exercise selection
│   ├── 4-7-8 Breathing
│   │   └── Inhale 4s, Hold 7s, Exhale 8s
│   ├── Box Breathing
│   │   └── Inhale 4s, Hold 4s, Exhale 4s, Pause 4s
│   └── Simple Breathing
│       └── Inhale 4s, Exhale 4s
├── Visual guide interface
│   ├── Large circular timer display
│   ├── Current phase indicator (Inhale/Hold/Exhale)
│   ├── Breath count tracker
│   ├── Total time elapsed
│   └── Breathing animation (expanding/contracting circle)
├── Controls
│   ├── Play/Pause button
│   ├── Reset button
│   ├── Exercise type selector
│   └── Sound toggle (breathing audio cues)
├── Session tracking
│   ├── Number of cycles completed
│   ├── Total duration
│   └── Save session to history
└── Post-session
    ├── "How do you feel?" rating
    ├── Notes field
    ├── Share progress
    └── Schedule reminder
```

#### Thought Challenging Tool
```
Click "Thought Challenging" → Cognitive Exercise
├── Thought Record Interface
│   ├── Step 1: Identify the situation
│   │   └── Text input: "Describe what happened"
│   ├── Step 2: Identify emotions
│   │   ├── Emotion selector (multi-select)
│   │   └── Intensity slider (0-10)
│   ├── Step 3: Automatic thoughts
│   │   └── "What went through your mind?"
│   ├── Step 4: Evidence for the thought
│   │   └── List builder interface
│   ├── Step 5: Evidence against the thought
│   │   └── List builder interface
│   ├── Step 6: Alternative perspective
│   │   └── "What's a more balanced view?"
│   └── Step 7: Re-rate emotions
│       └── Intensity slider comparison
├── Guided prompts
│   ├── Context-sensitive questions
│   ├── Examples for each step
│   └── CBT education snippets
├── Save and review
│   ├── Save thought record
│   ├── View past records
│   ├── Pattern identification
│   └── Progress over time
└── Export options
    ├── Share with therapist
    ├── Print worksheet
    └── Download PDF
```

#### Mindfulness Meditation Tool
```
Click "Mindfulness Meditation" → Meditation Interface
├── Meditation type selection
│   ├── Body Scan (10-30 min)
│   ├── Loving Kindness (10-20 min)
│   ├── Mindful Breathing (5-15 min)
│   └── Walking Meditation (10-20 min)
├── Meditation player interface
│   ├── Audio player controls
│   ├── Voice selection (if available)
│   ├── Background sound options
│   ├── Timer display
│   └── Progress bar
├── Meditation guidance
│   ├── Narrated instructions
│   ├── Pause points for practice
│   ├── Gentle return cues
│   └── Closing reflection
├── Meditation tracking
│   ├── Consecutive days streak
│   ├── Total minutes meditated
│   ├── Favorite practices
│   └── Progress milestones
└── Post-meditation
    ├── Mindfulness rating
    ├── Journal prompt
    ├── Insights noted
    └── Schedule next session
```

#### Mood Tracking Tool
```
Click "Mood Tracking" → Daily Mood Logger
├── Quick mood check-in
│   ├── Mood selector (emoji/scale)
│   ├── Energy level slider
│   ├── Anxiety level slider
│   ├── Sleep quality rating
│   └── Optional notes field
├── Trigger identification
│   ├── What influenced your mood?
│   ├── Positive events
│   ├── Challenging situations
│   └── Physical factors
├── Pattern analysis (over time)
│   ├── Mood trends graph
│   ├── Trigger frequency
│   ├── Best/worst times of day
│   ├── Day of week patterns
│   └── Correlation insights
├── Mood history
│   ├── Calendar view with color coding
│   ├── Weekly/monthly summaries
│   ├── Detailed entry view
│   └── Export data (CSV/PDF)
└── Insights generation
    ├── AI-powered pattern detection
    ├── Suggestions for improvement
    ├── Resource recommendations
    └── When to seek help indicators
```

---

#### 7.3 Find Help Flow

```
Resources → Find Help
├── Professional directory interface
├── Three main tabs:
│   ├── Find Professionals (default)
│   ├── Crisis Resources
│   └── Support Organizations
└── Search and filter system
```

#### Find Professionals Tab
```
Professional Directory
├── Search interface
│   ├── Location input
│   │   ├── City, State, Zip
│   │   ├── Use current location (GPS)
│   │   └── Distance radius selector
│   ├── Professional type filter
│   │   ├── Psychiatrists
│   │   ├── Psychologists
│   │   ├── Licensed Therapists
│   │   ├── Mental Health Counselors
│   │   └── Clinical Social Workers
│   ├── Specialization filter (multi-select)
│   │   ├── Anxiety Disorders
│   │   ├── Depression
│   │   ├── Trauma/PTSD
│   │   ├── Addiction
│   │   ├── Eating Disorders
│   │   ├── Relationship Issues
│   │   ├── Grief/Loss
│   │   ├── ADHD
│   │   ├── Teen/Adolescent
│   │   └── Family Therapy
│   ├── Insurance provider filter
│   │   ├── Major providers list
│   │   ├── Medicaid/Medicare
│   │   ├── Self-Pay
│   │   └── Sliding Scale
│   └── Additional filters
│       ├── Accepting new patients
│       ├── Telehealth available
│       ├── Gender preference
│       ├── Languages spoken
│       └── Evening/weekend availability
├── Search results
│   ├── Provider cards (list view)
│   ├── Sort options:
│   │   ├── Distance (nearest first)
│   │   ├── Rating (highest first)
│   │   ├── Availability (accepting first)
│   │   └── Insurance match
│   └── Results count and pagination
```

#### Provider Card Details
```
Each Provider Card Displays:
├── Provider header
│   ├── Name and credentials
│   ├── Professional type
│   ├── Profile photo (if available)
│   └── "Accepting new patients" badge
├── Practice information
│   ├── Practice name
│   ├── Full address
│   ├── Distance from search location
│   ├── Phone number (click to call)
│   └── Website link
├── Specializations (tags)
├── Insurance accepted (collapsible list)
├── Rating and reviews
│   ├── Star rating (out of 5)
│   ├── Number of reviews
│   └── Link to full reviews
├── Availability features
│   ├── Telehealth available badge
│   ├── Office visits badge
│   └── Languages spoken
└── Actions
    ├── "View Full Profile" button
    ├── "Contact" button (opens modal)
    ├── "Save to Favorites" (heart icon)
    └── "Share" option
```

#### Provider Profile (Expanded View)
```
Click "View Full Profile" → Detailed Provider Page
├── Professional details
│   ├── Full biography
│   ├── Education and training
│   ├── Years in practice
│   ├── Licenses and certifications
│   ├── Professional memberships
│   └── Treatment approaches
├── Services offered
│   ├── Individual therapy
│   ├── Group therapy
│   ├── Family/couples therapy
│   ├── Medication management
│   └── Psychological testing
├── Practice details
│   ├── Office hours
│   ├── Session length and fees
│   ├── Insurance details
│   ├── Payment options
│   ├── Cancellation policy
│   └── Telehealth setup requirements
├── Location and accessibility
│   ├── Embedded map
│   ├── Parking information
│   ├── Public transit options
│   └── Accessibility features
├── Patient reviews
│   ├── Overall rating breakdown
│   ├── Review highlights
│   ├── Recent reviews (anonymized)
│   ├── Sort/filter reviews
│   └── "Write a Review" (for patients)
└── Contact options
    ├── Request appointment form
    ├── Message provider
    ├── Call directly
    └── Email inquiry
```

#### Crisis Resources Tab
```
Crisis Resources Section
├── Immediate help banner
│   └── Large, prominent emergency contacts
├── Crisis hotline cards (always accessible)
│   ├── National Suicide Prevention Lifeline
│   │   ├── Phone: 988
│   │   ├── Description: 24/7 free confidential support
│   │   ├── Website link
│   │   ├── Languages available
│   │   └── "Call Now" button
│   ├── Crisis Text Line
│   │   ├── Text HOME to 741741
│   │   ├── Description: Free 24/7 crisis support
│   │   ├── Website link
│   │   └── "Start Texting" link
│   ├── SAMHSA National Helpline
│   │   ├── Phone: 1-800-662-4357
│   │   ├── Treatment referral service
│   │   └── Available 24/7
│   └── National Domestic Violence Hotline
│       ├── Phone: 1-800-799-7233
│       ├── Support for domestic violence
│       └── TTY option available
├── Specialized crisis resources
│   ├── Trevor Project (LGBTQ+ youth)
│   ├── Veterans Crisis Line
│   ├── Disaster Distress Helpline
│   └── Substance Abuse Helpline
├── International resources
│   └── Crisis lines by country
└── Safety planning resources
    ├── Creating a safety plan guide
    ├── Downloadable safety plan template
    ├── Emergency contact card
    └── Coping strategies list
```

#### Support Organizations Tab
```
Mental Health Organizations Directory
├── Organization categories
│   ├── Advocacy Organizations
│   ├── Research Foundations
│   ├── Support Groups
│   ├── Educational Resources
│   └── Treatment Locators
├── Organization cards
│   ├── National Alliance on Mental Illness (NAMI)
│   │   ├── Mission statement
│   │   ├── Services: support groups, education, advocacy
│   │   ├── Helpline: 1-800-950-6264
│   │   ├── Website and local chapters
│   │   └── Free resources available
│   ├── Mental Health America (MHA)
│   │   ├── Screening tools
│   │   ├── Educational materials
│   │   ├── Advocacy initiatives
│   │   └── Community resources
│   ├── Anxiety and Depression Association of America (ADAA)
│   │   ├── Condition-specific resources
│   │   ├── Find-a-therapist directory
│   │   ├── Support groups
│   │   └── Educational webinars
│   ├── American Psychological Association (APA)
│   │   ├── Psychologist locator
│   │   ├── Consumer resources
│   │   └── Research and publications
│   └── The Jed Foundation (teens/young adults)
│       ├── Age-specific programs
│       ├── Campus mental health
│       └── Crisis prevention
└── Local resources
    ├── Community mental health centers
    ├── State mental health departments
    ├── County crisis services
    └── Free/low-cost clinics
```

---

### 8. **Insights & Analytics Flow**

```
Dashboard/Sidebar → Insights
├── Personal dashboard
│   ├── Overview metrics
│   │   ├── Total assessments completed
│   │   ├── Journal entries written
│   │   ├── Modules in progress
│   │   ├── Community engagement
│   │   └── Active streak days
│   ├── Mental health trends
│   │   ├── Anxiety levels over time (line chart)
│   │   ├── Mood patterns (calendar heatmap)
│   │   ├── Stress indicators (bar chart)
│   │   └── Progress trajectory
│   ├── Pattern insights (AI-generated)
│   │   ├── "Your anxiety tends to be higher on Mondays"
│   │   ├── "You journal more consistently when stressed"
│   │   ├── "Breathing exercises most helpful in evenings"
│   │   └── "Social support correlates with improved mood"
│   ├── Achievement tracking
│   │   ├── Milestones reached
│   │   ├── Badges earned
│   │   ├── Consistency streaks
│   │   └── Growth indicators
│   └── Personalized recommendations
│       ├── Based on patterns identified
│       ├── Suggested next steps
│       ├── Resource recommendations
│       └── Professional help indicators
├── Assessment history
│   ├── Chronological list of completed assessments
│   ├── Score trends over time
│   ├── Comparison charts (before/after)
│   └── Download/export results
├── Journal insights
│   ├── Writing frequency analysis
│   ├── Most common themes
│   ├── Sentiment analysis
│   ├── Word cloud visualization
│   └── Emotional trend tracking
└── Progress reports
    ├── Weekly summaries
    ├── Monthly reviews
    ├── Quarterly progress reports
    ├── Export options (PDF/Email)
    └── Share with healthcare provider option
```

---

### 9. **Settings Flow**

```
Dashboard/Sidebar → Settings
├── Account Settings
│   ├── Profile information
│   │   ├── Full name
│   │   ├── Email address (with verification)
│   │   ├── Profile photo
│   │   └── Bio/about (optional)
│   ├── Password management
│   │   ├── Change password
│   │   ├── Two-factor authentication
│   │   └── Security questions
│   └── Account actions
│       ├── Download all data
│       ├── Deactivate account
│       └── Delete account (with confirmation)
├── Privacy Settings
│   ├── Data collection preferences
│   ├── Anonymous usage statistics
│   ├── Marketing communications opt-in/out
│   └── Third-party data sharing controls
├── Notification Settings
│   ├── Email notifications
│   │   ├── Assessment reminders
│   │   ├── Journal prompts
│   │   ├── Community replies
│   │   ├── Module updates
│   │   └── Weekly summaries
│   ├── Push notifications (if PWA)
│   └── Notification frequency
├── Preferences
│   ├── Display settings
│   │   ├── Theme (light/dark/system)
│   │   ├── Font size
│   │   └── Color scheme accessibility
│   ├── Language selection
│   ├── Time zone
│   └── Date/time format
├── Connected Services
│   ├── Calendar integration
│   ├── Wearable devices (future)
│   └── Healthcare provider connection
└── Help & Support
    ├── FAQ and documentation
    ├── Contact support
    ├── Report a bug
    ├── Feature requests
    └── Terms of service / Privacy policy
```

---

## 🎨 UI/UX Design System

### Design Principles

1. **Calming and Supportive**
   - Soft color palette (purples, blues, neutrals)
   - Ample white space
   - Smooth transitions and animations
   - Non-intimidating interface

2. **Accessible and Inclusive**
   - WCAG 2.1 AA compliance
   - High contrast ratios
   - Keyboard navigation support
   - Screen reader compatibility
   - Clear, simple language

3. **Privacy-First**
   - Prominent crisis resources
   - Anonymity options in community
   - Clear data usage explanations
   - Easy account management

4. **Progressive Disclosure**
   - Show only necessary information
   - Reveal complexity gradually
   - Clear information hierarchy
   - Logical user journeys

### Color Palette

```css
/* Primary Colors */
--mind-purple: #9b87f5      /* Primary brand color */
--mind-purple-dark: #7c6bca  /* Buttons, accents */
--mind-purple-light: #f2f0ff /* Backgrounds, highlights */

/* Secondary Colors */
--mind-blue: #6bb6ff         /* Secondary actions */
--mind-blue-dark: #4a9ae8    /* Active states */
--mind-blue-light: #e6f3ff   /* Light backgrounds */

/* Neutral Colors */
--mind-gray-dark: #1a1f2c    /* Primary text */
--mind-gray: #6b7280         /* Secondary text */
--mind-gray-light: #f8fafc   /* Backgrounds */

/* Semantic Colors */
--success: #10b981           /* Success states */
--warning: #f59e0b           /* Warnings */
--error: #ef4444             /* Errors, crisis */
--info: #3b82f6              /* Information */
```

### Typography

```css
/* Font Family */


/* Font Sizes */
--text-xs: 0.75rem    /* 12px */
--text-sm: 0.875rem   /* 14px */
--text-base: 1rem     /* 16px */
--text-lg: 1.125rem   /* 18px */
--text-xl: 1.25rem    /* 20px */
--text-2xl: 1.5rem    /* 24px */
--text-3xl: 1.875rem  /* 30px */
--text-4xl: 2.25rem   /* 36px */
--text-5xl: 3rem      /* 48px */

/* Font Weights */
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

### Spacing System

```css
/* Based on 4px scale */
--spacing-1: 0.25rem   /* 4px */
--spacing-2: 0.5rem    /* 8px */
--spacing-3: 0.75rem   /* 12px */
--spacing-4: 1rem      /* 16px */
--spacing-6: 1.5rem    /* 24px */
--spacing-8: 2rem      /* 32px */
--spacing-12: 3rem     /* 48px */
--spacing-16: 4rem     /* 64px */
```

### Component Patterns

#### Cards
- **Default**: White background, subtle border, hover shadow
- **Hover effect**: Slight elevation with shadow
- **Active state**: Border color change to primary
- **Padding**: 1.5rem (24px) standard

#### Buttons
- **Primary**: Purple background, white text, rounded
- **Secondary**: Purple border, purple text, transparent background
- **Outline**: Gray border, dark text
- **Ghost**: No border, hover background change
- **Destructive**: Red for dangerous actions
- **Size variants**: sm (32px), default (40px), lg (48px)

#### Forms
- **Input fields**: Border on focus, error states in red
- **Labels**: Above inputs, medium weight font
- **Validation**: Real-time feedback, clear error messages
- **Disabled state**: Reduced opacity, no pointer

#### Navigation
- **Sidebar**: Fixed position, purple background, white text
- **Active route**: Highlighted with lighter background
- **Icons**: Consistent size (20px), left-aligned
- **Badges**: Small circles for notifications

---

## 🔧 Features & Functionality

### 1. **Authentication System**

#### User Registration
- Email and password sign-up
- Password strength validation
- Email verification (future)
- Terms acceptance requirement
- Auto-login after registration

#### User Login
- Email/password authentication
- "Remember me" option
- Password reset via email
- Session management
- Secure token storage

#### Protected Routes
- Route-level authentication check
- Automatic redirect to login
- Redirect back after login
- Session expiry handling

---

### 2. **Journal System**

#### Entry Management
- **Create**: Rich text editor with formatting
- **Read**: View past entries by date
- **Update**: Edit existing entries
- **Delete**: Remove entries with confirmation

#### Features
- **Prompts**: Rotating journal prompts for inspiration
- **Calendar Integration**: Visual entry tracking
- **Search**: Find entries by keyword
- **Export**: Download entries (future)
- **Auto-save**: Draft preservation (future)

#### Data Structure
```typescript
interface JournalEntry {
  id: string
  user_id: string
  date: string (YYYY-MM-DD)
  content: string
  prompt: string
  created_at: timestamp
  updated_at: timestamp
  tags?: string[]
  mood?: number
  sentiment?: object (ML analysis result)
}
```

---

### 3. **Assessment System**

#### Assessment Types
1. **Mental Health Screenings**: GAD-7, PHQ-9
2. **Cognitive Assessments**: Bias inventory, thinking patterns
3. **Self-Discovery**: Values, strengths, personality

#### Assessment Flow
- Question presentation (single or multiple per page)
- Progress indication
- Answer validation
- Skip/back navigation
- Results calculation
- Score interpretation
- Recommendations generation

#### Scoring System
- Automated scoring algorithms
- Severity level determination
- Comparison with clinical norms
- Historical tracking
- Progress visualization

---

### 4. **Learning Modules**

#### Module Structure
- Sequential lessons/sections
- Mixed content types (text, video, interactive)
- Progress tracking
- Knowledge checks/quizzes
- Completion certificates
- Bookmark/resume capability

#### Content Types
- **Reading Materials**: Articles, guides
- **Videos**: Instructional content (future)
- **Interactive Exercises**: Practice activities
- **Quizzes**: Knowledge verification
- **Worksheets**: Downloadable PDFs

---

### 5. **Community Features**

#### Discussion Board
- **Thread Creation**: Title, content, tags, anonymity option
- **Replying**: Nested replies, threading
- **Interactions**: Like/dislike, flag/report
- **Moderation**: Community guidelines enforcement
- **Search**: Find discussions by keyword

#### Bias Detection (AI Feature)
- Real-time content analysis
- Identifies cognitive biases in posts
- Provides educational feedback
- Suggests reframes
- Optional feature (user can ignore)

#### Support Groups
- Category-based groups
- Join/leave functionality
- Group discussions
- Scheduled events
- Member directory

---

### 6. **Resource Management**

#### Educational Content
- **Articles**: Mental health topics
- **Guides**: Step-by-step instructions
- **Videos**: Educational content (future)
- **Infographics**: Visual information

#### Self-Help Tools
- **Breathing Exercises**: Interactive timers
- **Thought Records**: CBT worksheets
- **Meditation**: Guided audio (future)
- **Mood Tracking**: Daily check-ins

#### Professional Directory
- **Search**: Location-based, specialty, insurance
- **Profiles**: Provider information
- **Ratings**: Community reviews
- **Contact**: Direct communication

---

### 7. **Analytics & Insights**

#### Data Visualization
- **Line Charts**: Trends over time
- **Bar Charts**: Comparative data
- **Calendar Heatmaps**: Activity patterns
- **Progress Bars**: Goal completion
- **Word Clouds**: Journal themes (future)

#### AI-Powered Insights
- Pattern recognition
- Predictive analytics
- Personalized recommendations
- Correlation analysis
- Risk assessment

---


## 🔄 State Management

### Authentication Context
```js
// AuthContext
{
    user: Object|null,
    session: Object|null,
    signUp: Function,
    signIn: Function,
    signOut: Function,
    loading: Boolean
}
```

### Query Keys Structure
```js
['journalEntries', userId]
['assessment', assessmentId]
['modules', { status: 'active' }]
['communityPosts', { page: 1, filter: 'recent' }]
```

---

## 🗺️ Navigation Structure

### Public Navigation
```
Navbar (Fixed Top)
├── Logo (links to /)
├── Features dropdown
├── About
├── Resources
└── Auth buttons
    ├── Sign In
    └── Get Started
```

### Authenticated Navigation
```
Sidebar (Fixed Left, 256px wide)
├── Logo
├── Dashboard
├── Assessments
├── Journal
├── Insights
├── Modules
├── Community
├── Resources
│   ├── Educational Materials (submenu)
│   ├── Self-Help Tools (submenu)
│   └── Find Help (submenu)
└── Settings

Bottom Section:
├── User profile card
├── Crisis resources link
└── Sign out
```

### Mobile Navigation (< 768px)
- Hamburger menu icon
- Slide-in sidebar
- Bottom navigation bar (future)
- Swipe gestures (future)

---

## 🎭 User Personas & Journeys

### Persona 1: Sarah (Anxiety Management)
**Background**: 28, software developer, experiences work-related anxiety

**Journey**:
1. Discovers Mindfluence through search for anxiety tools
2. Signs up → Completes GAD-7 assessment
3. Results show moderate anxiety
4. Starts "Anxiety Toolkit" module
5. Uses breathing exercises during work stress
6. Journals regularly, tracking patterns
7. Sees progress in Insights dashboard
8. Joins anxiety support community
9. Shares techniques that work for her
10. Progress tracked over 3 months, anxiety score improves

**Key Features Used**:
- Assessments (GAD-7)
- Anxiety Toolkit module
- Breathing exercises tool
- Journal with mood tracking
- Insights dashboard
- Community support group

---

### Persona 2: Marcus (Career Exploration)
**Background**: 35, unhappy in current job, exploring career change

**Journey**:
1. Looking for career clarity tools
2. Signs up → Takes Core Values Assessment
3. Discovers values-career misalignment
4. Starts "Career Path Explorer" module
5. Uses thought challenging to address fears
6. Joins career transition support group
7. Creates career action plan in journal
8. Tracks decision-making biases
9. Uses insights to make informed choice
10. Transitions to new career aligned with values

**Key Features Used**:
- Core Values Assessment
- Cognitive Bias Inventory
- Career Path Explorer module
- Thought challenging tool
- Journal for planning
- Community career group

---

### Persona 3: Emily (Mental Health Awareness)
**Background**: 22, college student, learning about mental health

**Journey**:
1. Psychology course assignment on mental health
2. Signs up to explore educational resources
3. Reads articles on depression, anxiety, resilience
4. Takes assessments out of curiosity
5. Starts mindfulness meditation
6. Shares resources with friends
7. Becomes regular journaler
8. Uses platform for self-care routine
9. Monitors own mental health proactively
10. Recommends to peers struggling

**Key Features Used**:
- Educational materials
- Multiple assessments
- Mindfulness meditation tool
- Journal for reflection
- Community discussions (observer)

---

## 🚀 Performance Optimizations

### Code Splitting
- Route-based lazy loading
- Component-level code splitting
- Dynamic imports for heavy features

### Data Fetching
- React Query caching
- Prefetching on hover
- Background revalidation
- Optimistic updates

### Asset Optimization
- Image lazy loading
- SVG icons (inline for critical)
- Font subsetting
- CSS purging (Tailwind)

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

---

## 🔮 Future Enhancements

### Planned Features
1. **Mobile App**: Native iOS/Android or PWA
2. **Video Content**: Educational videos, meditation guides
3. **AI Chatbot**: 24/7 support companion
4. **Wearable Integration**: Apple Health, Fitbit sync
5. **Therapist Portal**: Professional account type
6. **Group Therapy Sessions**: Live video sessions
7. **Voice Journaling**: Audio entry recording
8. **Gamification**: Achievement system, streaks, rewards
9. **Social Sharing**: Progress milestones, articles
10. **Multi-language**: Internationalization support

### Technical Debt Items
- Comprehensive unit testing
- E2E testing with Playwright
- Performance monitoring (Web Vitals)
- Error tracking (Sentry integration)
- Analytics implementation
- A/B testing framework
- Documentation generation

---

## 📊 Success Metrics

### User Engagement
- Daily/Monthly Active Users (DAU/MAU)
- Session duration
- Feature adoption rates
- Retention rate (7-day, 30-day)
- Completion rates (assessments, modules)

### Mental Health Outcomes
- Assessment score improvements
- Journal entry frequency
- Tool usage patterns
- Community engagement
- Professional help seeking

### Technical Metrics
- Page load time (< 2s)
- Time to Interactive (< 3s)
- Error rates (< 0.1%)
- API response time (< 200ms)
- Crash-free sessions (> 99.9%)

---

## 🎓 Educational Foundation

All content and tools are based on evidence-based practices:
- **Cognitive Behavioral Therapy (CBT)**
- **Dialectical Behavior Therapy (DBT)**
- **Mindfulness-Based Stress Reduction (MBSR)**
- **Acceptance and Commitment Therapy (ACT)**
- **Positive Psychology**
- **Neuroscience research**

### Clinical Partnerships (Future)
- Collaboration with licensed mental health professionals
- Content review by clinical psychologists
- Research partnerships with universities
- Clinical trial participation

---

## ⚠️ Important Disclaimers

### Throughout the Application

**Prominent Disclaimers Appear:**
1. **Landing Page**: "Not therapy or diagnosis, seek professional help for crisis"
2. **Assessment Results**: "For self-awareness only, not diagnostic"
3. **Community**: "Peer support, not professional advice"
4. **Resources**: "Emergency resources for immediate help"
5. **Tools**: "Complements but doesn't replace professional treatment"

### Crisis Support Integration
- **Always Accessible**: Sidebar link, footer link, dedicated page
- **Prominent**: Red/orange color scheme for visibility
- **Clear Contact Info**: Phone numbers, text lines, websites
- **No Barriers**: No login required for crisis resources

---

## 🎯 Conclusion


Veramind provides a comprehensive, user-friendly platform for mental health self-awareness and management. The frontend architecture prioritizes:

✅ **User Experience**: Intuitive navigation, clear information hierarchy
✅ **Accessibility**: Inclusive design for all users
✅ **Privacy**: Secure, privacy-first approach
✅ **Evidence-Based**: Clinical foundations for all content
✅ **Safety**: Prominent crisis resources and appropriate disclaimers
✅ **Engagement**: Interactive tools and community support
✅ **Growth**: Structured learning paths and progress tracking
✅ **Scalability**: Modern tech stack for future expansion

The platform serves as a valuable tool for individuals seeking to understand themselves better, manage mental health challenges, and develop healthier thought patterns—while always emphasizing the importance of professional help when needed.

---

**Document Version**: 1.0
**Last Updated**: November 15, 2025
**Maintained By**: Veramind Development Team