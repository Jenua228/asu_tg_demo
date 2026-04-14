<template>
  <div class="inventory-alerts-widget">
    <div class="widget-header">
      <h3>{{ $t('inventory.alertsTitle') }}</h3>
      <button 
        @click="handleMarkAllAsRead"
        v-if="unreadCount > 0"
        class="btn-mark-read"
      >
        ✓ {{ $t('inventory.markAllRead') }}
      </button>
    </div>
    
    <!-- Счетчик непрочитанных -->
    <div class="alerts-stats">
      <div class="stat-item">
        <span class="stat-badge unread">{{ unreadCount }}</span>
        <span class="stat-label">{{ $t('inventory.unreadAlerts') }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-badge critical">{{ criticalCount }}</span>
        <span class="stat-label">{{ $t('inventory.criticalAlerts') }}</span>
      </div>
    </div>
    
    <!-- Список оповещений -->
    <div class="alerts-list">
      <template v-if="displayedAlerts.length > 0">
       <div 
        v-for="alert in displayedAlerts"
        :key="alert.id"
        :class="['alert-item', `type-${alert.alertType}`, { unread: !alert.isRead }]"
        @click="markAlertAsRead(alert.id)"
      > 
      
        <div class="alert-icon">
          <span v-if="alert.alertType === 'info'">ℹ️</span>
          <span v-else-if="alert.alertType === 'warning'">⚠️</span>
          <span v-else-if="alert.alertType === 'critical'">🔴</span>
          <span v-else-if="alert.alertType === 'success'">✅</span>
        </div>
        
        <div class="alert-content">
          <div class="alert-message">{{ alert.message }}</div>
          <div class="alert-meta">
            <span class="alert-type-badge">{{ alert.eventType }}</span>
            <span class="alert-time">{{ getTimeFromNow(alert.createdAt) }}</span>
          </div>
        </div>
        
        <button 
          @click.stop="deleteAlert(alert.id)"
          class="btn-delete-alert"
        >
          ✕
        </button>
      </div>
    </template>
      
      <div v-else class="no-alerts">
        <p>{{ $t('inventory.noAlerts') }}</p>
      </div>
    </div>
    
    <!-- Ссылка на полный список -->
    <!-- <div class="widget-footer">
      <router-link to="/inventory-requests" class="link-view-all">
        {{ $t('inventory.viewAllRequests') }} →
      </router-link>
    </div> -->
    <button @click="showAll = !showAll" class="toggle-view-btn">
       {{ showAll ? 'Показать только непрочитанные' : 'Показать все' }}
    </button>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useInventoryAlerts } from '../../composables/useInventoryAlerts'

const { t } = useI18n()
const { 
  alerts, 
  unreadCount, 
  criticalCount, 
  loadAlerts, 
  markAlertAsRead, 
  markAllAsRead, 
  deleteAlert,
  startPolling,
  stopPolling
} = useInventoryAlerts()

const emit = defineEmits(['alerts-updated'])

const showAll = ref(false)

const displayedAlerts = computed(() => {

  let filtered = alerts.value.filter(a => a.message && a.message.trim().length > 0);
  
  if (!showAll.value) {
    filtered = filtered.filter(a => !a.isRead)
  }
  return filtered.sort((a, b) => {
      if (a.isRead === b.isRead) {
        return new Date(b.createdAt) - new Date(a.createdAt)
      }
      return a.isRead ? 1 : -1
    }).slice(0, 5)
  })

const getTimeFromNow = (dateString) => {
  const now = new Date()
  const time = new Date(dateString + 'Z')
  const diff = Math.floor((now - time) / 1000) // в секундах
  
  if (diff < 60) return t('time.justNow')
  if (diff < 3600) return `${Math.floor(diff / 60)}м назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)}ч назад`
  return `${Math.floor(diff / 86400)}д назад`
}

const handleMarkAllAsRead = async () => {
  await markAllAsRead()
  emit('alerts-updated')
}

// onMounted(async () => {
//   await startPolling()
// })

onUnmounted(() => {
  stopPolling()
})

// Экспортируем loadAlerts для вызова из других компонентов
defineExpose({
  loadAlerts
})
</script>

<style scoped>
.inventory-alerts-widget {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.widget-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1f2937;
}

.btn-mark-read {
  padding: 5px 10px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.btn-mark-read:hover {
  background: #059669;
}

.alerts-stats {
  display: flex;
  gap: 15px;
  padding: 12px 15px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
  color: white;
}

.toggle-view-btn{
  padding: 5px 10px;
  margin: auto;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  width: 250px;
}

.stat-badge.unread {
  background: #3b82f6;
}

.stat-badge.critical {
  background: #ef4444;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.alerts-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f9fafb;
  border-left: 4px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.alert-item:hover {
  background: #f3f4f6;
}

.alert-item.unread {
  background: #f0f9ff;
  border-left-color: #3b82f6;
  font-weight: 500;
}

.alert-item.type-info {
  border-left-color: #3b82f6;
}

.alert-item.type-warning {
  border-left-color: #f59e0b;
}

.alert-item.type-critical {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.alert-item.type-success {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.alert-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.alert-message {
  font-size: 13px;
  color: #1f2937;
  word-break: break-word;
  line-height: 1.4;
}

.alert-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.alert-type-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: #e5e7eb;
  color: #4b5563;
  border-radius: 2px;
  text-transform: uppercase;
}

.alert-time {
  font-size: 11px;
  color: #9ca3af;
}

.btn-delete-alert {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}

.btn-delete-alert:hover {
  color: #ef4444;
}

.no-alerts {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #9ca3af;
  text-align: center;
  flex: 1;
}

.no-alerts p {
  margin: 0;
  font-size: 13px;
}

.widget-footer {
  padding: 10px 15px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.link-view-all {
  font-size: 13px;
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.link-view-all:hover {
  text-decoration: underline;
}
</style>
