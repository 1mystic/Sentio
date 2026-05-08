<template>
  <div>
    <!-- Navbar -->
    <nav class="navbar" :style="{ background: scrolled ? 'rgba(244,243,248,0.92)' : 'rgba(244,243,248,0.6)' }">
      <router-link class="nav-logo" to="/">
        <div class="nav-logo-mark">S</div>
        <span class="nav-logo-text">Sentio</span>
      </router-link>
      <div class="nav-links">
        <a v-for="link in navLinks" :key="link.href" class="nav-link" :href="link.href">{{ link.label }}</a>
      </div>
      <div class="nav-spacer" />
      <div class="nav-ctas">
        <router-link class="btn btn-ghost-nav" to="/login">Log in</router-link>
        <router-link class="btn btn-primary btn-pill" to="/signup">Start free <ChevronRight :size="14" /></router-link>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg" />
      <div class="orb orb-1 float" />
      <div class="orb orb-2 float-2" />
      <div class="orb orb-3" />
      <!-- Mandala decoration -->
      <svg class="mandala-bg" viewBox="0 0 200 200" fill="none">
        <circle v-for="r in [20,35,50,65,80,95]" :key="r" cx="100" cy="100" :r="r" stroke="#352b38" stroke-width="0.5" fill="none" />
        <line
          v-for="i in 12" :key="'line-'+i"
          x1="100" y1="100"
          :x2="100 + 95 * Math.cos((i/12)*Math.PI*2)"
          :y2="100 + 95 * Math.sin((i/12)*Math.PI*2)"
          stroke="#352b38" stroke-width="0.5"
        />
        <circle
          v-for="(dot, idx) in mandalaDots" :key="'dot-'+idx"
          :cx="dot.cx" :cy="dot.cy" r="1.5" fill="#9b94e8" opacity="0.8"
        />
      </svg>

      <div class="hero-inner">
        <div class="hero-pill fade-up">
          <div class="hero-pill-dot" />
          Trusted by 50,000+ practitioners worldwide
        </div>
        <h1 class="hero-title fade-up-d1">
          Know your mind,<br /><span class="accent">break free from bias</span>
        </h1>
        <p class="hero-sub fade-up-d2">
          Sentio is a science-backed cognitive bias self-awareness platform that helps you recognize hidden biases, build reflective thinking habits, and make clearer decisions through personalized AI guidance.
        </p>
        <div class="hero-ctas fade-up-d3">
          <router-link class="btn btn-hero btn-pill" to="/signup">Begin your journey <ChevronRight :size="17" /></router-link>
          <a class="btn btn-hero-outline btn-pill" href="#how-it-works">See how it works</a>
        </div>
        <div class="hero-social-proof fade-up-d4">
          <div class="avatar-stack">
            <div
              v-for="(init, i) in ['AM','JW','EL','MT','SK']"
              :key="i"
              class="avatar-stack-item"
              :style="{ background: `linear-gradient(135deg, ${avatarColors[i]}, #9b94e8)` }"
            >{{ init }}</div>
          </div>
          <div class="social-proof-text">
            <strong>4.9★</strong> from 12,400+ reviews
          </div>
        </div>
      </div>

      <!-- Dashboard Preview -->
      <div class="dashboard-preview" data-animate="scale-up" :style="{ '--stagger': '400ms' }">
        <div class="preview-frame">
          <div class="preview-topbar">
            <div class="preview-dot" style="background:#fca5a5" />
            <div class="preview-dot" style="background:#fcd34d" />
            <div class="preview-dot" style="background:#6ee7b7" />
            <div class="preview-url"><span class="url-lock"></span> app.sentio.so/dashboard</div>
          </div>
          <div class="preview-body">
            <!-- Mini sidebar -->
            <div class="preview-sidebar">
              <div class="preview-logo-mark">S</div>
              <div v-for="(icon, i) in ['⌂','▦','◎','▤','▭']" :key="i" class="preview-nav-icon" :class="{ active: i === 0 }">{{ icon }}</div>
            </div>
            <!-- Main -->
            <div class="preview-main">
              <div class="preview-header-bar">
                <div>
                  <div class="preview-greeting">Good morning, Alex</div>
                  <div class="preview-sub">You have 3 biases to review today</div>
                </div>
                <div class="preview-search">⌕ Search…</div>
              </div>
              <!-- Stats + side panel -->
              <div class="preview-cards">
                <div v-for="(stat, i) in previewStats" :key="i" class="preview-stat" :class="stat.color">
                  <div class="preview-stat-label">{{ stat.label }}</div>
                  <div class="preview-stat-val">{{ stat.val }}</div>
                  <div class="preview-stat-change">{{ stat.change }} vs last week</div>
                  <div class="mini-bars">
                    <div
                      v-for="(h, bi) in stat.bars" :key="bi"
                      class="mini-bar"
                      :style="{ height: h+'%', background: i===2 ? 'linear-gradient(180deg,#9b94e8,#dad8f9)' : 'rgba(155,148,232,0.4)', borderRadius: '2px 2px 0 0' }"
                    />
                  </div>
                </div>
                <!-- Side panels -->
                <div class="preview-side">
                  <div class="preview-insight">
                    <div class="preview-insight-title">Bias Categories</div>
                    <div v-for="(item, i) in previewInsights" :key="i" class="preview-pl-item">
                      <div class="preview-pl-icon" :style="{ background: item.bg, color: item.c }">{{ item.a }}</div>
                      <div style="flex:1">
                        <div style="display:flex;justify-content:space-between">
                          <span class="preview-pl-name">{{ item.name }}</span>
                          <span class="preview-pl-pct">{{ item.pct }}%</span>
                        </div>
                        <div class="preview-pl-bar">
                          <div class="preview-pl-fill" :style="{ width: item.pct+'%', background: `linear-gradient(90deg, ${item.c}, ${item.c}88)` }" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="preview-users">
                    <div class="preview-users-title">Recent Activity</div>
                    <div v-for="(u, i) in previewUsers" :key="i" class="prev-user">
                      <div class="prev-avatar">{{ u.init }}</div>
                      <div class="prev-info">
                        <div class="prev-name">{{ u.name }}</div>
                        <div class="prev-email">{{ u.sub }}</div>
                      </div>
                      <span class="prev-badge">{{ u.badge }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Pipeline -->
              <div class="preview-pipeline">
                <div class="preview-pipeline-title">Bias Awareness Pipeline</div>
                <div style="overflow-x:auto">
                  <div class="pipeline-grid">
                    <div v-for="h in pipelineHeaders" :key="h" class="pipeline-header">{{ h }}</div>
                    <template v-for="(row, ri) in pipelineRows" :key="ri">
                      <div class="p-label">{{ row.label }}</div>
                      <div
                        v-for="(v, vi) in row.vals" :key="vi"
                        class="p-cell"
                        :style="{ background: v !== '' ? row.colors[vi % row.colors.length] : 'transparent' }"
                      >{{ v }}</div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="section" id="features">
      <div class="section-label" data-animate="fade-up">✦ Features</div>
      <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:20px">
        <h2 class="section-title" data-animate="fade-up" :style="{ '--stagger': '80ms' }">Everything you need to<br/>understand your mind</h2>
        <p class="section-sub" data-animate="fade-up" :style="{ '--stagger': '160ms' }">Built on peer-reviewed research in cognitive psychology, behavioral economics, and decision science.</p>
      </div>
      <div class="features-grid">
        <div v-for="(f, i) in features" :key="i" class="feature-card" data-animate="fade-up" :style="{ '--stagger': i * 80 + 'ms' }">
          <div class="feature-icon" :style="{ background: f.bg }">{{ f.icon }}</div>
          <div class="feature-name">{{ f.name }}</div>
          <div class="feature-desc">{{ f.desc }}</div>
        </div>
      </div>
      <div class="stats-row" data-animate="fade-up" :style="{ '--stagger': '200ms' }">
        <div v-for="(s, i) in stats" :key="i" class="stat-block">
          <div class="stat-num">{{ s.num }}</div>
          <div class="stat-lbl">{{ s.lbl }}</div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <div class="how-bg" id="how-it-works">
      <div class="section" style="max-width:1200px">
        <div style="text-align:center">
          <div class="section-label" data-animate="fade-up">◎ Process</div>
          <h2 class="section-title" data-animate="fade-up" :style="{ '--stagger': '80ms' }">Simple. Consistent. Transformative.</h2>
        </div>
        <div class="how-steps">
          <div v-for="(s, i) in howSteps" :key="i" class="how-step" data-animate="fade-up" :style="{ '--stagger': i * 90 + 'ms' }">
            <div class="how-step-num">{{ s.num }}</div>
            <div class="how-step-title">{{ s.title }}</div>
            <div class="how-step-desc">{{ s.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile section -->
    <div class="mobile-section" id="mobile">
      <div class="mobile-section-inner">
        <div class="mobile-text">
          <div class="section-label" data-animate="fade-right">◈ Mobile App</div>
          <h2 class="section-title" data-animate="fade-right" :style="{ '--stagger': '80ms' }">Bias awareness in your pocket</h2>
          <p class="section-sub" data-animate="fade-right" :style="{ '--stagger': '160ms' }">Full-featured iOS and Android apps that sync seamlessly with the web platform. Reflect on the go.</p>
          <div class="mobile-bullets">
            <div v-for="(b, i) in mobileBullets" :key="i" class="mobile-bullet" data-animate="fade-right" :style="{ '--stagger': 240 + i * 100 + 'ms' }">
              <div class="mobile-bullet-icon" :style="{ background: b.bg }">{{ b.icon }}</div>
              <div>
                <div class="mobile-bullet-title">{{ b.title }}</div>
                <div class="mobile-bullet-desc">{{ b.desc }}</div>
              </div>
            </div>
          </div>
          <div style="display:flex;gap:12px;margin-top:36px" data-animate="fade-right" :style="{ '--stagger': '540ms' }">
            <button class="btn btn-primary" style="border-radius:12px;padding:12px 24px;font-size:15px">App Store</button>
            <button class="btn btn-ghost-nav" style="border-radius:12px;padding:12px 24px;font-size:15px">Google Play</button>
          </div>
        </div>
        <!-- Phone frames -->
        <div class="mobile-phones" data-animate="fade-left" :style="{ '--stagger': '200ms' }">
          <div class="phone-frame float">
            <div class="phone-topbar">
              <span class="phone-time">9:41</span>
              <span class="phone-status">▪▪▪ ◈ ▮</span>
            </div>
            <div class="phone-notch-bar" />
            <div class="phone-screen">
              <div class="phone-splash-inner">
                <div class="phone-logo-ring">
                  <svg viewBox="0 0 40 40" width="40" height="40" fill="none">
                    <path d="M20 5 C20 5 10 12 10 20 C10 28 15 33 20 35 C25 33 30 28 30 20 C30 12 20 5 20 5Z" stroke="#9b94e8" stroke-width="1.5" fill="none"/>
                    <path d="M20 10 C20 10 13 15 13 21 C13 27 17 31 20 32 C23 31 27 27 27 21 C27 15 20 10 20 10Z" stroke="#9b94e8" stroke-width="1" fill="rgba(155,148,232,0.1)"/>
                  </svg>
                </div>
                <div class="phone-brand">SENTIO</div>
                <div class="phone-welcome">Welcome back, Alex</div>
                <div class="phone-tagline">Your cognitive bias companion for clearer thinking.</div>
                <div class="phone-cta-btn">Start Session</div>
                <div style="font-size:10px;color:var(--slate)">Already have an account?</div>
              </div>
            </div>
          </div>
          <div class="phone-frame float-2" style="margin-top:80px;margin-left:-24px">
            <div class="phone-topbar">
              <span class="phone-time">9:41</span>
              <span class="phone-status">▪▪▪ ◈ ▮</span>
            </div>
            <div class="phone-notch-bar" />
            <div class="phone-screen-white">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <div class="phone-screen-title">Today's Biases</div>
                <div style="width:24px;height:24px;border-radius:99px;background:var(--lavender-deep);display:flex;align-items:center;justify-content:center;font-size:12px;color:white">+</div>
              </div>
              <div style="font-size:9px;font-weight:700;color:var(--slate);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px">Upcoming</div>
              <div class="phone-card">
                <div class="phone-card-title">Confirmation Bias</div>
                <div class="phone-card-sub">Assessment · 5 min</div>
                <div class="phone-timer">Starting in 1h 24m</div>
              </div>
              <div style="font-size:9px;font-weight:700;color:var(--slate);margin:10px 0 6px;text-transform:uppercase;letter-spacing:0.5px">Quick Actions</div>
              <div class="phone-block-row">
                <div v-for="([icon,lbl]) in [['▤','Journal'],['◎','Explore'],['▦','Quiz']]" :key="lbl" class="phone-block-btn">
                  <div class="phone-block-icon">{{ icon }}</div>
                  <div class="phone-block-lbl">{{ lbl }}</div>
                </div>
              </div>
              <div style="background:var(--plum);color:white;border-radius:12px;margin:10px 0 8px;padding:9px;text-align:center;font-size:11px;font-weight:700">Begin Reflection</div>
              <div class="phone-bottom-nav">
                <div v-for="([icon,lbl], i) in [['⌂','Home'],['▦','Explore'],['◎','Profile']]" :key="i" class="phone-nav-item" :class="{ active: i===1 }">
                  <div :style="{ background: i===1?'rgba(155,148,232,0.25)':undefined, borderRadius: '8px', padding: '2px 4px' }">{{ icon }}</div>
                  <div style="font-size:7px">{{ lbl }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Testimonials -->
    <div style="background:var(--bg)" id="stories">
      <div class="section">
        <div class="section-label" data-animate="fade-up">♡ Stories</div>
        <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:20px">
          <h2 class="section-title" data-animate="fade-up" :style="{ '--stagger': '80ms' }">Real minds, real results</h2>
          <p class="section-sub" data-animate="fade-up" :style="{ '--stagger': '160ms' }">From students to executives — Sentio meets you where you are.</p>
        </div>
        <div class="testimonials-grid">
          <div v-for="(t, i) in testimonials" :key="i" class="testimonial-card" data-animate="fade-up" :style="{ '--stagger': i * 80 + 'ms' }">
            <div class="testimonial-stars">
              <span v-for="s in 5" :key="s" class="testimonial-star">★</span>
            </div>
            <div class="testimonial-text">"{{ t.text }}"</div>
            <div class="testimonial-author">
              <div class="testimonial-avatar" :style="{ background: `linear-gradient(135deg, ${testimonialColors[i]}, #9b94e8)` }">{{ t.init }}</div>
              <div>
                <div class="testimonial-name">{{ t.name }}</div>
                <div class="testimonial-role">{{ t.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pricing -->
    <div style="background:white" id="pricing">
      <div class="section">
        <div style="text-align:center">
          <div class="section-label" data-animate="fade-up">◈ Pricing</div>
          <h2 class="section-title" data-animate="fade-up" :style="{ '--stagger': '80ms' }">Invest in your mind</h2>
          <p class="section-sub" data-animate="fade-up" :style="{ '--stagger': '160ms', margin: '0 auto 28px' }">Start free. Upgrade when you're ready. Cancel anytime.</p>
          <div class="billing-toggle">
            <button
              class="toggle-btn"
              :class="{ active: !annual }"
              @click="annual = false"
            >Monthly</button>
            <button
              class="toggle-btn"
              :class="{ active: annual }"
              @click="annual = true"
            >Annual <span class="save-badge">-25%</span></button>
          </div>
        </div>
        <div class="pricing-grid">
          <div
            v-for="(plan, i) in pricingPlans"
            :key="i"
            class="pricing-card"
            :class="{ featured: plan.featured }"
            data-animate="fade-up"
            :style="{ marginTop: plan.featured ? '-12px' : '0', '--stagger': i * 90 + 'ms' }"
          >
            <div v-if="plan.featured" class="pricing-badge">Most Popular</div>
            <div class="pricing-label" :class="{ 'featured-lbl': plan.featured }">{{ plan.name }}</div>
            <div class="pricing-price">
              <template v-if="plan.price === 0">Free</template>
              <template v-else><sup>$</sup>{{ annual ? plan.annualPrice : plan.monthlyPrice }}</template>
            </div>
            <div class="pricing-period">{{ plan.price === 0 ? 'forever' : annual ? '/mo billed annually' : '/month' }}</div>
            <div class="pricing-features">
              <div v-for="(f, fi) in plan.features" :key="fi" class="pricing-feature">
                <div class="pricing-feature-icon" :style="{ background: plan.featured ? 'rgba(218,216,249,0.15)' : 'var(--lavender-soft)' }">✓</div>
                {{ f }}
              </div>
            </div>
            <router-link
              v-if="plan.featured"
              to="/signup"
              class="btn-pricing-outline"
            >{{ plan.cta }}</router-link>
            <router-link
              v-else-if="plan.price === 0"
              to="/signup"
              class="btn-pricing-dark"
            >{{ plan.cta }}</router-link>
            <a
              v-else
              href="mailto:hello@sentio.so"
              class="btn-pricing-ghost"
            >{{ plan.cta }}</a>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div style="padding:0 48px 80px">
      <div class="cta-section">
        <div class="cta-orb cta-orb-1" />
        <div class="cta-orb cta-orb-2" />
        <div style="position:relative;z-index:2">
          <div class="cta-pill-label" data-animate="scale-up">✦ START YOUR FREE JOURNEY</div>
          <div class="cta-title" data-animate="fade-up" :style="{ '--stagger': '100ms' }">Your clearer mind<br/>starts today</div>
          <div class="cta-sub" data-animate="fade-up" :style="{ '--stagger': '200ms' }">No credit card required. 14-day free trial. Cancel anytime.</div>
          <div class="cta-ctas" data-animate="fade-up" :style="{ '--stagger': '300ms' }">
            <router-link to="/signup" class="btn-cta-white">Begin for free <ChevronRight :size="16" /></router-link>
            <a href="mailto:hello@sentio.so" class="btn-cta-outline">Talk to us</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="footer-logo">
            <div class="footer-logo-mark">S</div>
            <span class="footer-logo-text">Sentio</span>
          </div>
          <div class="footer-tagline">Science-backed cognitive bias awareness for a clearer, sharper, more self-aware mind.</div>
        </div>
        <div v-for="col in footerCols" :key="col.title">
          <div class="footer-col-title">{{ col.title }}</div>
          <a v-for="link in col.links" :key="link" class="footer-link" href="#">{{ link }}</a>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="footer-copy">© 2026 Sentio, Inc. All rights reserved.</div>
        <div class="footer-socials">
          <a v-for="s in ['𝕏','in','ig','yt']" :key="s" class="footer-social" href="#">{{ s }}</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChevronRight } from 'lucide-vue-next'

const scrolled = ref(false)
const annual = ref(true)

function handleScroll() {
  scrolled.value = window.scrollY > 20
}

let animObserver = null

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  animObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible')
          animObserver.unobserve(e.target)
        }
      })
    },
    { threshold: 0.1, rootMargin: '0px 0px -48px 0px' }
  )

  document.querySelectorAll('[data-animate]').forEach((el) => animObserver.observe(el))
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  animObserver?.disconnect()
})

