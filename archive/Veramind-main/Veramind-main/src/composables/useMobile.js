import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Mobile detection composable
 * Detects if user is on a mobile device and tracks window size
 */
export const useMobile = () => {
  const isMobile = ref(false)
  const isTablet = ref(false)
  const windowWidth = ref(0)

  const checkDevice = () => {
    if (process.client) {
      windowWidth.value = window.innerWidth
      isMobile.value = windowWidth.value < 768
      isTablet.value = windowWidth.value >= 768 && windowWidth.value < 1024
    }
  }

  onMounted(() => {
    if (process.client) {
      checkDevice()
      window.addEventListener('resize', checkDevice)
    }
  })

  onUnmounted(() => {
    if (process.client) {
      window.removeEventListener('resize', checkDevice)
    }
  })

  return {
    isMobile: readonly(isMobile),
    isTablet: readonly(isTablet),
    windowWidth: readonly(windowWidth)
  }
}

