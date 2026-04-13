const DEFAULT_DURATION = 4000
const TOAST_TYPES = ['success', 'error', 'info', 'warning']

let toastId = 0
const listeners = new Set()

const normalizeType = (type) => {
  return TOAST_TYPES.includes(type) ? type : 'info'
}

const normalizeToast = (message, type = 'info', duration = DEFAULT_DURATION) => {
  const trimmedMessage = typeof message === 'string' ? message.trim() : String(message ?? '').trim()

  if (!trimmedMessage) {
    return null
  }

  toastId += 1

  return {
    id: toastId,
    message: trimmedMessage,
    type: normalizeType(type),
    duration: Number.isFinite(duration) ? Math.max(duration, 0) : DEFAULT_DURATION
  }
}

const notifyListeners = (event) => {
  listeners.forEach((listener) => listener(event))
}

const show = (message, type = 'info', duration = DEFAULT_DURATION) => {
  const toast = normalizeToast(message, type, duration)

  if (!toast) {
    return null
  }

  notifyListeners({
    type: 'add',
    toast
  })

  return toast.id
}

const clear = () => {
  notifyListeners({
    type: 'clear'
  })
}

export const toast = {
  show,
  access(message, duration = DEFAULT_DURATION) {
    return show(message, 'success', duration)
  },
  success(message, duration = DEFAULT_DURATION) {
    return show(message, 'success', duration)
  },
  error(message, duration = DEFAULT_DURATION) {
    return show(message, 'error', duration)
  },
  info(message, duration = DEFAULT_DURATION) {
    return show(message, 'info', duration)
  },
  warning(message, duration = DEFAULT_DURATION) {
    return show(message, 'warning', duration)
  },
  clear
}

export function useToast() {
  return toast
}

export function createToastStore() {
  return toast
}

export function subscribeToToasts(listener) {
  listeners.add(listener)

  return () => {
    listeners.delete(listener)
  }
}

export const ToastPlugin = {
  install(app) {
    app.config.globalProperties.$toast = toast
  }
}
