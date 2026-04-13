<template>
  <div class="toast-item" :class="`toast-${type}`" role="status">
    <div class="toast-content" :style="{ '--toast-duration': progressDuration }">
      <span class="toast-icon">{{ getIcon() }}</span>
      <span class="toast-message">{{ message }}</span>
      <button @click="close" class="toast-close">✕</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
  },
  duration: { type: Number, default: 4000 }
})

const emit = defineEmits(['close'])
const progressDuration = computed(() => `${Math.max(props.duration, 0)}ms`)

const getIcon = () => {
  switch (props.type) {
    case 'success': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return 'ℹ️'
  }
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.toast-item {
  width: min(360px, 100%);
  max-width: 100%;
  pointer-events: auto;
}

.toast-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
  font-size: 14px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.toast-content::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 3px;
  width: 100%;
  background: var(--toast-accent, #3b82f6);
  transform-origin: left center;
  animation: toast-progress var(--toast-duration, 4000ms) linear forwards;
}

@keyframes toast-progress {
  from {
    transform: scaleX(1);
  }

  to {
    transform: scaleX(0);
  }
}

.toast-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  color: #1f2937;
  line-height: 1.4;
  word-break: break-word;
}

.toast-close {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
}

.toast-close:hover {
  color: #1f2937;
}

.toast-info {
  --toast-accent: #3b82f6;
}

.toast-success {
  --toast-accent: #10b981;
}

.toast-warning {
  --toast-accent: #f59e0b;
}

.toast-error {
  --toast-accent: #ef4444;
}

.toast-info .toast-content,
.toast-success .toast-content,
.toast-warning .toast-content,
.toast-error .toast-content {
  border-left: 4px solid var(--toast-accent);
}
</style>
