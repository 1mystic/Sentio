<template>
  <div class="profile-page">

    <!-- Page Title -->
    <div class="page-header">
      <h1 class="page-title">Profile &amp; Settings</h1>
    </div>

    <div class="profile-layout">

      <!-- Left Column -->
      <div class="left-col">

        <!-- Profile Card -->
        <div class="card profile-card">
          <div class="avatar-section">
            <div class="avatar-large">{{ initials }}</div>
            <button class="btn btn-ghost btn-sm">Edit Avatar</button>
          </div>
          <h2 class="profile-name">{{ name }}</h2>
          <div class="profile-email">{{ email }}</div>
          <div class="member-badge">
            <span class="badge badge-lavender">🗓 Member since May 2026</span>
          </div>
          <div class="profile-stats">
            <div class="pstat">
              <span class="pstat-val">12</span>
              <span class="pstat-label">Entries</span>
            </div>
            <div class="pstat">
              <span class="pstat-val">3</span>
              <span class="pstat-label">Assessments</span>
            </div>
            <div class="pstat">
              <span class="pstat-val">🔥 7</span>
              <span class="pstat-label">Day Streak</span>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="card danger-card">
          <div class="danger-title">Danger Zone</div>
          <p class="danger-desc">Permanently delete your account and all associated data. This action cannot be undone.</p>
          <button class="btn btn-danger btn-sm">🗑 Delete Account</button>
        </div>

      </div>

      <!-- Right Column -->
      <div class="right-col">

        <!-- Personal Info -->
        <div class="card settings-card">
          <div class="section-header">
            <span class="section-title">Personal Info</span>
          </div>
          <form @submit.prevent="saveProfile" class="settings-form">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input v-model="name" class="input" placeholder="Your name" />
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input v-model="email" class="input" type="email" placeholder="your@email.com" />
            </div>
            <div class="form-group">
              <label class="form-label">Bio</label>
              <textarea v-model="bio" class="input bio-textarea" placeholder="Tell us a bit about yourself..." rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Save Changes</button>
          </form>
        </div>

        <!-- Notifications -->
        <div class="card settings-card">
          <div class="section-header">
            <span class="section-title">Notifications</span>
          </div>
          <div class="notif-list">
            <div class="notif-item" v-for="n in notifItems" :key="n.key">
              <div class="notif-info">
                <div class="notif-label">{{ n.label }}</div>
                <div class="notif-desc">{{ n.desc }}</div>
              </div>
              <div class="toggle-wrap" @click="toggleNotif(n.key)">
                <div class="toggle" :class="{ on: notifications[n.key] }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Privacy & Data -->
        <div class="card settings-card">
          <div class="section-header">
            <span class="section-title">Privacy &amp; Data</span>
          </div>
          <div class="privacy-options">
            <div class="privacy-row">
              <div class="privacy-info">
                <div class="privacy-label">Export My Data</div>
                <div class="privacy-sub">Download a copy of all your journal entries and assessments</div>
              </div>
              <button class="btn btn-ghost btn-sm">Export</button>
            </div>
            <div class="privacy-row">
              <div class="privacy-info">
                <div class="privacy-label">Journal Visibility</div>
                <div class="privacy-sub">Your journal is private and never shared</div>
              </div>
              <span class="badge badge-green">Private</span>
            </div>
            <div class="privacy-row">
              <div class="privacy-info">
                <div class="privacy-label">AI Data Usage</div>
                <div class="privacy-sub">AI conversations are not stored beyond the session</div>
              </div>
              <span class="badge badge-lavender">Session only</span>
            </div>
          </div>
        </div>

        <!-- Appearance -->
        <div class="card settings-card">
          <div class="section-header">
            <span class="section-title">Appearance</span>
          </div>
          <div class="appearance-placeholder">
            <div class="appearance-icon">🎨</div>
            <div class="appearance-text">
              <div class="appearance-label">Theme Customization</div>
              <div class="appearance-sub">Dark mode and custom themes coming soon</div>
            </div>
            <span class="badge badge-yellow">Soon</span>
          </div>
        </div>

      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastVisible" class="toast">✓ Profile saved!</div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const name = ref(auth.user?.user_metadata?.full_name || 'User')
const email = ref(auth.user?.email || '')
const bio = ref('')
const notifications = ref({ daily: true, weekly: true, assessments: false, ai: true })
const toastVisible = ref(false)

const initials = computed(() => {
  return name.value.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || 'U'
})

const notifItems = [
  { key: 'daily', label: 'Daily Reflection Reminder', desc: 'Get a gentle nudge to write in your journal each day' },
  { key: 'weekly', label: 'Weekly Insights Report', desc: 'A summary of your bias patterns and progress every week' },
  { key: 'assessments', label: 'Assessment Recommendations', desc: 'Suggestions for new assessments based on your profile' },
  { key: 'ai', label: 'AI Guide Suggestions', desc: 'Proactive insights from Sentio AI based on your entries' },
]

