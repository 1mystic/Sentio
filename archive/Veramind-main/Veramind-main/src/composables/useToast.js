import { ref } from 'vue'

const toasts = ref([])

/**
 * Toast notification composable
 * Provides global toast notifications
 */
export const useToast = () => {
  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now()
    const toast = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration
    }

    toasts.value.push(toast)

    // Auto remove after duration
    setTimeout(() => {
      removeToast(id)
    }, duration)

    return id
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (message, duration) => showToast(message, 'success', duration)
  const error = (message, duration) => showToast(message, 'error', duration)
  const warning = (message, duration) => showToast(message, 'warning', duration)
  const info = (message, duration) => showToast(message, 'info', duration)

  return {
    toasts: readonly(toasts),
    showToast,
    removeToast,
    success,
    error,
    warning,
    info
  }
}

