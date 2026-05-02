# VeraMind Architecture Documentation

## 📐 System Architecture Overview

VeraMind is built as a modern, full-stack web application with a clear separation of concerns between frontend, backend services, and AI/ML components.

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Browser)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vue 3 + Vite Frontend                                  │  │
│  │  - Vue Router (manual route definitions)               │  │
│  │  - Components (Reusable UI)                            │  │
│  │  - Composables (useAuth, useToast, etc.)               │  │
│  │  - Custom CSS (No frameworks)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │
┌───────────────────────────┴───────────────────────────────┐
│                    Serverless / API Layer                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Serverless Functions or External APIs               │  │
│  │  - /api/health                                        │  │
│  │  - /api/gemini/chat (proxy to Gemini, kept server-side)
│  │  - /api/journal/insights (future)
│  │  - /api/rag/query (future)
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│   Supabase     │  │  Google Gemini  │  │    Cohere      │
│   (Database)   │  │      API        │  │     API        │
│                │  │                 │  │   (ReRank)     │
│ - PostgreSQL   │  │ - Chat          │  │                │
│ - pgvector     │  │ - Function      │  │                │
│ - Auth         │  │   Calling       │  │                │
│ - Realtime     │  │ - Embeddings    │  │                │
└────────────────┘  └─────────────────┘  └────────────────┘
        │
        │
┌───────▼──────────────────────────────────────────────────┐
│         External Services (Future)                        │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ Hugging Face     │  │  GitHub Actions   │             │
│  │ Spaces           │  │  (Batch Jobs)      │             │
│  │                  │  │                  │             │
│  │ - Engagement     │  │ - Archetype       │             │
│  │   Model (FastAPI)│  │   Model (UMAP +   │             │
│  │                  │  │   HDBSCAN)       │             │
│  │ - Journal        │  │                  │             │
│  │   Insights       │  │                  │             │
│  │   (DistilBERT)   │  │                  │             │
│  └──────────────────┘  └──────────────────┘             │
└───────────────────────────────────────────────────────────┘
```

## 📂 Frontend Architecture

### Component Structure

```
components/
├── ui/                    # Base UI components (future)
│   ├── Button.vue
│   ├── Card.vue
│   └── Input.vue
├── DashboardLayout.vue     # Main layout wrapper
├── Navbar.vue             # Top navigation
├── Sidebar.vue            # Side navigation
├── Footer.vue             # Footer component
└── ProtectedRoute.vue     # Auth guard wrapper
```

### Page Structure (File-based Routing)

```
pages/
├── index.vue              # Landing page (/)
├── login.vue              # Login page (/login)
├── signup.vue             # Signup page (/signup)
├── dashboard.vue          # Dashboard (/dashboard)
├── journal.vue            # Journal page (/journal)
├── assessments.vue        # Assessments list (/assessments)
├── insights.vue           # Insights page (/insights)
├── modules.vue            # Learning modules (/modules)
├── community.vue          # Community (/community)
├── resources.vue          # Resources hub (/resources)
└── settings.vue           # Settings (/settings)
```

### Composables Pattern

Composables provide reusable, reactive logic:

- **useAuth.js**: Authentication state and methods
- **useMobile.js**: Responsive breakpoint detection
- **useToast.js**: Global notification system

### State Management

- **No Pinia/Vuex**: Using composables and reactive refs
- **Server State**: Direct Supabase queries with reactive refs
- **Client State**: Component-level reactive state

## 🔧 Backend Architecture

### Serverless / External API Routes

Server-side functionality should be implemented as serverless or external API routes (Vercel Serverless Functions, Netlify Functions, or Supabase Edge Functions). Keep secrets and paid-API calls on the server side.

Example layout for serverless functions:

```
api/
├── health.js
├── gemini/chat.js
├── journal/insights.js
└── rag/query.js
```

### API Design Principles

1. **RESTful**: Clear resource-based endpoints
2. **Error Handling**: Consistent error responses
3. **Authentication**: Supabase Auth middleware
4. **Rate Limiting**: (Future: Vercel Edge Config)

## 🗄️ Database Architecture

### Supabase PostgreSQL Schema

**Core Tables**:
- `profiles`: User profile data
- `journal_entries`: Journal entries with sentiment analysis
- `assessments`: Assessment results and scores
- `module_progress`: Learning module completion tracking

**Community Tables**:
- `community_posts`: Discussion posts
- `community_replies`: Nested replies
- `support_groups`: Support group definitions
- `group_memberships`: User-group relationships

**Content Tables**:
- `educational_articles`: Articles with vector embeddings for RAG

### Row Level Security (RLS)

All tables use RLS policies:
- Users can only access their own data
- Community posts are public (read-only for others)
- Educational articles are public

### Vector Search (pgvector)

- `educational_articles.embedding`: Vector column for semantic search
- Used for RAG (Retrieval-Augmented Generation)
- Cosine similarity for relevance ranking

## 🤖 AI/ML Architecture

### Current Implementation

1. **Gemini API Integration**
   - Direct API calls from server routes
   - Chat completions
   - Function calling (future)

### Planned Models

#### 1. Engagement Model
- **Tech**: XGBoost + MLflow
- **Deployment**: FastAPI on Hugging Face Spaces
- **Input**: User activity features
- **Output**: Engagement score (0-100)

#### 2. Archetype Model
- **Tech**: UMAP + HDBSCAN
- **Deployment**: GitHub Actions (scheduled batch job)
- **Input**: User behavior vectors
- **Output**: Archetype classification

#### 3. Mindful Focus Tool
- **Tech**: OpenCV.js / MediaPipe.js
- **Deployment**: Client-side (browser)
- **Input**: Webcam feed
- **Output**: Gaze estimation, focus metrics

#### 4. Journal Insights
- **Tech**: DistilBERT (fine-tuned) + Gemini
- **Deployment**: FastAPI on Hugging Face Spaces
- **Input**: Journal entry text
- **Output**: Cognitive distortion detection + sentiment

#### 5. AI Guide (RAG)
- **Tech**: pgvector + Cohere ReRank + Gemini
- **Deployment**: Serverless API routes (Vercel / Netlify serverless functions or Supabase Edge Functions)
- **Flow**:
    1. Query → Vector search (pgvector)
    2. Top 10 results → Cohere ReRank
    3. Top 3 → Gemini for answer generation (server-side)

#### 6. Growth Plan Agent
- **Tech**: LangChain.js + Gemini Function Calling
- **Deployment**: Serverless API routes or external API server (avoid exposing secrets in client)
- **Tools**: Supabase Edge Functions (optional for secure short-lived operations)
- **Flow**: Agentic loop with tool calling (all heavy work runs server-side)

## 🔐 Security Architecture

### Authentication Flow

```
User → Sign Up/Login → Supabase Auth → JWT Token → Stored in Cookie
                                                      │
                                                      └─→ Protected Routes Check