const navLinks = [
  { href: '#features', label: 'Features' },
  { href: '#how-it-works', label: 'How it works' },
  { href: '#mobile', label: 'Mobile' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#stories', label: 'Stories' },
]

const avatarColors = ['#dad8f9','#d8f9e8','#f9d8f0','#d8edf9','#fef9c3']

// Mandala dots data
const mandalaDots = (() => {
  const dots = []
  for (const r of [30, 55, 75]) {
    for (let j = 0; j < 8; j++) {
      const a = (j / 8) * Math.PI * 2
      dots.push({ cx: 100 + r * Math.cos(a), cy: 100 + r * Math.sin(a) })
    }
  }
  return dots
})()

const previewStats = [
  { label: 'Biases Identified', val: '+42', change: '↑ 24%', color: 'lavender', bars: [30,50,35,60,45,70,55,80,60,75] },
  { label: 'Reflection Score', val: '8.4', change: '↑ 14%', color: 'pink', bars: [45,55,50,65,60,55,70,75,65,80] },
  { label: 'Journal Entries', val: '2.4k', change: '↑ 30%', color: 'blue', bars: [25,40,50,35,55,65,50,75,60,85] },
]

const previewInsights = [
  { name: 'Cognitive', pct: 60, bg: '#ede9fe', c: '#9b94e8', a: 'C' },
  { name: 'Social', pct: 20, bg: '#d1fae5', c: '#6ee7b7', a: 'S' },
  { name: 'Memory', pct: 10, bg: '#fee2e2', c: '#fca5a5', a: 'M' },
  { name: 'Decision', pct: 7, bg: '#fef9c3', c: '#fcd34d', a: 'D' },
]

const previewUsers = [
  { init: 'AM', name: 'Alexandra M.', sub: 'Completed 3 assessments', badge: 'Active' },
  { init: 'JW', name: 'John W.', sub: 'New journal entry', badge: 'New' },
]

const pipelineHeaders = ['','Discovered','Assessed','Reflected','Improved','Mastered']
const pipelineRows = [
  { label: 'Confirmation', vals: [30,24,20,12,8], colors: ['#dbeafe','#eff6ff','#dbeafe','#bfdbfe','#e0f2fe'] },
  { label: 'Anchoring', vals: [27,20,17,'',''], colors: ['#d8f9e8','#d1fae5','#d8f9e8'] },
  { label: 'Availability', vals: [46,30,26,15,''], colors: ['#f9d8f0','#fce7f3','#f9d8f0','#fbcfe8'] },
  { label: 'Dunning-K.', vals: [23,12,8,6,8], colors: ['#d8edf9','#dbeafe','#bfdbfe','#d8edf9','#bfdbfe'] },
]

const features = [
  { icon: '◎', bg: '#ede9fe', name: 'Bias Explorer', desc: 'Explore 180+ documented cognitive biases with real-world examples, research context, and personal relevance scoring.' },
  { icon: '✏', bg: '#fef9c3', name: 'Reflective Journal', desc: 'AI-guided journaling prompts that help you spot bias patterns in your own thinking and decisions.' },
  { icon: '▦', bg: '#d1fae5', name: 'Bias Assessments', desc: 'Validated psychometric assessments that reveal your personal bias profile across cognitive, social, and decision categories.' },
  { icon: '✦', bg: '#ede9fe', name: 'AI Guide', desc: 'Your personal bias coach, available 24/7. Gets smarter about your patterns and suggests targeted exercises.' },
  { icon: '↑', bg: '#dbeafe', name: 'Progress Tracking', desc: 'Track your self-awareness growth over time. Visualize which biases you have identified, worked on, and reduced.' },
  { icon: '♡', bg: '#fee2e2', name: 'Therapist Directory', desc: 'Connect with certified cognitive behavioral therapists who can help you work through deeply rooted bias patterns.' },
]

const stats = [
  { num: '180+', lbl: 'Documented cognitive biases' },
  { num: '94%', lbl: 'Report better decisions in 4 weeks' },
  { num: '2.4M', lbl: 'Reflections completed' },
  { num: '4.9★', lbl: 'Average app rating' },
]

const howSteps = [
  { num: '01', title: 'Create your profile', desc: 'Tell us about your decision-making patterns and thinking habits. Takes 3 minutes.' },
  { num: '02', title: 'Discover your biases', desc: 'Take a baseline assessment to reveal your personal bias profile across key cognitive categories.' },
  { num: '03', title: 'Reflect daily', desc: 'Use guided journaling and targeted exercises to spot bias in real situations. As short as 5 minutes.' },
  { num: '04', title: 'Track & grow', desc: 'Watch your self-awareness scores improve. Celebrate when biases lose their grip on your thinking.' },
]

const mobileBullets = [
  { icon: '◷', bg: '#ede9fe', title: 'Daily reflection prompts', desc: 'Bite-sized prompts that surface bias patterns in your everyday choices and social interactions.' },
  { icon: '◎', bg: '#d1fae5', title: 'Offline bias library', desc: 'Browse the full cognitive bias library anywhere, even without internet connection.' },
  { icon: '↑', bg: '#dbeafe', title: 'Progress streaks', desc: 'Build consistent reflection habits with streak tracking and milestone celebrations.' },
]

const testimonials = [
  { name: 'Alexandra M.', role: 'Product Designer', init: 'AM', text: "Sentio completely changed how I approach design decisions. I stopped rationalizing my early assumptions and started genuinely testing them. The bias journal is eye-opening." },
  { name: 'James Park', role: 'Software Engineer', init: 'JP', text: "I was skeptical at first but the assessments revealed patterns I never would have noticed on my own. The AI Guide is uncannily accurate at catching when I'm anchoring." },
  { name: 'Dr. Sara Klein', role: 'Clinical Psychologist', init: 'SK', text: "I recommend Sentio to clients as a between-session self-reflection tool. The CBT-informed journaling prompts align well with evidence-based practice." },
  { name: 'Marcus Tang', role: 'Entrepreneur', init: 'MT', text: "Built two companies making bias-driven decisions. Sentio helped me see my sunk-cost and overconfidence patterns before they cost me a third time." },
  { name: 'Emily Lee', role: 'Teacher', init: 'EL', text: "I use Sentio with my high school students to teach critical thinking. Seeing their own biases surfaced by the assessments creates genuine aha moments." },
  { name: 'Priya Nair', role: 'Graduate Student', init: 'PN', text: "As a researcher, I thought I was immune to bias. Sentio humbled me fast. Now I use it before every analysis to check my assumptions." },
]
const testimonialColors = ['#dad8f9','#d8f9e8','#f9d8f0','#d8edf9','#fef9c3','#ede9fe']

const pricingPlans = [
  {
    name: 'Free', price: 0, annualPrice: 0, monthlyPrice: 0,
    features: ['5 bias assessments/month', 'Basic journal (20 entries)', 'Community access', '30 biases from explorer'],
    cta: 'Get started free',
  },
  {
    name: 'Pro', price: 1, annualPrice: 12, monthlyPrice: 16, featured: true,
    features: ['Unlimited assessments', 'AI Guide (Sentio AI)', 'Full bias library (180+)', 'Unlimited journal', 'Progress analytics', 'Mobile app full access'],
    cta: 'Start 14-day free trial',
  },
  {
    name: 'Team', price: 2, annualPrice: 8, monthlyPrice: 10,
    features: ['Everything in Pro', 'Team bias dashboard', 'Group reflection sessions', 'Admin controls', 'SAML SSO', 'Dedicated CSM'],
    cta: 'Contact sales',
  },
]

const footerCols = [
  { title: 'Product', links: ['Features','Pricing','Mobile App','Integrations','Changelog'] },
  { title: 'Company', links: ['About','Blog','Careers','Press','Contact'] },
  { title: 'Legal', links: ['Privacy Policy','Terms of Use','Cookie Policy','GDPR','Security'] },
]
</script>

<style scoped>
/* Navbar */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; padding: 0 48px;
  height: 68px;
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(218,216,249,0.4);
  transition: background 0.3s;
}
.nav-logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.nav-logo-mark {
  width: 38px; height: 38px; border-radius: 11px;
  background: linear-gradient(135deg, #dad8f9 0%, #9b94e8 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 19px; font-weight: 900; color: var(--plum); letter-spacing: -1px;
}
.nav-logo-text { font-size: 20px; font-weight: 800; color: var(--plum); letter-spacing: -0.5px; }
.nav-links { display: flex; align-items: center; gap: 6px; margin-left: 40px; }
.nav-link {
  padding: 7px 14px; border-radius: 8px; font-size: 14px; font-weight: 500;
  color: var(--slate); text-decoration: none; transition: all 0.15s;
}
.nav-link:hover { color: var(--plum); background: var(--lavender-soft); }
.nav-spacer { flex: 1; }
.nav-ctas { display: flex; align-items: center; gap: 10px; }
.btn-ghost-nav { padding: 8px 18px; border-radius: 10px; font-size: 14px; background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); font-family: 'Urbanist', sans-serif; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.15s; }
.btn-ghost-nav:hover { background: var(--lavender-soft); }

