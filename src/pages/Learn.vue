<template>
  <div class="learn-page">
    <div class="page-header">
      <h1 class="page-title">Learn</h1>
      <p class="page-sub">Deepen your understanding of cognitive biases with curated guides and exercises.</p>
    </div>

    <!-- Category filter -->
    <div class="filter-row">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="filter-pill"
        :class="{ active: activeCategory === cat.id }"
        @click="activeCategory = cat.id"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Featured article -->
    <div v-if="featured" class="featured-card" @click="openArticle(featured)">
      <div class="featured-badge">Featured</div>
      <div class="featured-category">{{ featured.category }}</div>
      <h2 class="featured-title">{{ featured.title }}</h2>
      <p class="featured-excerpt">{{ featured.excerpt }}</p>
      <div class="featured-meta">
        <span class="meta-tag">{{ featured.readTime }} min read</span>
        <span class="meta-tag">{{ featured.level }}</span>
      </div>
    </div>

    <!-- Article grid -->
    <div class="articles-grid">
      <div
        v-for="article in filteredArticles"
        :key="article.id"
        class="article-card"
        @click="openArticle(article)"
      >
        <div class="article-icon" :style="{ background: article.iconBg }">
          <component :is="article.icon" :size="20" :color="article.iconColor" />
        </div>
        <div class="article-body">
          <div class="article-category">{{ article.category }}</div>
          <h3 class="article-title">{{ article.title }}</h3>
          <p class="article-excerpt">{{ article.excerpt }}</p>
          <div class="article-meta">
            <span class="meta-tag">{{ article.readTime }} min</span>
            <span class="meta-tag level" :class="article.level.toLowerCase()">{{ article.level }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Exercises section -->
    <div class="section-header">
      <h2 class="section-title">Reflection Exercises</h2>
      <p class="section-sub">Short, practical exercises to build self-awareness.</p>
    </div>

    <div class="exercises-list">
      <div v-for="ex in exercises" :key="ex.id" class="exercise-card">
        <div class="exercise-num">{{ ex.num }}</div>
        <div class="exercise-content">
          <h4 class="exercise-title">{{ ex.title }}</h4>
          <p class="exercise-desc">{{ ex.desc }}</p>
          <div class="exercise-actions">
            <span class="ex-time">⏱ {{ ex.duration }}</span>
            <button class="btn-sm" @click="startExercise(ex)">Start →</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Article modal -->
    <div v-if="activeArticle" class="modal-overlay" @click.self="closeArticle">
      <div class="modal-panel">
        <button class="modal-close" @click="closeArticle">✕</button>
        <div class="modal-category">{{ activeArticle.category }}</div>
        <h2 class="modal-title">{{ activeArticle.title }}</h2>
        <div class="modal-meta">
          <span class="meta-tag">{{ activeArticle.readTime }} min read</span>
          <span class="meta-tag level" :class="activeArticle.level.toLowerCase()">{{ activeArticle.level }}</span>
        </div>
        <div class="modal-body" v-html="activeArticle.body"></div>
        <div class="modal-footer">
          <button class="btn-outline" @click="closeArticle">Close</button>
          <router-link v-if="activeArticle.biasSlug" :to="`/explore/${activeArticle.biasSlug}`" class="btn-primary" @click="closeArticle">
            Explore This Bias →
          </router-link>
          <router-link v-else to="/journal/new" class="btn-primary" @click="closeArticle">
            Reflect in Journal →
          </router-link>
        </div>
      </div>
    </div>

    <!-- Exercise modal -->
    <div v-if="activeExercise" class="modal-overlay" @click.self="closeExercise">
      <div class="modal-panel">
        <button class="modal-close" @click="closeExercise">✕</button>
        <h2 class="modal-title">{{ activeExercise.title }}</h2>
        <div class="exercise-steps">
          <div v-for="(step, i) in activeExercise.steps" :key="i" class="exercise-step">
            <div class="step-num">{{ i + 1 }}</div>
            <p class="step-text">{{ step }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-outline" @click="closeExercise">Done</button>
          <router-link to="/journal/new" class="btn-primary" @click="closeExercise">
            Journal About It →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Brain, Zap, Eye, Scale, Clock, AlertTriangle,
  TrendingUp, Users, BookOpen, Target
} from 'lucide-vue-next'

const activeCategory = ref('all')
const activeArticle = ref(null)
const activeExercise = ref(null)

const categories = [
  { id: 'all', label: 'All' },
  { id: 'fundamentals', label: 'Fundamentals' },
  { id: 'decision', label: 'Decision-Making' },
  { id: 'social', label: 'Social' },
  { id: 'self', label: 'Self-Awareness' },
  { id: 'practice', label: 'Practice' },
]

const articles = [
  {
    id: 1,
    category: 'Fundamentals',
    categoryId: 'fundamentals',
    title: 'What Are Cognitive Biases?',
    excerpt: 'A clear introduction to why our brains take mental shortcuts — and why that matters for everyday decisions.',
    readTime: 5,
    level: 'Beginner',
    icon: Brain,
    iconBg: '#eceaf9',
    iconColor: '#9b94e8',
    featured: true,
    biasSlug: null,
    body: `<p>Cognitive biases are systematic patterns of deviation from rational judgment. They arise from the brain's tendency to simplify information processing. While they often serve us well as quick heuristics, they can lead to poor judgments and decisions in certain situations.</p>
<h3>Why do biases exist?</h3>
<p>Our brains process roughly 11 million bits of information per second, but our conscious minds can only handle about 40-50 bits. To cope, the brain uses mental shortcuts — called <strong>heuristics</strong> — that help us make fast decisions without exhausting our cognitive resources.</p>
<h3>The dual-process model</h3>
<p>Psychologist Daniel Kahneman describes two systems of thinking:</p>
<ul>
  <li><strong>System 1</strong>: Fast, automatic, emotional, intuitive</li>
  <li><strong>System 2</strong>: Slow, deliberate, logical, effortful</li>
</ul>
<p>Most biases emerge from System 1 operating unchecked. The goal isn't to eliminate System 1 — it's to know when to invoke System 2.</p>
<h3>Are biases bad?</h3>
<p>Not always. Many biases exist because they were adaptive in ancestral environments. The problem arises when they misfire in modern, complex situations. Awareness is the first step toward better decisions.</p>`,
  },
  {
    id: 2,
    category: 'Decision-Making',
    categoryId: 'decision',
    title: 'Anchoring: Why First Numbers Stick',
    excerpt: 'How an arbitrary number seen first can skew every estimate you make afterward — and how to guard against it.',
    readTime: 4,
    level: 'Beginner',
    icon: Scale,
    iconBg: '#fef3c7',
    iconColor: '#d97706',
    featured: false,
    biasSlug: 'anchoring-bias',
    body: `<p>Anchoring bias occurs when we rely too heavily on the first piece of information we encounter (the "anchor") when making decisions.</p>
<h3>The classic study</h3>
<p>Tversky and Kahneman (1974) showed participants a spinning wheel (rigged to land on 10 or 65). Afterward, participants who saw 65 estimated African countries made up 45% of the UN, while those who saw 10 estimated only 25%. The random number anchored their judgments.</p>
<h3>Where you see it in real life</h3>
<ul>
  <li><strong>Salary negotiation</strong>: Whoever names a number first sets the anchor</li>
  <li><strong>Shopping</strong>: "Was $200, now $120" makes $120 feel like a deal regardless of value</li>
  <li><strong>Performance reviews</strong>: Your first impression of someone's work colors how you rate it later</li>
</ul>
<h3>How to reduce it</h3>
<p>1. Generate your own estimate <em>before</em> looking at any external figures.<br>2. Deliberately consider whether the anchor is relevant to your decision.<br>3. Ask: "What would I think if I had seen a completely different number first?"</p>`,
  },
  {
    id: 3,
    category: 'Fundamentals',
    categoryId: 'fundamentals',
    title: 'Confirmation Bias: The Echo Chamber in Your Head',
    excerpt: 'Why we unconsciously seek out information that confirms what we already believe — and how it polarizes thinking.',
    readTime: 6,
    level: 'Beginner',
    icon: Eye,
    iconBg: '#dcfce7',
    iconColor: '#16a34a',
    featured: false,
    biasSlug: 'confirmation-bias',
    body: `<p>Confirmation bias is the tendency to search for, interpret, and recall information in a way that confirms or supports one's prior beliefs or values.</p>
<h3>Three forms</h3>
<ul>
  <li><strong>Selective search</strong>: We seek confirming evidence (e.g., Googling "reasons to support X")</li>
  <li><strong>Biased interpretation</strong>: Ambiguous evidence gets interpreted as supporting our view</li>
  <li><strong>Selective memory</strong>: We remember hits and forget misses</li>
</ul>
<h3>Why it's dangerous</h3>
<p>Confirmation bias is particularly insidious because it feels like rational evidence-gathering. You genuinely believe you're being objective. The research suggests it increases with emotional investment — the more you care about a topic, the stronger the bias.</p>
<h3>Counter-strategies</h3>
<p>1. <strong>Steelman the opposition</strong>: Articulate the strongest version of the opposing view.<br>2. <strong>Pre-mortem</strong>: Before committing to a belief, ask "How could this be wrong?"<br>3. <strong>Seek disconfirmation</strong>: Actively search for evidence that contradicts your position.</p>`,
  },
  {
    id: 4,
    category: 'Social',
    categoryId: 'social',
    title: 'The Halo Effect in Relationships',
    excerpt: 'How one positive trait causes us to assume other positive traits — and why first impressions are dangerously sticky.',
    readTime: 4,
    level: 'Intermediate',
    icon: Users,
    iconBg: '#fce7f3',
    iconColor: '#be185d',
    featured: false,
    biasSlug: 'halo-effect',
    body: `<p>The halo effect is when a positive impression in one area causes us to view someone more positively in unrelated areas.</p>
<h3>The original experiment</h3>
<p>Psychologist Edward Thorndike (1920) found that military officers rated attractive soldiers as more intelligent, loyal, and capable — qualities completely unrelated to appearance.</p>
<h3>Where it shows up</h3>
<ul>
  <li><strong>Hiring</strong>: Attractive candidates receive higher interview scores</li>
  <li><strong>Education</strong>: Teachers rate students they perceive as hardworking as more intelligent</li>
  <li><strong>Marketing</strong>: Celebrity endorsements transfer positive feelings to products</li>
  <li><strong>Relationships</strong>: Early charm can mask serious incompatibilities</li>
</ul>
<h3>Countering the halo</h3>
<p>Evaluate each attribute independently. In hiring, use structured interviews with separate scoring per competency before seeing overall impressions. In relationships, consciously assess specific behaviors rather than overall "vibes."</p>`,
  },
  {
    id: 5,
    category: 'Self-Awareness',
    categoryId: 'self',
    title: 'Dunning-Kruger: What You Don\'t Know You Don\'t Know',
    excerpt: 'The counterintuitive finding that low competence often comes with high confidence — and what true expertise feels like.',
    readTime: 5,
    level: 'Intermediate',
    icon: TrendingUp,
    iconBg: '#ede9fe',
    iconColor: '#7c3aed',
    featured: false,
    biasSlug: 'dunning-kruger',
    body: `<p>The Dunning-Kruger effect describes the tendency for people with limited knowledge in a domain to overestimate their own competence, while experts tend to underestimate theirs.</p>
<h3>The four stages of competence</h3>
<ol>
  <li><strong>Unconscious incompetence</strong>: You don't know what you don't know (peak confidence)</li>
  <li><strong>Conscious incompetence</strong>: You realize how much you don't know (confidence drop)</li>
  <li><strong>Conscious competence</strong>: You can do it, but it requires effort</li>
  <li><strong>Unconscious competence</strong>: Mastery — it's automatic</li>
</ol>
<h3>Why experts underestimate themselves</h3>
<p>Experts assume others find the same things easy. They underweight their own knowledge because they can no longer recall what it felt like not to know it — called the <em>curse of knowledge</em>.</p>
<h3>Using this for growth</h3>
<p>The "confidence valley" at stage 2 is where most people quit. Recognizing you've entered the valley means you're actually progressing. Embrace feeling incompetent — it means you're learning.</p>`,
  },
  {
    id: 6,
    category: 'Decision-Making',
    categoryId: 'decision',
    title: 'The Sunk Cost Trap',
    excerpt: 'Why throwing good money (or time, or energy) after bad is so psychologically compelling — and how to escape it.',
    readTime: 4,
    level: 'Beginner',
    icon: AlertTriangle,
    iconBg: '#fff7ed',
    iconColor: '#ea580c',
    featured: false,
    biasSlug: 'sunk-cost-fallacy',
    body: `<p>The sunk cost fallacy is the tendency to continue an endeavor because of past investments — time, money, effort — even when the rational choice is to cut losses.</p>
<h3>Why we fall for it</h3>
<p>Losses loom larger than equivalent gains (loss aversion). Walking away from a sunk cost feels like confirming a loss, while continuing preserves the <em>hope</em> of recovering it. Our identity becomes intertwined with our investments.</p>
<h3>Classic examples</h3>
<ul>
  <li>Finishing a bad book because you've already read 200 pages</li>
  <li>Staying in a wrong career because of years already invested</li>
  <li>Holding a losing stock waiting to "break even"</li>
  <li>Continuing a failing project because of the budget already spent</li>
</ul>
<h3>The mental shift</h3>
<p>Ask: "If I were starting from scratch today, would I choose this?" If no, the sunk costs aren't a reason to continue. Reframe walking away as freeing resources for better uses, not as admitting failure.</p>`,
  },
  {
    id: 7,
    category: 'Practice',
    categoryId: 'practice',
    title: 'A Daily Debiasing Practice',
    excerpt: 'A 5-minute daily routine that builds lasting cognitive flexibility through structured reflection.',
    readTime: 7,
    level: 'Advanced',
    icon: Target,
    iconBg: '#f0fdf4',
    iconColor: '#15803d',
    featured: false,
    biasSlug: null,
    body: `<p>Awareness alone doesn't eliminate bias — it requires deliberate, repeated practice. Here's a 5-minute daily routine used in evidence-based debiasing research.</p>
<h3>The STOP-SLOW-GO framework</h3>
<p><strong>STOP (30 sec)</strong>: When making any significant decision, pause. Name the decision explicitly: "I am deciding X."</p>
<p><strong>SLOW (2 min)</strong>: Ask three questions:
<ul>
  <li>What biases might be affecting my thinking right now?</li>
  <li>What would I advise a friend in this exact situation?</li>
  <li>What evidence contradicts my current view?</li>
</ul>
</p>
<p><strong>GO (30 sec)</strong>: Proceed with the decision, noting which bias risk was highest.</p>
<h3>Evening reflection (2 min)</h3>
<p>Before bed, recall one decision you made today. Which of the three SLOW questions was hardest to answer? That's likely your dominant bias pattern. Write it down — this is your journal entry for the day.</p>
<h3>30-day outcomes</h3>
<p>Research by Morewedge et al. shows that just 30-45 minutes of debiasing training reduces bias by 29-33%, with effects lasting months. Daily micro-practice compounds this significantly.</p>`,
  },
  {
    id: 8,
    category: 'Self-Awareness',
    categoryId: 'self',
    title: 'Building Your Cognitive Profile',
    excerpt: 'How to use Sentio\'s tools together to build an accurate picture of your unique thinking patterns over time.',
    readTime: 5,
    level: 'Intermediate',
    icon: Zap,
    iconBg: '#fef9c3',
    iconColor: '#ca8a04',
    featured: false,
    biasSlug: null,
    body: `<p>Self-knowledge about your cognitive patterns is built progressively — no single assessment or journal entry tells the full story. Here's how to use Sentio's three pillars together.</p>
<h3>1. Journal entries — the raw signal</h3>
<p>Each journal entry captures your thinking in context. The AI analyzes patterns across entries, not single data points. Aim for 3-5 entries per week for meaningful signal.</p>
<h3>2. Assessments — validated benchmarks</h3>
<p>Assessments measure specific biases in controlled scenarios. They complement journal analysis by catching patterns your writing might not reveal. Complete all available assessments before drawing conclusions.</p>
<h3>3. Bias Explorer — building vocabulary</h3>
<p>Naming a bias you experience is the first step to managing it. Browse the Explorer regularly — when a bias "clicks" as something you recognize in yourself, that recognition is valuable data.</p>
<h3>Your archetype evolves</h3>
<p>Your cognitive archetype isn't fixed. As you practice debiasing, your dominant patterns shift. Revisit assessments quarterly to track genuine change versus noise.</p>`,
  },
]

const featured = computed(() => articles.find(a => a.featured))

const filteredArticles = computed(() => {
  const base = articles.filter(a => !a.featured)
  if (activeCategory.value === 'all') return base
  return base.filter(a => a.categoryId === activeCategory.value)
})

const exercises = [
  {
    id: 'ex1',
    num: '01',
    title: 'The Pre-Mortem',
    desc: 'Before a decision, imagine it failed spectacularly. Work backward to find why.',
    duration: '5 min',
    steps: [
      'Think of a decision you are about to make or are considering.',
      'Imagine it is 6 months from now, and this decision turned out to be a complete failure.',
      'Write down every reason you can think of for why it failed — be specific.',
      'Review your list: which risks are real and addressable? Adjust your decision accordingly.',
      'Notice which failure modes you avoided thinking about originally — those are your blind spots.',
    ],
  },
  {
    id: 'ex2',
    num: '02',
    title: 'The Outside View',
    desc: 'Replace personal intuitions with base rates from similar past situations.',
    duration: '5 min',
    steps: [
      'Identify a prediction you are making (timeline, outcome, probability).',
      'Name a reference class: what type of situation is this? (e.g. "launching a new habit", "starting a job", "first date with X")',
      'What is the base rate for this type of situation? How often does it succeed? Look it up if possible.',
      'Compare your gut estimate to the base rate. How far apart are they?',
      'Adjust your prediction toward the base rate. Write down the adjusted prediction and your reasoning.',
    ],
  },
  {
    id: 'ex3',
    num: '03',
    title: 'Belief Audit',
    desc: 'Surface a belief you hold strongly and stress-test the evidence behind it.',
    duration: '7 min',
    steps: [
      'Write down one belief you hold strongly about yourself, someone else, or the world.',
      'Rate your confidence: 0-100%. Write it down before proceeding.',
      'List every piece of evidence FOR this belief.',
      'Now actively search for evidence AGAINST. This is the hard part — force yourself to find at least 3 counterpoints.',
      'Re-rate your confidence. If it didn\'t change at all, ask yourself why the counter-evidence was dismissed.',
    ],
  },
  {
    id: 'ex4',
    num: '04',
    title: 'The Steel Man',
    desc: 'Construct the strongest possible version of a position you disagree with.',
    duration: '10 min',
    steps: [
      'Choose a view, person, or position you currently disagree with.',
      'Write down the version of this view you typically argue against (the "straw man").',
      'Now write the strongest, most reasonable, most charitable version of this view you can — as if you were its best advocate.',
      'Ask: does the person who holds this view actually believe what you wrote in step 2, or closer to step 3?',
      'What does the steel man version change about how you engage with this view?',
    ],
  },
]

function openArticle(article) {
  activeArticle.value = article
}

function closeArticle() {
  activeArticle.value = null
}

function startExercise(ex) {
  activeExercise.value = ex
}

function closeExercise() {
  activeExercise.value = null
}
</script>

<style scoped>
.learn-page { padding: 32px; max-width: 1000px; }

.page-header { margin-bottom: 24px; }
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0 0 6px; }
.page-sub { font-size: 15px; color: var(--text-muted); margin: 0; }