```

### Data Security

1. **Row Level Security**: Database-level access control
2. **API Keys**: Environment variables (never in code)
3. **HTTPS Only**: All traffic encrypted
4. **CORS**: Configured for Vercel domain only

### Privacy

- User data encrypted at rest (Supabase)
- No third-party analytics (privacy-first)
- User can export/delete all data

## 📊 Data Flow Examples

### Journal Entry Creation

```
User Input → Vue Component → journalService.createEntry()
    ↓
Supabase Client → INSERT INTO journal_entries
    ↓
Database Trigger → (Future: Call Journal Insights API)
    ↓
Update UI with new entry
```

### RAG Query Flow

```
User Query → Nuxt Server Route (/api/rag/query)
    ↓
1. Generate query embedding (Gemini)
    ↓
2. Vector search in pgvector (Supabase)
    ↓
3. Get top 10 results
    ↓
4. Re-rank with Cohere API
    ↓
5. Top 3 → Gemini for answer
    ↓
Return answer to client
```

## 🚀 Deployment Architecture

### Vercel Deployment

```
GitHub Repository
    ↓
Vercel (Auto-deploy on push)
    ↓
Build Nuxt 3 App
    ↓
Deploy Serverless Functions
    ↓
CDN Distribution
```

### Environment Variables

All sensitive data in environment variables:
- Supabase credentials
- API keys
- Feature flags

## 🔄 State Management Flow

### Client-Side State

```
Component State (ref/reactive)
    ↓
Composables (useAuth, useToast)
    ↓
Services (journalService)
    ↓
Supabase Client
    ↓
Database
```

### Server-Side State

```
Server Route
    ↓
Runtime Config (env vars)
    ↓
External APIs (Gemini, Cohere)
    ↓
Response to Client
```

## 📈 Scalability Considerations

### Current (Free Tier)

- **Vercel**: 100GB bandwidth/month
- **Supabase**: 500MB database, 2GB storage
- **Gemini API**: Free tier limits
- **Cohere**: Free tier limits

### Future Scaling

1. **Database**: Upgrade Supabase plan
2. **CDN**: Vercel Edge Network (automatic)
3. **Caching**: Redis for frequently accessed data
4. **Queue**: Background job processing
5. **Monitoring**: Error tracking, analytics

## 🧪 Testing Strategy (Future)

### Unit Tests
- Composables
- Utility functions
- Services

### Integration Tests
- API endpoints
- Database operations
- Auth flows

### E2E Tests
- User journeys
- Critical paths
- Cross-browser testing

## 📝 Code Organization Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **DRY**: Reusable composables and utilities
3. **Single Responsibility**: Each component/service has one job
4. **Type Safety**: (Future: TypeScript migration)
5. **Documentation**: Inline comments for complex logic

## 🔮 Future Architecture Enhancements

1. **TypeScript Migration**: Type safety across codebase
2. **GraphQL API**: (Optional) For complex queries
3. **WebSocket**: Real-time features (Supabase Realtime)
4. **Edge Functions**: Supabase Edge Functions for secure operations
5. **Microservices**: Split AI models into separate services
6. **Caching Layer**: Redis for performance
7. **Message Queue**: For async processing

---

**Architecture is designed to be:**
- ✅ Scalable
- ✅ Maintainable
- ✅ Secure
- ✅ Free-tier compatible
- ✅ Developer-friendly