/* Hero */
.hero {
  min-height: 100vh; padding-top: 68px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0; z-index: 0;
  background: linear-gradient(160deg, #f4f3f8 0%, #edeaf4 35%, #e4e1f5 65%, #dbd6f5 100%);
}
.orb { position: absolute; border-radius: 50%; background: radial-gradient(circle, rgba(155,148,232,0.22), rgba(218,216,249,0.08)); pointer-events: none; }
.orb-1 { width: 600px; height: 600px; top: -150px; right: -100px; }
.orb-2 { width: 400px; height: 400px; bottom: -80px; left: -80px; background: radial-gradient(circle, rgba(218,216,249,0.3), transparent); }
.orb-3 { width: 200px; height: 200px; top: 40%; left: 20%; }
.mandala-bg { position: absolute; opacity: 0.06; z-index: 0; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 700px; height: 700px; }

.hero-inner {
  position: relative; z-index: 2;
  display: flex; flex-direction: column; align-items: center;
  text-align: center; padding: 52px 24px 0; max-width: 860px;
}
.hero-pill {
  display: inline-flex; align-items: center; gap: 8px;
  background: white; border: 1.5px solid var(--lavender); border-radius: 99px;
  padding: 7px 16px; font-size: 13px; font-weight: 600; color: var(--lavender-deep);
  margin-bottom: 28px; box-shadow: 0 2px 12px rgba(155,148,232,0.12);
}
.hero-pill-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--lavender-deep); }
.hero-title {
  font-size: clamp(44px,7vw,80px); font-weight: 900; line-height: 1.05;
  letter-spacing: -2.5px; color: var(--plum); margin-bottom: 20px; text-wrap: balance;
}
.hero-title .accent {
  background: linear-gradient(135deg, #9b94e8 0%, #b8b4f0 50%, #352b38 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-size: 18px; font-weight: 400; color: var(--slate); line-height: 1.65; max-width: 580px; margin-bottom: 36px; text-wrap: pretty; }
.hero-ctas { display: flex; gap: 12px; align-items: center; margin-bottom: 48px; flex-wrap: wrap; justify-content: center; }
.btn-hero { padding: 15px 36px; border-radius: 14px; font-size: 17px; font-weight: 700; background: var(--plum); color: white; font-family: 'Urbanist', sans-serif; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s; }
.btn-hero:hover { background: #4a3550; box-shadow: 0 8px 32px rgba(53,43,56,0.28); transform: translateY(-2px); }
.btn-hero-outline { padding: 15px 36px; border-radius: 14px; font-size: 17px; font-weight: 700; background: transparent; color: var(--plum); border: 2px solid var(--lavender-mid); font-family: 'Urbanist', sans-serif; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s; }
.btn-hero-outline:hover { background: var(--lavender-soft); border-color: var(--lavender-deep); }
.btn-pill { border-radius: 99px !important; }

.hero-social-proof { display: flex; align-items: center; gap: 14px; }
.avatar-stack { display: flex; }
.avatar-stack-item { width: 32px; height: 32px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: var(--plum); margin-left: -8px; }
.avatar-stack-item:first-child { margin-left: 0; }
.social-proof-text { font-size: 13px; color: var(--slate); }
.social-proof-text strong { color: var(--plum); }

/* Dashboard preview */
.dashboard-preview { position: relative; z-index: 2; width: 100%; max-width: 1080px; margin: 0 auto; padding: 0 24px 80px; }
.preview-frame { background: white; border-radius: 24px; box-shadow: 0 32px 80px rgba(53,43,56,0.16), 0 2px 8px rgba(53,43,56,0.06); overflow: hidden; border: 1px solid rgba(218,216,249,0.5); }
.preview-topbar { display: flex; align-items: center; gap: 6px; padding: 14px 20px; background: var(--ghost); border-bottom: 1px solid var(--lavender-soft); }
.preview-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.preview-url {
  flex: 1; height: 26px; background: white; border-radius: 6px; margin: 0 12px;
  display: flex; align-items: center; gap: 5px; padding: 0 10px;
  font-size: 11px; color: var(--slate); border: 1px solid var(--lavender-soft);
  overflow: hidden; white-space: nowrap;
}
.url-lock {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background: #6ee7b7; flex-shrink: 0;
}
.preview-body { display: flex; height: 480px; }
.preview-sidebar { width: 52px; flex-shrink: 0; background: var(--ghost); border-right: 1px solid var(--lavender-soft); display: flex; flex-direction: column; align-items: center; padding: 16px 0; gap: 10px; }
.preview-logo-mark { width: 30px; height: 30px; border-radius: 9px; background: linear-gradient(135deg, #dad8f9, #9b94e8); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px; color: #352b38; margin-bottom: 8px; }
.preview-nav-icon { width: 30px; height: 30px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; transition: background 0.15s; }
.preview-nav-icon.active { background: var(--lavender); }
.preview-main { flex: 1; padding: 16px; overflow: hidden; background: var(--ghost); min-width: 0; }
.preview-header-bar { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; gap: 8px; }
.preview-greeting { font-size: 15px; font-weight: 800; }
.preview-sub { font-size: 10px; color: var(--slate); }
.preview-search { display: flex; align-items: center; gap: 6px; background: white; border: 1px solid var(--lavender); border-radius: 8px; padding: 5px 10px; font-size: 10px; color: var(--slate); width: 140px; flex-shrink: 0; }

/* Stats grid + side panel */
.preview-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr)) 186px;
  gap: 8px;
  margin-bottom: 8px;
  align-items: start;
}
.preview-stat { background: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(53,43,56,0.06); min-width: 0; }
.preview-stat.lavender { background: linear-gradient(135deg, #dad8f9, #eceaf9); }
.preview-stat.pink { background: linear-gradient(135deg, #f9d8f0, #fde8f9); }
.preview-stat.blue { background: linear-gradient(135deg, #d8edf9, #e8f4fd); }
.preview-stat-label { font-size: 8px; font-weight: 600; color: var(--slate); text-transform: uppercase; letter-spacing: 0.4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.preview-stat-val { font-size: 20px; font-weight: 800; margin: 3px 0 2px; }
.preview-stat-change { font-size: 8px; font-weight: 700; color: #059669; }
.mini-bars { display: flex; align-items: flex-end; gap: 2px; height: 32px; margin-top: 5px; }
.mini-bar { flex: 1; min-width: 0; }

/* Side panel */
.preview-side { display: flex; flex-direction: column; gap: 8px; grid-row: 1; min-width: 0; }
.preview-insight { background: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(53,43,56,0.06); }
.preview-insight-title { font-size: 10px; font-weight: 700; margin-bottom: 7px; }
.preview-pl-item { display: flex; align-items: center; gap: 5px; margin-bottom: 5px; }
.preview-pl-icon { width: 16px; height: 16px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: 800; flex-shrink: 0; }
.preview-pl-name { font-size: 9px; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.preview-pl-pct { font-size: 9px; font-weight: 700; color: var(--slate); flex-shrink: 0; }
.preview-pl-bar { height: 3px; background: var(--lavender-soft); border-radius: 99px; margin-top: 2px; overflow: hidden; }
.preview-pl-fill { height: 100%; border-radius: 99px; }
.preview-users { background: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(53,43,56,0.06); }
.preview-users-title { font-size: 10px; font-weight: 700; margin-bottom: 7px; }
.prev-user { display: flex; align-items: center; gap: 5px; margin-bottom: 7px; }
.prev-user:last-child { margin-bottom: 0; }
.prev-avatar { width: 22px; height: 22px; flex-shrink: 0; border-radius: 7px; background: linear-gradient(135deg, var(--lavender), var(--lavender-deep)); display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: 700; }
.prev-info { flex: 1; min-width: 0; }
.prev-name { font-size: 9px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prev-email { font-size: 8px; color: var(--slate); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prev-badge { font-size: 7px; background: var(--lavender); border-radius: 99px; padding: 2px 5px; font-weight: 700; flex-shrink: 0; white-space: nowrap; }

/* Pipeline */
.preview-pipeline { background: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(53,43,56,0.06); }
.preview-pipeline-title { font-size: 10px; font-weight: 700; margin-bottom: 7px; }
.pipeline-grid { display: grid; grid-template-columns: 72px repeat(5, minmax(0, 1fr)); gap: 3px; }
.pipeline-header { font-size: 7px; font-weight: 700; color: var(--slate); text-transform: uppercase; padding: 2px 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.p-label { font-size: 8px; color: var(--slate); display: flex; align-items: center; padding-left: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.p-cell { border-radius: 4px; padding: 3px 2px; font-size: 9px; font-weight: 700; text-align: center; min-width: 0; overflow: hidden; }

/* Sections */
.section { padding: 96px 48px; max-width: 1200px; margin: 0 auto; }
.section-title { font-size: clamp(30px,4vw,48px); font-weight: 800; letter-spacing: -1.5px; line-height: 1.1; color: var(--plum); margin-bottom: 16px; text-wrap: balance; }
.section-sub { font-size: 17px; color: var(--slate); line-height: 1.65; max-width: 540px; text-wrap: pretty; }

/* Features */
.features-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; margin-top: 52px; }
.feature-card { background: white; border-radius: 20px; padding: 28px; box-shadow: 0 4px 24px rgba(53,43,56,0.06); border: 1px solid rgba(218,216,249,0.4); transition: all 0.2s; }
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(53,43,56,0.12); }
.feature-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px; }
.feature-name { font-size: 17px; font-weight: 700; margin-bottom: 8px; }
.feature-desc { font-size: 14px; color: var(--slate); line-height: 1.6; }

/* Stats row */
.stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 2px; background: var(--lavender-soft); border-radius: 20px; overflow: hidden; margin-top: 52px; }
.stat-block { background: white; padding: 36px 28px; text-align: center; }
.stat-num { font-size: 48px; font-weight: 900; letter-spacing: -2px; background: linear-gradient(135deg, var(--plum), var(--lavender-deep)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-lbl { font-size: 14px; color: var(--slate); margin-top: 4px; }

/* How it works */
.how-bg { background: white; }
.how-steps { display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; margin-top: 52px; position: relative; }
.how-steps::before { content: ''; position: absolute; top: 28px; left: 10%; right: 10%; height: 2px; background: linear-gradient(90deg, var(--lavender-soft), var(--lavender), var(--lavender-soft)); z-index: 0; }
.how-step { position: relative; z-index: 1; text-align: center; padding: 0 12px; }
.how-step-num { width: 56px; height: 56px; border-radius: 16px; background: var(--lavender); display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900; color: var(--plum); margin: 0 auto 16px; box-shadow: 0 4px 16px rgba(155,148,232,0.2); }
.how-step-title { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
.how-step-desc { font-size: 13px; color: var(--slate); line-height: 1.6; }

/* Mobile section */
.mobile-section { padding: 96px 48px; background: linear-gradient(160deg, #edeaf4, #e4e0f5); }
.mobile-section-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; gap: 60px; }
.mobile-text { flex: 1; }
.mobile-phones { flex: 1; display: flex; justify-content: center; align-items: flex-start; }
.phone-frame { width: 200px; background: white; border-radius: 32px; overflow: hidden; box-shadow: 0 20px 60px rgba(53,43,56,0.16); border: 1px solid rgba(218,216,249,0.5); flex-shrink: 0; }
.phone-topbar { background: white; padding: 10px 14px 0; display: flex; justify-content: space-between; align-items: center; }
.phone-time { font-size: 11px; font-weight: 700; }
.phone-status { font-size: 9px; color: var(--slate); }
.phone-notch-bar { width: 50px; height: 6px; background: #352b38; border-radius: 99px; margin: 0 auto -3px; position: relative; z-index: 1; }
.phone-screen { padding: 12px; min-height: 300px; background: linear-gradient(160deg, #fdeef8, #ede9fd, #e8d9fb); }
.phone-screen-white { padding: 12px; min-height: 300px; background: white; }
.phone-splash-inner { display: flex; flex-direction: column; align-items: center; padding-top: 24px; padding-bottom: 16px; }
.phone-logo-ring { width: 60px; height: 60px; border-radius: 50%; border: 2px solid rgba(155,148,232,0.5); display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.phone-brand { font-size: 13px; font-weight: 800; color: var(--plum); letter-spacing: -0.5px; margin-bottom: 4px; }
.phone-welcome { font-size: 16px; font-weight: 800; margin-bottom: 6px; text-align: center; line-height: 1.2; }
.phone-tagline { font-size: 10px; color: var(--slate); text-align: center; line-height: 1.5; max-width: 140px; margin-bottom: 20px; }
.phone-cta-btn { background: var(--plum); color: white; border-radius: 99px; padding: 10px 32px; font-size: 12px; font-weight: 700; margin-bottom: 10px; width: 80%; text-align: center; }
.phone-screen-title { font-size: 16px; font-weight: 800; margin-bottom: 10px; }
.phone-card { background: rgba(218,216,249,0.4); border-radius: 12px; padding: 10px; margin-bottom: 8px; }
.phone-card-title { font-size: 11px; font-weight: 700; }
.phone-card-sub { font-size: 9px; color: var(--slate); margin-top: 2px; }
.phone-timer { font-size: 9px; color: var(--lavender-deep); margin-top: 4px; display: flex; align-items: center; gap: 3px; }
.phone-block-row { display: flex; gap: 8px; margin: 8px 0; }
.phone-block-btn { flex: 1; background: white; border-radius: 10px; padding: 8px; text-align: center; box-shadow: 0 2px 8px rgba(53,43,56,0.06); }
.phone-block-icon { font-size: 14px; margin-bottom: 3px; }
.phone-block-lbl { font-size: 8px; color: var(--slate); }
.phone-bottom-nav { display: flex; background: var(--plum); border-radius: 14px; margin: 8px; overflow: hidden; }
.phone-nav-item { flex: 1; padding: 8px; text-align: center; font-size: 8px; color: rgba(255,255,255,0.5); }
.phone-nav-item.active { color: white; }

/* Mobile bullets */
.mobile-bullets { display: flex; flex-direction: column; gap: 20px; margin-top: 32px; }
.mobile-bullet { display: flex; gap: 14px; align-items: flex-start; }
.mobile-bullet-icon { width: 44px; height: 44px; border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.mobile-bullet-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.mobile-bullet-desc { font-size: 13px; color: var(--slate); line-height: 1.5; }

/* Testimonials */
.testimonials-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; margin-top: 52px; }
.testimonial-card { background: white; border-radius: 20px; padding: 28px; box-shadow: 0 4px 24px rgba(53,43,56,0.06); border: 1px solid rgba(218,216,249,0.4); }
.testimonial-stars { display: flex; gap: 3px; margin-bottom: 14px; }
.testimonial-star { color: #fbbf24; font-size: 16px; }
.testimonial-text { font-size: 14px; color: var(--slate); line-height: 1.7; margin-bottom: 18px; font-style: italic; }
.testimonial-author { display: flex; align-items: center; gap: 10px; }
.testimonial-avatar { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; }
.testimonial-name { font-size: 14px; font-weight: 700; }
.testimonial-role { font-size: 12px; color: var(--slate); }

/* Pricing */
.billing-toggle { display: inline-flex; align-items: center; gap: 0; background: var(--lavender-soft); border-radius: 99px; padding: 4px 6px; margin-bottom: 0; }
.toggle-btn { padding: 8px 18px; border-radius: 99px; border: none; cursor: pointer; font-family: 'Urbanist', sans-serif; font-weight: 600; font-size: 14px; background: transparent; color: var(--plum); box-shadow: none; transition: all 0.15s; }
.toggle-btn.active { background: white; box-shadow: 0 2px 8px rgba(53,43,56,0.08); }
.save-badge { font-size: 11px; background: #d1fae5; color: #059669; padding: 1px 6px; border-radius: 99px; margin-left: 4px; }
.pricing-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; margin-top: 52px; }
.pricing-card { background: white; border-radius: 24px; padding: 32px; box-shadow: 0 4px 24px rgba(53,43,56,0.06); border: 2px solid transparent; position: relative; transition: all 0.2s; }
.pricing-card.featured { background: var(--plum); }
.pricing-card.featured * { color: white !important; }
.pricing-card.featured .pricing-feature-icon { background: rgba(255,255,255,0.1) !important; }
.pricing-label { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--slate); margin-bottom: 12px; }
.featured-lbl { color: var(--lavender-mid) !important; }
.pricing-price { font-size: 52px; font-weight: 900; letter-spacing: -2px; line-height: 1; }
.pricing-price sup { font-size: 22px; font-weight: 700; vertical-align: top; margin-top: 8px; display: inline-block; letter-spacing: 0; }
.pricing-period { font-size: 13px; color: var(--slate); margin-top: 4px; margin-bottom: 24px; }
.pricing-features { display: flex; flex-direction: column; gap: 10px; margin-bottom: 28px; }
.pricing-feature { display: flex; align-items: center; gap: 10px; font-size: 14px; }
.pricing-feature-icon { width: 20px; height: 20px; border-radius: 6px; background: var(--lavender-soft); display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; }
.pricing-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: linear-gradient(90deg, var(--lavender-deep), var(--lavender-mid)); color: white; font-size: 11px; font-weight: 700; padding: 4px 14px; border-radius: 99px; white-space: nowrap; }
.btn-pricing-dark { display: block; width: 100%; padding: 13px; border-radius: 12px; font-size: 15px; font-weight: 700; background: var(--plum); color: white; border: none; cursor: pointer; transition: all 0.2s; font-family: 'Urbanist', sans-serif; text-align: center; text-decoration: none; }
.btn-pricing-dark:hover { background: #4a3550; transform: translateY(-1px); }
.btn-pricing-outline { display: block; width: 100%; padding: 13px; border-radius: 12px; font-size: 15px; font-weight: 700; background: transparent; color: white; border: 2px solid rgba(255,255,255,0.3); cursor: pointer; transition: all 0.2s; font-family: 'Urbanist', sans-serif; text-align: center; text-decoration: none; }
.btn-pricing-outline:hover { background: rgba(255,255,255,0.1); }
.btn-pricing-ghost { display: block; width: 100%; padding: 13px; border-radius: 12px; font-size: 15px; font-weight: 700; background: transparent; color: var(--plum); border: 2px solid var(--lavender-mid); cursor: pointer; transition: all 0.2s; font-family: 'Urbanist', sans-serif; text-align: center; text-decoration: none; }
.btn-pricing-ghost:hover { background: var(--lavender-soft); }

/* CTA */
.cta-section { background: linear-gradient(135deg, var(--plum) 0%, #4a3550 100%); border-radius: 28px; padding: 72px 48px; text-align: center; position: relative; overflow: hidden; }
.cta-orb { position: absolute; border-radius: 50%; pointer-events: none; background: radial-gradient(circle, rgba(218,216,249,0.12), transparent); }
.cta-orb-1 { width: 400px; height: 400px; top: -150px; right: -80px; }
.cta-orb-2 { width: 300px; height: 300px; bottom: -120px; left: -60px; }
.cta-pill-label { display: inline-flex; align-items: center; gap: 8px; background: rgba(218,216,249,0.1); border: 1px solid rgba(218,216,249,0.2); border-radius: 99px; padding: 6px 16px; font-size: 12px; font-weight: 700; color: rgba(218,216,249,0.7); margin-bottom: 20px; letter-spacing: 0.8px; }
.cta-title { font-size: clamp(32px,4vw,52px); font-weight: 900; color: white; letter-spacing: -2px; margin-bottom: 16px; text-wrap: balance; }
.cta-sub { font-size: 17px; color: rgba(218,216,249,0.7); margin-bottom: 36px; line-height: 1.6; }
.cta-ctas { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.btn-cta-white { padding: 15px 36px; border-radius: 14px; font-size: 16px; font-weight: 700; background: white; color: var(--plum); border: none; cursor: pointer; transition: all 0.2s; font-family: 'Urbanist', sans-serif; text-decoration: none; display: inline-flex; align-items: center; }
.btn-cta-white:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.2); }
.btn-cta-outline { padding: 15px 36px; border-radius: 14px; font-size: 16px; font-weight: 700; background: transparent; color: white; border: 2px solid rgba(255,255,255,0.3); cursor: pointer; transition: all 0.2s; font-family: 'Urbanist', sans-serif; text-decoration: none; display: inline-flex; align-items: center; }
.btn-cta-outline:hover { background: rgba(255,255,255,0.08); }

/* Footer */
.footer { background: var(--plum); padding: 60px 48px 36px; }
.footer-top { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 52px; max-width: 1200px; margin-left: auto; margin-right: auto; }
.footer-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.footer-logo-mark { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, rgba(218,216,249,0.2), rgba(155,148,232,0.3)); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 900; color: white; }
.footer-logo-text { font-size: 20px; font-weight: 800; color: white; }
.footer-tagline { font-size: 14px; color: rgba(218,216,249,0.5); line-height: 1.6; max-width: 240px; }
.footer-col-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: rgba(218,216,249,0.5); margin-bottom: 16px; }
.footer-link { display: block; font-size: 14px; color: rgba(218,216,249,0.7); text-decoration: none; margin-bottom: 10px; transition: color 0.15s; }
.footer-link:hover { color: white; }
.footer-bottom { display: flex; align-items: center; justify-content: space-between; padding-top: 28px; border-top: 1px solid rgba(218,216,249,0.1); max-width: 1200px; margin: 0 auto; }
.footer-copy { font-size: 13px; color: rgba(218,216,249,0.4); }
.footer-socials { display: flex; gap: 10px; }
.footer-social { width: 34px; height: 34px; border-radius: 9px; background: rgba(218,216,249,0.1); display: flex; align-items: center; justify-content: center; font-size: 14px; color: rgba(218,216,249,0.6); cursor: pointer; transition: all 0.15s; text-decoration: none; }
.footer-social:hover { background: rgba(218,216,249,0.18); color: white; }

/* Responsive */
@media (max-width: 1080px) {
  /* Slightly tighten the preview on non-full-width screens */
  .preview-cards { grid-template-columns: repeat(3, minmax(0, 1fr)) 160px; }
}

@media (max-width: 900px) {
  .navbar { padding: 0 24px; }
  .nav-links { display: none; }
  .features-grid, .testimonials-grid, .pricing-grid { grid-template-columns: 1fr; }
  .how-steps { grid-template-columns: repeat(2,1fr); }
  .how-steps::before { display: none; }
  .footer-top { grid-template-columns: 1fr 1fr; }
  .stats-row { grid-template-columns: repeat(2,1fr); }
  .mobile-section-inner { flex-direction: column; }
  .section { padding: 60px 24px; }
  .cta-section { margin: 0 24px 40px; padding: 40px 24px; }

  /* Preview: drop side panel, show 3 stats + pipeline only */
  .preview-cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .preview-side { display: none; }
  .preview-body { height: 360px; }
  .preview-search { display: none; }
}

@media (max-width: 640px) {
  /* Preview: 2-col stats, hide pipeline */
  .preview-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .preview-pipeline { display: none; }
  .preview-body { height: 240px; }
  .preview-sidebar { display: none; }
  .dashboard-preview { padding: 0 16px 60px; }
  .preview-main { padding: 12px; }
  .preview-header-bar { margin-bottom: 8px; }
}

@media (max-width: 440px) {
  /* Just hide the whole preview on very small phones — it's decorative */
  .dashboard-preview { display: none; }
}

/* ── Hero entrance (auto-plays on load) ───────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up    { animation: fadeUp 0.65s ease both; }
.fade-up-d1 { animation: fadeUp 0.65s 0.12s ease both; }
.fade-up-d2 { animation: fadeUp 0.65s 0.24s ease both; }
.fade-up-d3 { animation: fadeUp 0.65s 0.36s ease both; }
.fade-up-d4 { animation: fadeUp 0.65s 0.48s ease both; }

/* ── Scroll-triggered entrance animations ──────────────────────── */
[data-animate] { opacity: 0; }
[data-animate="fade-up"]    { transform: translateY(30px); }
[data-animate="fade-left"]  { transform: translateX(-30px); }
[data-animate="fade-right"] { transform: translateX(30px); }
[data-animate="scale-up"]   { transform: scale(0.93); }

[data-animate].is-visible {
  opacity: 1;
  transform: none;
  transition:
    opacity  0.65s ease var(--stagger, 0ms),
    transform 0.65s ease var(--stagger, 0ms);
}

@media (prefers-reduced-motion: reduce) {
  .fade-up, .fade-up-d1, .fade-up-d2, .fade-up-d3, .fade-up-d4 { animation: none; }
  [data-animate] { opacity: 1; transform: none; }
  [data-animate].is-visible { transition: none; }
}
</style>
