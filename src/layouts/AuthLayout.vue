<template>
  <div class="auth-shell">
    <div class="auth-bg" />
    <div class="auth-box">
      <div class="auth-logo">
        <div class="auth-logo-mark">S</div>
        <span class="auth-logo-text">Sentio</span>
      </div>
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.auth-shell {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
}
.auth-bg {
  position: absolute; inset: 0;
  background: linear-gradient(160deg, #f4f3f8 0%, #edeaf4 35%, #e4e1f5 65%, #dbd6f5 100%);
}
.auth-box {
  position: relative; z-index: 2;
  background: white; border-radius: 24px; padding: 40px;
  width: 100%; max-width: 420px;
  box-shadow: 0 20px 60px rgba(53,43,56,0.12);
  border: 1px solid rgba(218,216,249,0.5);
}
.auth-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 28px; justify-content: center; }
.auth-logo-mark {
  width: 38px; height: 38px; border-radius: 11px;
  background: linear-gradient(135deg, #dad8f9, #9b94e8);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 900; color: var(--plum);
}
.auth-logo-text { font-size: 22px; font-weight: 800; color: var(--plum); }
</style>
