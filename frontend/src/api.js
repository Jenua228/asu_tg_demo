import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// ==================== GANTT API ====================

/*export const taskApi = {
  getAll: () => api.get('/tasks'),
  get: (id) => api.get(`/tasks/${id}`),
  create: (task) => api.post('/tasks', task),
  //update: (id, task) => api.put(`/tasks/${id}`, task),
  //delete: (id) => api.delete(`/tasks/${id}`),
  seed: () => api.post('/tasks/seed')
}*/

/*export const connectionApi = {
  getAll: () => api.get('/connections'),
  create: (connection) => api.post('/connections', connection),
  update: (id, connection) => api.put(`/connections/${id}`, connection),
  delete: (id) => api.delete(`/connections/${id}`)
}*/

// Report Connections (для диаграммы Ганта из отчётов)
export const reportConnectionApi = {
  getAll: () => api.get('/report-connections'),
  create: (connection) => api.post('/report-connections', connection),
  update: (id, connection) => api.put(`/report-connections/${id}`, connection),
  delete: (id) => api.delete(`/report-connections/${id}`)
}

// Gantt data from Reports
export const ganttDataApi = {
  getAll: () => api.get('/gantt-data'),
  update: (id, data) => api.put(`/gantt-data/${id}`, data)
}

// ==================== REPORTS API ====================

export const reportApi = {
  getAll: () => api.get('/reports'),
  create: (record) => api.post('/reports', record),
  update: (id, record) => api.put(`/reports/${id}`, record),
  delete: (id) => api.delete(`/reports/${id}`),
  reset: () => api.post('/reports/reset')
}

// ==================== GANTT (READ-ONLY) ====================

export const ganttApi = {
  // Получить все данные для Ганта (задачи + связи)
  getAll: () => api.get('/gantt'),
  
  // Обновление дат при перетаскивании (работает с report_records)
  updateDates: (id, data) => api.put(`/gantt-data/${id}`, data)
}

// ==================== REPAIR DETAILS API ====================

export const repairDetailApi = {
  // Получить все этапы для записи
  getByReportId: (reportId) => api.get(`/repair-details/${reportId}`),
  
  // Инициализировать этапы (создать 16 пустых)
  init: (reportId) => api.post(`/repair-details/${reportId}/init`),
  
  // Обновить этап
  update: (detailId, data) => api.put(`/repair-details/item/${detailId}`, data),
  
  // Удалить этап
  delete: (detailId) => api.delete(`/repair-details/item/${detailId}`),
  create: (reportId, data) => api.post(`/repair-details/${reportId}`, data)
}

// ==================== INVENTORY API (СКЛАД ЗИП) ====================

export const inventoryApi = {
  // Управление товарами на складе
  getAll: () => api.get('/inventory'),
  get: (id) => api.get(`/inventory/${id}`),
  create: (item) => api.post('/inventory', item),
  update: (id, item) => api.put(`/inventory/${id}`, item),
  delete: (id) => api.delete(`/inventory/${id}`),
  
  // Проверка минимальных запасов и автоматическое создание заявок
  checkLowStock: () => api.post('/inventory/check-low-stock')
}

// ==================== INVENTORY REQUESTS API (ЗАЯВКИ) ====================

export const inventoryRequestApi = {
  // Управление заявками на пополнение
  getAll: () => api.get('/inventory-requests'),
  getAllFiltered: (status) => api.get(`/inventory-requests?status=${status}`),
  get: (id) => api.get(`/inventory-requests/${id}`),
  create: (request) => api.post('/inventory-requests', request),
  update: (id, request) => api.put(`/inventory-requests/${id}`, request),
  delete: (id) => api.delete(`/inventory-requests/${id}`),
  
  // Удобные методы для обновления статуса
  markAsInProcess: (id) => api.put(`/inventory-requests/${id}`, { status: 'в_процессе' }),
  markAsCompleted: (id) => api.put(`/inventory-requests/${id}`, { status: 'выполнена' }),
  markAsCancelled: (id) => api.put(`/inventory-requests/${id}`, { status: 'отменена' })
}

// ==================== INVENTORY ALERTS API (ОПОВЕЩЕНИЯ) ====================

export const inventoryAlertApi = {
  // Управление оповещениями
  getAll: () => api.get('/inventory-alerts'),
  getUnread: () => api.get('/inventory-alerts?unread=true'),
  getAllLimited: (limit) => api.get(`/inventory-alerts?limit=${limit}`),
  
  // Отметить как прочитанное
  markAsRead: (id) => api.put(`/inventory-alerts/${id}`, { isRead: true }),
  markAllAsRead: () => api.post('/inventory-alerts/mark-all-read'),
  
  // Удалить оповещение
  delete: (id) => api.delete(`/inventory-alerts/${id}`)
}

// ==================== INVENTORY STATISTICS API ====================

export const inventoryStatsApi = {
  // Получить статистику по запасам
  getOverview: () => api.get('/inventory/stats/overview')
}

export default api
