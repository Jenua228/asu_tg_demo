<template>
  <div class="toast-container" aria-live="polite" aria-atomic="true">
    <transition-group name="toast" tag="div" class="toasts-list">
      <ToastNotification
        v-for="toast in toasts"
        :key="`toast-${toast.id}`"
        :message="toast.message"
        :type="toast.type"
        :duration="toast.duration"
        @close="removeToast(toast.id)"
      />
    </transition-group>
  </div>
</template>

<script setup>
import { onUnmounted, ref } from 'vue'
import ToastNotification from './ToastNotification.vue'
import { subscribeToToasts } from '../composables/useToast'

const toasts = ref([])
const timeoutMap = new Map()

const removeToast = (id) => {
  const timeoutId = timeoutMap.get(id)

  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutMap.delete(id)
  }

  toasts.value = toasts.value.filter((toast) => toast.id !== id)
}

const addToast = (toast) => {
  toasts.value = [...toasts.value, toast]

  if (toast.duration > 0) {
    const timeoutId = setTimeout(() => {
      removeToast(toast.id)
    }, toast.duration)

    timeoutMap.set(toast.id, timeoutId)
  }
}

const unsubscribe = subscribeToToasts((event) => {
  if (event.type === 'clear') {
    timeoutMap.forEach((timeoutId) => clearTimeout(timeoutId))
    timeoutMap.clear()
    toasts.value = []
    return
  }

  if (event.type === 'add') {
    addToast(event.toast)
  }
})

onUnmounted(() => {
  unsubscribe()
  timeoutMap.forEach((timeoutId) => clearTimeout(timeoutId))
  timeoutMap.clear()
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 5000;
  pointer-events: none;
}

.toasts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: auto;
  align-items: flex-end;
}
/* 
.toasts-list > * {
  pointer-events: auto;
} */

/* Animations for toast group */
/* .toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%) translateY(100%) !important;
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%) translateY(-20px) !important;
  opacity: 0;
}

.toast-move {
  transition: transform 0.3s ease;
} */

.toast-enter-active,
.toast-leave-active {
  transition: all 0.24s ease;
}

.toast-enter-from,
.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.toast-move {
  transition: transform 0.24s ease;
}

@media (max-width: 768px) {
  .toast-container {
    right: 12px;
    left: 12px;
    bottom: 12px;
  }

  .toasts-list {
    align-items: stretch;
  }
}
</style> 