/* Filters */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
.filter-pill {
  padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 500;
  border: 1.5px solid var(--lavender-soft); background: white; color: var(--text-muted);
  cursor: pointer; transition: all 0.15s;
}
.filter-pill:hover { border-color: var(--lavender); color: var(--plum); }
.filter-pill.active { background: var(--plum); color: white; border-color: var(--plum); }

/* Featured */
.featured-card {
  background: linear-gradient(135deg, var(--plum) 0%, #5b4b6b 100%);
  border-radius: 16px; padding: 32px; margin-bottom: 32px; cursor: pointer;
  transition: transform 0.15s; position: relative; overflow: hidden;
}
.featured-card:hover { transform: translateY(-2px); }
.featured-badge {
  display: inline-block; background: rgba(255,255,255,0.2); color: white;
  font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;
  padding: 3px 10px; border-radius: 20px; margin-bottom: 12px;
}
.featured-category { font-size: 12px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 8px; }
.featured-title { font-size: 24px; font-weight: 800; color: white; margin: 0 0 10px; }
.featured-excerpt { font-size: 15px; color: rgba(255,255,255,0.8); line-height: 1.6; margin: 0 0 16px; max-width: 600px; }
.featured-meta { display: flex; gap: 8px; }

/* Meta tags */
.meta-tag {
  font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
  background: rgba(255,255,255,0.15); color: rgba(255,255,255,0.85);
}
.article-meta .meta-tag { background: var(--bg); color: var(--text-muted); }
.article-meta .meta-tag.level.beginner { background: #dcfce7; color: #16a34a; }
.article-meta .meta-tag.level.intermediate { background: #fef3c7; color: #d97706; }
.article-meta .meta-tag.level.advanced { background: #fce7f3; color: #be185d; }

/* Grid */
.articles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 48px; }

.article-card {
  background: white; border-radius: 14px; padding: 20px;
  border: 1.5px solid var(--lavender-soft); cursor: pointer;
  transition: all 0.15s; display: flex; gap: 14px;
}
.article-card:hover { border-color: var(--lavender); box-shadow: 0 4px 16px rgba(53,43,56,0.07); transform: translateY(-1px); }

.article-icon {
  width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.article-body { flex: 1; min-width: 0; }
.article-category { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.article-title { font-size: 15px; font-weight: 700; color: var(--plum); margin: 0 0 6px; line-height: 1.3; }
.article-excerpt { font-size: 13px; color: var(--text-muted); line-height: 1.5; margin: 0 0 10px; }
.article-meta { display: flex; gap: 6px; }

/* Exercises */
.section-header { margin-bottom: 20px; }
.section-title { font-size: 22px; font-weight: 800; color: var(--plum); margin: 0 0 4px; }
.section-sub { font-size: 14px; color: var(--text-muted); margin: 0; }

.exercises-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 40px; }
.exercise-card {
  background: white; border-radius: 14px; padding: 20px 24px;
  border: 1.5px solid var(--lavender-soft); display: flex; gap: 20px; align-items: flex-start;
}
.exercise-num { font-size: 28px; font-weight: 900; color: var(--lavender-soft); min-width: 40px; }
.exercise-content { flex: 1; }
.exercise-title { font-size: 16px; font-weight: 700; color: var(--plum); margin: 0 0 4px; }
.exercise-desc { font-size: 14px; color: var(--text-muted); margin: 0 0 12px; line-height: 1.5; }
.exercise-actions { display: flex; align-items: center; gap: 12px; }
.ex-time { font-size: 12px; color: var(--text-muted); }
.btn-sm {
  padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 600;
  background: var(--plum); color: white; border: none; cursor: pointer; transition: opacity 0.15s;
}
.btn-sm:hover { opacity: 0.85; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(53,43,56,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 24px;
}
.modal-panel {
  background: white; border-radius: 20px; max-width: 620px; width: 100%;
  max-height: 80vh; overflow-y: auto; padding: 32px; position: relative;
}
.modal-close {
  position: absolute; top: 16px; right: 16px;
  background: var(--bg); border: none; border-radius: 8px;
  width: 32px; height: 32px; cursor: pointer; font-size: 14px; color: var(--text-muted);
}
.modal-category { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.modal-title { font-size: 24px; font-weight: 800; color: var(--plum); margin: 0 0 12px; }
.modal-meta { display: flex; gap: 8px; margin-bottom: 24px; }
.modal-meta .meta-tag { background: var(--bg); color: var(--text-muted); }
.modal-body { font-size: 15px; color: var(--text-body); line-height: 1.7; }
.modal-body h3 { font-size: 17px; font-weight: 700; color: var(--plum); margin: 20px 0 8px; }
.modal-body p { margin: 0 0 12px; }
.modal-body ul, .modal-body ol { padding-left: 20px; margin: 0 0 12px; }
.modal-body li { margin-bottom: 6px; }
.modal-footer { display: flex; gap: 10px; margin-top: 28px; padding-top: 20px; border-top: 1px solid var(--lavender-soft); }
.btn-outline {
  padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600;
  border: 1.5px solid var(--lavender-soft); background: white; color: var(--plum); cursor: pointer;
}
.btn-primary {
  padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600;
  background: var(--plum); color: white; text-decoration: none; border: none; cursor: pointer;
}

/* Exercise steps */
.exercise-steps { display: flex; flex-direction: column; gap: 12px; margin-top: 16px; }
.exercise-step { display: flex; gap: 14px; align-items: flex-start; }
.step-num {
  width: 28px; height: 28px; border-radius: 50%; background: var(--lavender-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: var(--plum); flex-shrink: 0;
}
.step-text { font-size: 15px; color: var(--text-body); line-height: 1.6; margin: 0; padding-top: 4px; }
</style>
