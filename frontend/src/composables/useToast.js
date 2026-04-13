import { ref, inject } from 'vue'

// Ключ для provide/inject
export const ToastKey = Symbol('Toast')

// Composable для использования в компонентах
export function useToast() {
  const toast = inject(ToastKey, null)
  
  if (!toast) {
    console.log('useToast must be used within a component that has provided the Toast context')
  } 
  
  return toast || {
    show: () => console.warn('Toast context not available'),
    success: () => console.warn('Toast context not available'),
    error: () => console.warn('Toast context not available'),
    warning: () => console.warn('Toast context not available'),
    info: () => console.warn('Toast context not available')
  }
}

// Функция для создания toast storage
export function createToastStore() {
  const toasts = ref([])

  const show = (message, type = 'info', duration = 3000) => {
    const id = Date.now() + Math.random()
    const toast = { id, message, type, duration }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  const remove = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (message, duration = 3000) => show(message, 'success', duration)
  const error = (message, duration = 3000) => show(message, 'error', duration)
  const warning = (message, duration = 3000) => show(message, 'warning', duration)
  const info = (message, duration = 3000) => show(message, 'info', duration)

  return {
    toasts,
    show,
    remove,
    success,
    error,
    warning,
    info
  }
}
