<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div" class="toasts-list">
      <ToastNotification
        v-for="toast in toasts"
        :key="`toast-${toast.id}`"
        :message="toast.message"
        :type="toast.type"
        :duration="4000"
        
        @close="emit('remove', toast.id)"
      />
    </transition-group>
  </div>
</template>

<script setup>
import ToastNotification from './ToastNotification.vue'

const props = defineProps({
  toasts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['remove'])
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
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

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { transform: translateX(100%); opacity: 0; }
.toast-leave-to { transform: translateX(100%); opacity: 0; }
.toast-move { transition: transform 0.3s ease; }
</style> 

