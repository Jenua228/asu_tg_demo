  <!-- <template>
    <Teleport to="body">
      <div v-if="visible" class="toast-wrapper">
        <div class="toast-container" :class="`toast-${type}`">
          <div class="toast-content">
            <span class="toast-icon">{{ getIcon() }}</span>
            <span class="toast-message">{{ message }}</span>
            <button @click="close" class="toast-close">✕</button>
          </div>
        </div>
      </div>
    </Teleport>
  </template>

  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'

  const props = defineProps({
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info', // info, success, warning, error
      validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000 // milliseconds
    }
  })

  const emit = defineEmits(['close'])

  const visible = ref(true)
  let timeoutId = null

  const getIcon = () => {
    switch (props.type) {
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      case 'info':
      default: return 'ℹ️'
    }
  }

  const close = () => {
    visible.value = false
    emit('close')
    if (timeoutId) clearTimeout(timeoutId)
  }

  onMounted(() => {
    if (props.duration > 0) {
      timeoutId = setTimeout(() => {
        close()
      }, props.duration)
    }
  })

  onUnmounted(() => {
    if (timeoutId) clearTimeout(timeoutId)
  })
  </script>

  <style scoped>
  .toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%) translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0) translateY(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    to {
      transform: translateX(100%) translateY(100%);
      opacity: 0;
    }
  }

  .toast-container:active {
    animation: slideOut 0.3s ease-in forwards;
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 6px;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    font-size: 14px;
    min-width: 250px;
    max-width: 400px;
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

  /* Стили для разных типов */
  .toast-info {
    --accent-color: #3b82f6;
  }

  .toast-info .toast-content {
    border-left: 4px solid var(--accent-color);
  }

  .toast-success {
    --accent-color: #10b981;
  }

  .toast-success .toast-content {
    border-left: 4px solid var(--accent-color);
  }

  .toast-warning {
    --accent-color: #f59e0b;
  }

  .toast-warning .toast-content {
    border-left: 4px solid var(--accent-color);
  }

  .toast-error {
    --accent-color: #ef4444;
  }

  .toast-error .toast-content {
    border-left: 4px solid var(--accent-color);
  }
  </style> -->


  <template>
  <div v-if="visible" class="toast-item" :class="`toast-${type}`">
    <div class="toast-content">
      <span class="toast-icon">{{ getIcon() }}</span>
      <span class="toast-message">{{ message }}</span>
      <button @click="close" class="toast-close">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  type: {
    type: String,
    default: 'info',
    validator: v => ['info','success','warning','error'].includes(v)
  },
  duration: { type: Number, default: 3000 }
})

const emit = defineEmits(['close'])
const visible = ref(true)
let timeoutId = null

const getIcon = () => {
  switch (props.type) {
    case 'success': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return 'ℹ️'
  }
}

const close = () => {
  visible.value = false
  emit('close')
  if (timeoutId) clearTimeout(timeoutId)
}

onMounted(() => {
  if (props.duration > 0) {
    timeoutId = setTimeout(close, props.duration)
  }
})

onUnmounted(() => {
  if (timeoutId) clearTimeout(timeoutId)
})
</script>

<style scoped>
.toast-item {
  animation: slideIn 0.3s ease-out;
  width: 300px;
  max-width: 90vw;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  font-size: 14px;
}

.toast-icon { font-size: 18px; flex-shrink: 0; }
.toast-message { flex: 1; color: #1f2937; line-height: 1.4; }
.toast-close {
  background: none; border: none; color: #6b7280;
  cursor: pointer; font-size: 16px; padding: 0; line-height: 1;
}
.toast-close:hover { color: #1f2937; }

.toast-info .toast-content { border-left: 4px solid #3b82f6; }
.toast-success .toast-content { border-left: 4px solid #10b981; }
.toast-warning .toast-content { border-left: 4px solid #f59e0b; }
.toast-error .toast-content { border-left: 4px solid #ef4444; }
</style>
