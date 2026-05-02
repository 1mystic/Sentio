<template>
  <div class="notfound-page">

    <!-- Background orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <!-- Top left logo -->
    <div class="logo-top">
      <router-link to="/" class="logo-link">
        <div class="logo-mark">S</div>
        <span class="logo-text">sentio</span>
      </router-link>
    </div>

    <!-- Center Content -->
    <div class="notfound-center">
      <div class="four-oh-four">404</div>
      <h1 class="notfound-title">Oops! Page not found</h1>
      <p class="notfound-desc">The page you're looking for seems to have wandered off into cognitive bias territory.</p>
      <div class="notfound-actions">
        <button class="btn btn-ghost" @click="router.back()">← Go Back</button>
        <router-link to="/dashboard" class="btn btn-primary">Go to Dashboard</router-link>
      </div>
      <p class="notfound-hint">Lost? Try navigating to <router-link to="/explore" class="hint-link">Explore Biases</router-link> or <router-link to="/journal" class="hint-link">Your Journal</router-link>.</p>
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

* { font-family: 'Urbanist', sans-serif; box-sizing: border-box; }

.notfound-page {
  min-height: 100vh;
  background: var(--bg, #edeaf4);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 32px;
}

/* Orbs */
.orb { position: absolute; border-radius: 50%; filter: blur(60px); pointer-events: none; }
.orb-1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(155,148,232,0.18), transparent); top: -100px; right: -100px; }
.orb-2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(184,180,240,0.14), transparent); bottom: -80px; left: -80px; }
.orb-3 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(53,43,56,0.05), transparent); top: 50%; left: 50%; transform: translate(-50%, -50%); }

/* Logo */
.logo-top { position: absolute; top: 32px; left: 32px; z-index: 10; }
.logo-link { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.logo-mark { width: 36px; height: 36px; border-radius: 10px; background: var(--plum, #352b38); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: white; }
.logo-text { font-size: 18px; font-weight: 700; color: var(--plum, #352b38); }

/* Center */
.notfound-center { display: flex; flex-direction: column; align-items: center; gap: 20px; text-align: center; max-width: 520px; position: relative; z-index: 5; }

/* 404 text */
.four-oh-four {
  font-size: 120px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #352b38, #9b94e8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  letter-spacing: -4px;
  user-select: none;
}

.notfound-title { font-size: 24px; font-weight: 700; color: var(--plum, #352b38); margin: 0; }
.notfound-desc { font-size: 15px; color: var(--slate, #7e808c); line-height: 1.6; margin: 0; }

/* Actions */
.notfound-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; justify-content: center; margin-top: 4px; }

.btn { display: inline-flex; align-items: center; gap: 6px; font-family: 'Urbanist'; font-weight: 600; border: none; cursor: pointer; transition: all 0.18s; outline: none; text-decoration: none; }
.btn-primary { background: var(--plum, #352b38); color: white; padding: 12px 24px; border-radius: 10px; font-size: 15px; }
.btn-primary:hover { background: #4a3550; transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--plum, #352b38); border: 1.5px solid var(--lavender, #dad8f9); padding: 12px 24px; border-radius: 10px; font-size: 15px; }
.btn-ghost:hover { background: var(--lavender-soft, #eceaf9); }

.notfound-hint { font-size: 13px; color: var(--slate, #7e808c); margin: 0; }
.hint-link { color: var(--lavender-deep, #9b94e8); font-weight: 600; text-decoration: none; }
.hint-link:hover { text-decoration: underline; }
</style>