function toggleNotif(key) {
  notifications.value[key] = !notifications.value[key]
}

async function saveProfile() {
  toastVisible.value = true
  setTimeout(() => { toastVisible.value = false }, 2000)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.profile-page { display: flex; flex-direction: column; gap: 28px; }
.page-header {}
.page-title { font-size: 28px; font-weight: 800; color: var(--plum); margin: 0; }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; }
.btn-primary { background: var(--plum); color: white; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--plum); border: 1.5px solid var(--lavender); padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-ghost:hover { background: var(--lavender-soft); }
.btn-sm { padding: 6px 14px !important; font-size: 13px !important; border-radius: 8px !important; }
.btn-danger { background: #fee2e2; color: #dc2626; border: none; padding: 10px 20px; border-radius: 10px; font-size: 14px; }
.btn-danger:hover { background: #fecaca; }

.card { background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(53,43,56,0.07); padding: 24px; }
.badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 99px; display: inline-flex; align-items: center; }
.badge-lavender { background: var(--lavender); color: var(--plum); }
.badge-green { background: #d1fae5; color: #059669; }
.badge-yellow { background: #fef9c3; color: #92400e; }
.input { font-family: 'Urbanist'; font-size: 14px; color: var(--plum); background: white; border: 1.5px solid var(--lavender); border-radius: 10px; padding: 10px 14px; outline: none; transition: all 0.15s; width: 100%; }
.input:focus { border-color: var(--lavender-deep); box-shadow: 0 0 0 3px rgba(155,148,232,0.15); }

/* Section Header */
.section-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1.5px solid var(--lavender-soft); margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--plum); }

/* Layout */
.profile-layout { display: grid; grid-template-columns: 280px 1fr; gap: 24px; align-items: start; }
@media (max-width: 900px) { .profile-layout { grid-template-columns: 1fr; } }
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* Profile Card */
.profile-card { display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; }
.avatar-section { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.avatar-large { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #352b38, #9b94e8); display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: white; }
.profile-name { font-size: 22px; font-weight: 700; color: var(--plum); margin: 0; }
.profile-email { font-size: 13px; color: var(--slate); }
.member-badge {}
.profile-stats { display: flex; gap: 20px; padding: 16px 0; border-top: 1px solid var(--lavender-soft); width: 100%; justify-content: center; }
.pstat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.pstat-val { font-size: 20px; font-weight: 800; color: var(--plum); }
.pstat-label { font-size: 11px; color: var(--slate); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }

/* Danger Zone */
.danger-card { border: 1px solid #fee2e2; }
.danger-title { font-size: 14px; font-weight: 700; color: #dc2626; margin-bottom: 8px; }
.danger-desc { font-size: 13px; color: var(--slate); margin: 0 0 14px; line-height: 1.5; }

/* Settings Form */
.settings-card {}
.settings-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--plum); }
.bio-textarea { resize: vertical; min-height: 80px; }

/* Notifications */
.notif-list { display: flex; flex-direction: column; gap: 0; }
.notif-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid var(--lavender-soft); gap: 16px; }
.notif-item:last-child { border-bottom: none; }
.notif-info { flex: 1; }
.notif-label { font-size: 14px; font-weight: 600; color: var(--plum); }
.notif-desc { font-size: 12px; color: var(--slate); margin-top: 2px; }

/* Toggle */
.toggle-wrap { display: flex; align-items: center; gap: 10px; cursor: pointer; flex-shrink: 0; }
.toggle { width: 44px; height: 24px; border-radius: 99px; background: var(--lavender); position: relative; transition: background 0.2s; flex-shrink: 0; }
.toggle.on { background: var(--lavender-deep); }
.toggle::after { content: ''; position: absolute; top: 3px; left: 3px; width: 18px; height: 18px; border-radius: 50%; background: white; transition: transform 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
.toggle.on::after { transform: translateX(20px); }

/* Privacy */
.privacy-options { display: flex; flex-direction: column; gap: 0; }
.privacy-row { display: flex; align-items: center; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid var(--lavender-soft); gap: 16px; }
.privacy-row:last-child { border-bottom: none; }
.privacy-info { flex: 1; }
.privacy-label { font-size: 14px; font-weight: 600; color: var(--plum); }
.privacy-sub { font-size: 12px; color: var(--slate); margin-top: 2px; }

/* Appearance */
.appearance-placeholder { display: flex; align-items: center; gap: 14px; padding: 12px; background: var(--lavender-soft); border-radius: 12px; }
.appearance-icon { font-size: 24px; }
.appearance-text { flex: 1; }
.appearance-label { font-size: 14px; font-weight: 600; color: var(--plum); }
.appearance-sub { font-size: 12px; color: var(--slate); }

/* Toast */
.toast { position: fixed; bottom: 32px; right: 32px; background: var(--plum); color: white; font-weight: 600; font-size: 14px; padding: 12px 24px; border-radius: 12px; box-shadow: 0 8px 32px rgba(53,43,56,0.18); z-index: 1000; }
</style>
