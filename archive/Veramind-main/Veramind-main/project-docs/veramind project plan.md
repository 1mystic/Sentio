# Veramind Frontend: Project Plan (Updated Tech Stack)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Updated Technology Stack](#updated-technology-stack)
3. [Application Architecture](#application-architecture)
4. [User Flows](#user-flows)
5. [Pages & Components](#pages--components)
6. [UI/UX Design System](#uiux-design-system)
7. [Features & Functionality](#features--functionality)
8. [State Management](#state-management)
9. [Navigation Structure](#navigation-structure)

---

## 🎯 Overview


Veramind is a comprehensive mental health and self-discovery platform that provides users with tools for understanding cognitive patterns, managing anxiety, exploring career paths, and improving overall mental wellbeing through evidence-based assessments, journaling, educational modules, and community support.

---

## 🚀 Updated Technology Stack


### Frontend (App)
- **Framework**: Vue 3 (JavaScript only, no TypeScript) — Vite + Vue Router (no Nuxt)
- **Build Tool**: Vite (standalone)
- **Styling**: Custom CSS (Vanilla, no UI Libraries/Frameworks). All components (buttons, cards, forms, layouts) will be built from scratch using custom assets/css/main.css
- **Deployment**: Vercel (or Netlify) for static hosting; serverless API endpoints (Vercel Serverless Functions), Supabase Edge Functions, or an external API server are recommended for backend routes

### Backend (Data & Auth)
- **Database (Relational)**: Supabase (Free-tier Postgres for users, profiles, journal entries, assessments, etc.)
- **Authentication**: Supabase Auth (Handles email, password, and Google/OAuth logins)
- **Real-time (Community)**: Supabase Realtime (Powers the live community chat feed)

### Backend (AI & Machine Learning)
- **AI Model 1 (Classical ML)**: FastAPI (Python) + Hugging Face Spaces (Free-tier CPU-based hosting for Python-based XGBoost/scikit-learn models)
- **AI Models 2-6 (NLP, RAG, Agents)**: Google AI Studio (Gemini 2.5 Pro API) (Free, powerful tier for all generative and analytical NLP tasks)
- **Vector Database (RAG)**: Supabase pgvector (Free, built-in vector extension for Postgres; stores article embeddings for RAG)
- **AI Logic (Orchestration)**: Serverless or external API routes (Vercel Serverless Functions, Supabase Edge Functions, or an Express/Fastify API) using LangChain.js (or the Vercel AI SDK) to coordinate RAG, agents, and API calls

---



## 🏗️ Application Architecture

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

### Authentication Flow
- Sign Up: Landing → Sign Up → Dashboard (with error handling)
- Login: Landing → Login → Dashboard (with forgot password, redirect, etc.)
- Protected Route: Redirect unauthenticated users to login, then back to requested page

### Dashboard Flow
- Welcome message, quick actions (check-in, module, journal), recent insights, active modules, crisis support
- Navigation: Quick actions, module cards, sidebar, crisis banner

### Assessment Flow
- Discovery: Tabs for available/completed, card grid, start assessment
- Taking: Instructions, single-question screens, progress, review, submit, results (score, severity, recommendations)
- Types: GAD-7, PHQ-9, Cognitive Bias Inventory, Core Values Assessment

### Journal Flow
- Tabs: Write, Past Entries, Calendar View
- Write: Date selector, prompt rotation, rich text editor, save entry, tags/mood
- Past Entries: Chronological list, filters, actions (edit, delete, share/export)
- Calendar: Monthly grid, entry highlights, consistency tracking
- Analytics: Sentiment, mood trends, themes, frequency

### Learning Modules Flow
- Discovery: Grid of modules, cards with progress
- Progression: Module detail, lessons, sequential unlocking, interactive content, quizzes, completion tracking

### Community Flow
- Tabs: Discussions, Support Groups
- Discussions: Thread list, create post, reply, like/dislike, report, bias check tool
- Support Groups: Categories, group cards, join/leave, group detail (discussions, events, directory, resources)

### Resources Flow
- Hub: Crisis banner, cards for Educational Materials, Self-Help Tools, Find Help
- Educational Materials: Article library, filters, cards, full article view, engagement features
- Self-Help Tools: Card grid, breathing exercises, thought challenging, meditation, mood tracking
- Find Help: Professional directory, search/filter, provider cards, profile details, crisis resources, organizations

### Insights & Analytics Flow
- Personal dashboard: Metrics, trends, pattern insights, achievements, recommendations
- Assessment history: List, score trends, comparison charts
- Journal insights: Frequency, themes, sentiment, word cloud
- Progress reports: Summaries, reviews, export/share

### Settings Flow
- Account: Profile, password, account actions
- Privacy: Data preferences, communications
- Notifications: Email/push, frequency
- Preferences: Display, language, timezone
- Connected Services: Calendar, wearables, provider connection
- Help & Support: FAQ, contact, bug report, feature requests, terms

---

## 🎨 UI/UX Design System

### Design Principles
- Calming/supportive, accessible/inclusive, privacy-first, progressive disclosure

### Color Palette, Typography, Spacing
- As per original doc (see above)

### Component Patterns
- Cards: Custom, white bg, border, hover shadow, active border, padding
- Buttons: Custom, primary/secondary/outline/ghost/destructive, size variants
- Forms: Custom, input focus/error, labels, validation, disabled state
- Navigation: Sidebar/navbar, icons, badges

---

## 🔧 Features & Functionality

### Authentication System
- Registration: Email/password, validation, terms, auto-login
- Login: Email/password, remember me, password reset, session management
- Protected Routes: Auth check, redirect, session expiry

### Journal System
- Entry CRUD: Rich text, view by date, edit, delete
- Prompts: Rotating, inspiration
- Calendar: Visual tracking
- Search: Keyword
- Export: Download (future)
- Auto-save: Drafts (future)

#### Data Structure
```js
// JournalEntry
{
	id: String,
	user_id: String,
	date: String, // YYYY-MM-DD
	content: String,
	prompt: String,
	created_at: Timestamp,
	updated_at: Timestamp,
	tags: Array,
	mood: Number,
	sentiment: Object // ML analysis
}
```

### Assessment System
- Types: GAD-7, PHQ-9, Cognitive, Self-Discovery
- Flow: Question screens, progress, validation, navigation, results, scoring, recommendations
- Scoring: Automated, severity, historical tracking, visualization

### Learning Modules
- Structure: Sequential lessons, mixed content, progress, quizzes, certificates, resume/bookmark
- Content: Reading, video, interactive, quizzes, worksheets

### Community Features
- Discussion Board: Thread creation, reply, like/dislike, report, moderation, search
- Bias Detection: AI analysis, feedback, reframe suggestions
- Support Groups: Categories, join/leave, events, directory

### Resource Management
- Educational: Articles, guides, videos, infographics
- Self-Help: Breathing, thought records, meditation, mood tracking
- Directory: Search, profiles, ratings, contact

### Analytics & Insights
- Visualization: Line/bar charts, heatmaps, progress bars, word clouds
- AI Insights: Pattern recognition, recommendations, risk assessment

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
Navbar: Logo, Features, About, Resources, Auth buttons

### Authenticated Navigation
Sidebar: Logo, Dashboard, Assessments, Journal, Insights, Modules, Community, Resources (submenus), Settings, profile card, crisis link, sign out

### Mobile Navigation
Hamburger, slide-in sidebar, bottom bar (future), swipe gestures (future)

---

## 🎭 User Personas & Journeys

### Persona 1: Sarah (Anxiety Management)
Journey: Signs up, completes GAD-7, starts Anxiety Toolkit, uses breathing exercises, journals, sees progress, joins support group, shares techniques, tracks progress

### Persona 2: Marcus (Career Exploration)
Journey: Signs up, takes Core Values, starts Career Path Explorer, uses thought challenging, joins career group, plans in journal, tracks biases, uses insights, transitions career

### Persona 3: Emily (Mental Health Awareness)
Journey: Signs up, explores resources, reads articles, takes assessments, starts meditation, shares resources, journals, uses platform for self-care, monitors health, recommends to peers

---

## 🚀 Performance Optimizations

- Code splitting, lazy loading, dynamic imports
- Data fetching: caching, prefetch, background revalidation, optimistic updates
- Asset optimization: lazy images, SVG icons, font subsetting, CSS purging
- Accessibility: semantic HTML, ARIA, keyboard nav, focus, screen reader

---

## 🔮 Future Enhancements

- Mobile app, video content, AI chatbot, wearable integration, therapist portal, group therapy, voice journaling, gamification, social sharing, multi-language
- Technical debt: testing, monitoring, error tracking, analytics, A/B testing, docs

---

## 📊 Success Metrics

- User engagement: DAU/MAU, session duration, feature adoption, retention, completion rates
- Mental health outcomes: score improvements, journal frequency, tool usage, community engagement, help seeking
- Technical: load time, TTI, error rates, API response, crash-free sessions

---

## 🎓 Educational Foundation

- CBT, DBT, MBSR, ACT, Positive Psychology, Neuroscience
- Clinical partnerships (future): licensed professionals, content review, research, trials

---

## ⚠️ Important Disclaimers

- Prominent disclaimers: not therapy, not diagnostic, peer support, emergency resources, tools complement not replace treatment
- Crisis support: always accessible, prominent, clear contact info, no barriers

---

---

**Document Version**: 1.1
**Last Updated**: November 18, 2025
**Maintained By**: Veramind Development Team
