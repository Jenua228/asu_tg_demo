import { ref, computed } from 'vue'
import { inventoryAlertApi } from '../api'
import { useToast } from './useToast'

// Глобальное состояние для оповещений
const alertsStore = {
  alerts: ref([]),
  lastAlertIds: new Set(),
  isFirstLoad: true,
  errorCount: 0,
  updateInterval: null
}

export function useInventoryAlerts() {
  const toast = useToast()

  const unreadCount = computed(() => {
    return alertsStore.alerts.value.filter(a => !a.isRead).length
  })

  const criticalCount = computed(() => {
    return alertsStore.alerts.value.filter(a => a.alertType === 'critical').length
  })

  // Функция для загрузки оповещений с показом toast для новых
  const loadAlerts = async (showToast = true) => {
    try {
      const response = await inventoryAlertApi.getAllLimited(10)
      const newAlerts = response.data || []
      
      // При первой загрузке просто запоминаем существующие оповещения, не показываем toast
      if (alertsStore.isFirstLoad) {
        newAlerts.forEach(alert => {
          alertsStore.lastAlertIds.add(alert.id)
        })
        alertsStore.isFirstLoad = false
      } else if (showToast) {
        // Проверяем на новые непрочитанные оповещения которых еще не были показаны как toast
        for (const alert of newAlerts) {
          if (!alert.isRead && !alertsStore.lastAlertIds.has(alert.id)) {
            // Это новое неприч оповещение
            alertsStore.lastAlertIds.add(alert.id)
            // Показываем toast через глобальное хранилище
            if (alert.message) {
              const toastType = getToastType(alert.alertType)
              toast.show(alert.message, toastType, 4000)
            }
          }
        }
      }
      
      alertsStore.alerts.value = newAlerts
      alertsStore.errorCount = 0 // Reset error counter on success
    } catch (error) {
      alertsStore.errorCount++
      console.warn(`Alert loading error (${alertsStore.errorCount}):`, error.message)
      
      // Stop polling after 5 consecutive errors to prevent spamming
      if (alertsStore.errorCount >= 5) {
        console.error('Too many alert polling errors, stopping polling')
        if (alertsStore.updateInterval) {
          clearInterval(alertsStore.updateInterval)
          alertsStore.updateInterval = null
        }
      }
    }
  }

  const getToastType = (alertType) => {
    switch (alertType) {
      case 'critical': return 'error'
      case 'warning': return 'warning'
      case 'success': return 'success'
      case 'info':
      default: return 'info'
    }
  }

  const markAlertAsRead = async (alertId) => {
    try {
      await inventoryAlertApi.markAsRead(alertId)
      const alert = alertsStore.alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.isRead = true
      }
    } catch (error) {
      console.error('Ошибка:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await inventoryAlertApi.markAllAsRead()
      alertsStore.alerts.value.forEach(a => a.isRead = true)
    } catch (error) {
      console.error('Ошибка:', error)
    }
  }

  const deleteAlert = async (alertId) => {
    try {
      await inventoryAlertApi.delete(alertId)
      alertsStore.alerts.value = alertsStore.alerts.value.filter(a => a.id !== alertId)
    } catch (error) {
      console.error('Ошибка:', error)
    }
  }

  const startPolling = () => {
    if (!alertsStore.updateInterval) {
      loadAlerts(false) // Initial load without toast
      alertsStore.updateInterval = setInterval(() => {
        loadAlerts(true) // Regular polling with toast for new alerts
      }, 10000)
    }
  }

  const stopPolling = () => {
    if (alertsStore.updateInterval) {
      clearInterval(alertsStore.updateInterval)
      alertsStore.updateInterval = null
    }
  }

  return {
    // State
    alerts: computed(() => alertsStore.alerts.value),
    unreadCount,
    criticalCount,
    
    // Methods
    loadAlerts,
    markAlertAsRead,
    markAllAsRead,
    deleteAlert,
    startPolling,
    stopPolling
  }
}
