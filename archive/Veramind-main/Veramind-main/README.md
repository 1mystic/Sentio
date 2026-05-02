# VeraMind

**AI-Powered Mental Wellness Platform**

VeraMind is a comprehensive mental wellness web application built with Vue 3, Vite, and Python. It focuses on user self-awareness, cognitive pattern identification, and anxiety management through evidence-based assessments, journaling, educational modules, and AI-powered insights.

## 🎯 Project Overview

VeraMind helps users:
- **Self-awareness**: Identify cognitive biases and thought patterns
- **Mental health management**: Track anxiety, stress, and mood
- **Personal growth**: Complete structured learning modules
- **Community support**: Connect with peers and resources

**Important**: VeraMind is not a replacement for professional therapy or medical treatment. Always seek professional help in crisis situations.

## 🚀 Tech Stack

-### Frontend
- **Framework**: Vue 3 with Vite (no Nuxt)
- **Styling**: Custom CSS/SCSS (no frameworks)
- **Deployment**: Vercel (Free Tier)

### Backend & Services
- **Database**: Supabase (PostgreSQL + pgvector)
- **Authentication**: Supabase Auth
- **AI/ML**: Google Gemini 1.5 Pro API
- **AI Orchestration**: LangChain.js
- **Vector Search**: Supabase pgvector
- **Re-ranking**: Cohere API (Free Tier)

### AI/ML Models
1. **Engagement Model**: XGBoost + MLflow → FastAPI on Hugging Face Spaces
2. **Archetype Model**: UMAP + HDBSCAN → GitHub Actions batch job
3. **Mindful Focus Tool**: OpenCV.js/MediaPipe.js → Client-side browser
4. **Journal Insights**: DistilBERT + Gemini → FastAPI on Hugging Face Spaces
5. **AI Guide**: RAG with pgvector + Cohere ReRank + Gemini
6. **Growth Plan Agent**: LangChain.js + Gemini Function Calling

## 📁 Project Structure

```
veramind/
├── assets/
│   └── css/
│       └── main.css          # Global styles & design system
├── components/               # Vue components
│   ├── ui/                   # Base UI components
│   ├── DashboardLayout.vue
│   ├── Navbar.vue
│   ├── Sidebar.vue
│   ├── Footer.vue
│   └── ProtectedRoute.vue
├── composables/              # Vue composables
│   ├── useAuth.js
│   ├── useMobile.js
│   └── useToast.js
├── integrations/             # External service integrations
│   └── supabase/
│       ├── client.js
│       └── types.js
├── pages/                    # Route page components (use Vue Router)
│   ├── index.vue
│   ├── login.vue
│   ├── signup.vue
│   └── dashboard.vue
├── server/ (optional)
│   └── api/                  # Serverless / server API functions (Vercel / Netlify / Supabase Edge)
│       ├── health.js
│       └── gemini/
│           └── chat.js
├── services/                 # API service functions
│   └── journalService.js
├── utils/                    # Utility functions
│   └── utils.js
├── app.vue                   # Root component
├── (optional) nuxt.config.js  # Legacy Nuxt configuration (ignored when running as Vite app)
└── package.json
```

## 🛠️ Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Supabase account (free tier)
- Google Gemini API key
- Cohere API key (for ReRank)

### Installation

1. **Clone the repository** (or navigate to project directory)

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory (use `VITE_` prefix for client-exposed variables):
   ```env
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_GEMINI_API_KEY=your_gemini_api_key
   VITE_COHERE_API_KEY=your_cohere_api_key
   ```

4. **Set up Supabase**:
   - Create a new Supabase project
   - Run the database migrations (see `SETUP.md`)
   - Enable pgvector extension

5. **Run the development server**:
   ```bash
   npm run dev
   ```

6. **Open your browser**:
   Navigate to `http://localhost:5173` (default Vite dev server) or the URL printed by Vite

## 📚 Documentation

- **[SETUP.md](./SETUP.md)**: Detailed setup instructions
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: System architecture and design decisions
- **[FRONTEND_DOCUMENTATION.md](./FRONTEND_DOCUMENTATION.md)**: Frontend feature documentation
- **[veramind project plan.md](./veramind%20project%20plan.md)**: Project roadmap

## 🎨 Design System

VeraMind uses a custom CSS design system with:
- **Primary Color**: Purple (#9b87f5)
- **Secondary Color**: Blue (#6bb6ff)
- **Typography**: System fonts with consistent sizing
- **Spacing**: 4px scale
- **Components**: Custom-built (no UI frameworks)

See `assets/css/main.css` for full design system.

## 🔐 Authentication

VeraMind uses Supabase Auth for:
- Email/password authentication
- Session management
- Protected routes
- User profiles

## 🧪 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors

### Code Style

- Vue 3 Composition API with `<script setup>`
- Custom CSS only (no Tailwind, Bootstrap, etc.)
- ESLint for code quality
- Consistent naming conventions

## 🚢 Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy automatically on push

See `SETUP.md` for detailed deployment instructions.

## 📊 Database Schema

Key tables:
- `profiles` - User profiles
- `journal_entries` - Journal entries
- `assessments` - Assessment results
- `module_progress` - Learning module progress
- `community_posts` - Community discussions
- `educational_articles` - Educational content (with embeddings)

See `SETUP.md` for full schema and migrations.

## 🤖 AI/ML Integration

### Current Implementation
- Gemini API integration for chat
- Server routes for AI orchestration

### Planned Models
See project plan for details on the 6 AI/ML models.

## 🧩 Features

### Implemented
- ✅ Authentication (sign up, sign in, sign out)
- ✅ Landing page
- ✅ Dashboard layout
- ✅ Protected routes
- ✅ Basic navigation

### In Progress
- 🔄 Journal system
- 🔄 Assessments
- 🔄 Learning modules
- 🔄 Community features
- 🔄 AI insights

## 📝 License

This project is for portfolio/educational purposes.

## ⚠️ Disclaimers

- **Not Therapy**: VeraMind is not a replacement for professional therapy
- **Not Diagnostic**: Assessments are for self-awareness only
- **Crisis Support**: Always accessible crisis resources
- **Privacy**: User data is handled according to privacy policy

## 🤝 Contributing

This is a portfolio project. For questions or suggestions, please open an issue.

## 📞 Support

For crisis support, see the Crisis Resources page in the app or contact:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741

---

**Built with ❤️ for mental wellness awareness**

