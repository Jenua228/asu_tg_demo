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
  // const toast = useToast()

  const unreadCount = computed(() => {
    //console.log('aaaaa', alertsStore.alerts.value.map(a => a.isRead));
    return alertsStore.alerts.value.filter(a => !a.isRead).length
  })

  const criticalCount = computed(() => {
    return alertsStore.alerts.value.filter(a => a.alertType === 'critical').length
  })

  // Функция для загрузки оповещений с показом toast для новых
  const loadAlerts = async (showToast = true) => {
    try {
      const response = await inventoryAlertApi.getAllLimited(10)
      const newAlerts = (response.data || []).filter(a => a.message && a.message.trim().length > 0)

          
      // При первой загрузке просто запоминаем существующие оповещения, не показываем toast
      if (alertsStore.isFirstLoad) {
        newAlerts.forEach(alert => {
          alertsStore.lastAlertIds.add(alert.id)
        })
        alertsStore.isFirstLoad = false
      } else {
        // Нет toast notifications - просто добавляем в lastAlertIds
        for (const alert of newAlerts) {
          if (!alert.isRead && !alertsStore.lastAlertIds.has(alert.id)) {
            alertsStore.lastAlertIds.add(alert.id)
          }
        }
      }
      
      alertsStore.alerts.value = newAlerts
      alertsStore.errorCount = 0 // Reset error counter on success
    } catch (error) {
      alertsStore.errorCount++
      
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

  // const getToastType = (alertType) => {
  //   switch (alertType) {
  //     case 'critical': return 'error'
  //     case 'warning': return 'warning'
  //     case 'success': return 'success'
  //     case 'info':
  //     default: return 'info'
  //   }
  // }

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

  const startPolling = async () => {
    if (!alertsStore.updateInterval) {
      await loadAlerts(false) // Initial load without toast
      alertsStore.updateInterval = setInterval(() => {
        loadAlerts(true) // Regular polling with toast for new alerts
      }, 10000)
    }
    else{
      console.log('🟡 Polling already active')
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
