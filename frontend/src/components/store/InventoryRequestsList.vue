<template>
  <div class="inventory-requests-panel">
    <!-- Заголовок с фильтрами -->
    <div class="requests-header">
      <h2>{{ $t('inventory.requestsTitle') }} ({{ requests.length }})</h2>
      
      <div class="filter-controls">
        <select v-model="selectedStatus" class="status-filter" @change="applyStatusFilter">
          <option value="">{{ $t('inventory.allStatuses') }}</option>
          <option value="новая">{{ $t('inventory.statusNew') }}</option>
          <option value="в_процессе">{{ $t('inventory.statusInProcess') }}</option>
          <option value="выполнена">{{ $t('inventory.statusCompleted') }}</option>
          <option value="отменена">{{ $t('inventory.statusCancelled') }}</option>
        </select>
        
        <button @click="refreshRequests" class="btn-refresh" :disabled="isLoading">
          🔄 {{ $t('inventory.refresh') }}
        </button>
        
        <button @click="checkLowStockAndCreate" class="btn-check-stock" :disabled="isLoading">
          ⚠️ {{ $t('inventory.checkLowStock') }}
        </button>

        <!-- Кнопка возврата на вкладку товаров -->
        <button @click="goBackToInventory" class="btn-back">
          ← {{ $t('common.back') }}
        </button>
      </div>
    </div>
    
    <!-- Таблица заявок -->
    <div class="requests-table-container" v-if="filteredRequests.length > 0">
      <table class="requests-table">
        <thead>
          <tr>
            <th>{{ $t('inventory.id') }}</th>
            <th>{{ $t('inventory.itemArticle') }}</th>
            <th>{{ $t('inventory.itemName') }}</th>
            <th>{{ $t('inventory.quantity') }}</th>
            <th>{{ $t('inventory.reason') }}</th>
            <th>{{ $t('inventory.status') }}</th>
            <th>{{ $t('inventory.createdDate') }}</th>
            <th>{{ $t('inventory.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="req in filteredRequests" 
            :key="req.id"
            :class="`status-${req.status}`"
          >
            <td class="id-cell">{{ req.id }}</td>
            <td>{{ req.inventoryItem.article }}</td>
            <td class="name-cell">{{ req.inventoryItem.nameRus }}</td>
            <td class="quantity-cell">
              <!-- Редактируемое поле количества -->
              <input 
                :value="req.requestedQuantity"
                @change="updateRequestQuantity(req.id, parseInt($event.target.value), req)"
                type="number"
                min="1"
                class="quantity-input"
              />
            </td>
            <td>
              <span :class="`badge-${req.reason}`">
                {{ req.reason === 'manual' ? $t('inventory.reasonManual') : $t('inventory.reasonAuto') }}
              </span>
            </td>
            <td>
              <select 
                :value="req.status"
                @change="updateRequestStatus(req.id, $event.target.value)"
                class="status-select"
              >
                <option value="новая">{{ $t('inventory.statusNew') }}</option>
                <option value="в_процессе">{{ $t('inventory.statusInProcess') }}</option>
                <option value="выполнена">{{ $t('inventory.statusCompleted') }}</option>
                <option value="отменена">{{ $t('inventory.statusCancelled') }}</option>
              </select>
            </td>
            <td class="date-cell">{{ formatDate(req.createdAt) }}</td>
            <td class="actions-cell">
              <button 
                @click="viewRequestDetails(req)"
                class="btn-details"
                :title="$t('inventory.viewDetails')"
              >
                👁️
              </button>
              <button 
                v-if="req.status !== 'отменена'"
                @click="deleteRequest(req.id)"
                class="btn-delete"
                :title="$t('inventory.cancel')"
              >
                ✕
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Пустое состояние -->
    <div v-else class="empty-state">
      <p>{{ $t('inventory.noRequests') }}</p>
    </div>
    
    <!-- Модальное окно деталей заявки -->
    <div v-if="selectedRequest" class="modal-overlay" @click="closeRequestDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('inventory.requestDetails') }} #{{ selectedRequest.id }}</h3>
          <button class="close-btn" @click="closeRequestDetails">&times;</button>
        </div>
        
        <div class="request-details-content">
          <div class="detail-section">
            <h4>{{ $t('inventory.itemInfo') }}</h4>
            <p><strong>{{ $t('inventory.article') }}:</strong> {{ selectedRequest.inventoryItem.article }}</p>
            <p><strong>{{ $t('inventory.name') }}:</strong> {{ selectedRequest.inventoryItem.nameRus }}</p>
            <p><strong>{{ $t('inventory.quantity') }}:</strong> {{ selectedRequest.requestedQuantity }}</p>
          </div>
          
          <div class="detail-section">
            <h4>{{ $t('inventory.requestInfo') }}</h4>
            <p><strong>{{ $t('inventory.reason') }}:</strong> {{ selectedRequest.reason }}</p>
            <p><strong>{{ $t('inventory.status') }}:</strong> {{ selectedRequest.status }}</p>
            <p><strong>{{ $t('inventory.createdBy') }}:</strong> {{ selectedRequest.createdBy || '—' }}</p>
            <p><strong>{{ $t('inventory.createdAt') }}:</strong> {{ formatDatetime(selectedRequest.createdAt) }}</p>
          </div>
          
          <div v-if="selectedRequest.relatedRepairDetailId" class="detail-section">
            <h4>{{ $t('inventory.relatedRepair') }}</h4>
            <p><strong>{{ $t('inventory.repairDetailId') }}:</strong> {{ selectedRequest.relatedRepairDetailId }}</p>
          </div>
          
          <div class="detail-section">
            <h4>{{ $t('inventory.plannedDelivery') }}</h4>
            <input 
              v-model="selectedRequest.plannedDeliveryDate"
              type="date"
              class="input-date"
            >
            <button @click="updateDeliveryDate" class="btn-save-date">
              {{ $t('inventory.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { inventoryRequestApi, inventoryApi } from '../../api'

const { t } = useI18n()

const emit = defineEmits(['back-to-inventory'])

const requests = ref([])
const selectedStatus = ref('')
const selectedRequest = ref(null)
const isLoading = ref(false)

const filteredRequests = computed(() => {
  if (!selectedStatus.value) {
    return requests.value
  }
  return requests.value.filter(req => req.status === selectedStatus.value)
})

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('ru-RU')
}

const formatDatetime = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleString('ru-RU')
}

const refreshRequests = async () => {
  isLoading.value = true
  try {
    const response = await inventoryRequestApi.getAll()
    requests.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке заявок:', error)
    alert(t('inventory.loadError'))
  } finally {
    isLoading.value = false
  }
}

// Автоматически загружаем заявки при монтировании
onMounted(() => {
  refreshRequests()
})

const applyStatusFilter = () => {
  // Фильтрация уже происходит через computed свойство
}

const updateRequestStatus = async (requestId, newStatus) => {
  try {
    console.log('📤 Обновляю статус заявки ID=' + requestId + ' на "' + newStatus + '"')
    await inventoryRequestApi.update(requestId, { status: newStatus })
    console.log('✅ Статус обновлён в БД')
    // Обновляем локальный список
    const req = requests.value.find(r => r.id === requestId)
    if (req) {
      req.status = newStatus
    }
  } catch (error) {
    console.error('Ошибка при обновлении статуса:', error)
    alert(t('inventory.updateError'))
  }
}

const updateRequestQuantity = async (requestId, newQuantity, request) => {
  if (!newQuantity || newQuantity < 1) {
    alert('Количество должно быть больше 0')
    return
  }
  
  try {
    console.log('📤 Обновляю кол-во заявки ID=' + requestId + ' на ' + newQuantity)
    await inventoryRequestApi.update(requestId, { requestedQuantity: newQuantity })
    console.log('✅ Количество обновлено в БД')
    // Обновляем локальный список
    const req = requests.value.find(r => r.id === requestId)
    if (req) {
      req.requestedQuantity = newQuantity
    }
  } catch (error) {
    console.error('Ошибка при обновлении количества:', error)
    alert('Ошибка при обновлении количества: ' + error.message)
  }
}

const updateDeliveryDate = async () => {
  if (!selectedRequest.value) return
  
  try {
    await inventoryRequestApi.update(selectedRequest.value.id, {
      plannedDeliveryDate: selectedRequest.value.plannedDeliveryDate
    })
    alert(t('inventory.dateSaved'))
  } catch (error) {
    console.error('Ошибка:', error)
  }
}

const deleteRequest = async (requestId) => {
  if (!confirm(t('inventory.confirmCancel'))) return
  
  try {
    await inventoryRequestApi.delete(requestId)
    requests.value = requests.value.filter(r => r.id !== requestId)
  } catch (error) {
    console.error('Ошибка при удалении заявки:', error)
    alert(t('inventory.deleteError'))
  }
}

const viewRequestDetails = (req) => {
  selectedRequest.value = { ...req }
}

const closeRequestDetails = () => {
  selectedRequest.value = null
}

const checkLowStockAndCreate = async () => {
  isLoading.value = true
  try {
    // Используем inventoryApi для проверки низких запасов
    const response = await inventoryApi.checkLowStock()
    // После проверки обновляем список заявок
    await refreshRequests()
    alert(t('inventory.checkCompleted'))
  } catch (error) {
    console.error('Ошибка при проверке запасов:', error)
  } finally {
    isLoading.value = false
  }
}

const goBackToInventory = () => {
  // Отправляем событие родителю
  emit('back-to-inventory')
}

onMounted(() => {
  refreshRequests()
})
</script>

<style scoped>
.inventory-requests-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.requests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.requests-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1f2937;
}

.filter-controls {
  display: flex;
  gap: 10px;
}

.status-filter,
.status-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh,
.btn-check-stock {
  padding: 8px 15px;
  background: #4b5563;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover:not(:disabled) {
  background: #374151;
}

.btn-check-stock {
  background: #f59e0b;
}

.btn-check-stock:hover:not(:disabled) {
  background: #d97706;
}

.btn-refresh:disabled,
.btn-check-stock:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-back {
  padding: 8px 15px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-left: auto;
}

.btn-back:hover {
  background: #4f46e5;
}

.requests-table-container {
  overflow-x: auto;
}

.requests-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.requests-table thead {
  background: #f3f4f6;
  font-weight: 600;
}

.requests-table th {
  padding: 12px;
  text-align: left;
  font-size: 14px;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.requests-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
}

.requests-table tbody tr:hover {
  background: #f9fafb;
}

.requests-table tr.status-новая {
  border-left: 4px solid #3b82f6;
}

.requests-table tr.status-в_процессе {
  border-left: 4px solid #f59e0b;
}

.requests-table tr.status-выполнена {
  border-left: 4px solid #10b981;
}

.requests-table tr.status-отменена {
  border-left: 4px solid #ef4444;
  opacity: 0.7;
}

.id-cell {
  font-weight: 600;
  color: #4b5563;
}

.name-cell {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quantity-cell {
  text-align: center;
  font-weight: 600;
  color: #1f2937;
}

.date-cell {
  color: #6b7280;
  font-size: 12px;
}

.actions-cell {
  display: flex;
  gap: 5px;
}

.btn-details,
.btn-delete {
  padding: 4px 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}

.btn-details:hover {
  background: #dbeafe;
  border-radius: 4px;
}

.btn-delete:hover {
  background: #fee2e2;
  border-radius: 4px;
}

.badge-manual {
  display: inline-block;
  padding: 4px 8px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-auto {
  display: inline-block;
  padding: 4px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.close-btn:hover {
  color: #1f2937;
}

.request-details-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: #f9fafb;
  padding: 15px;
  border-radius: 6px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 14px;
  font-weight: 600;
}

.detail-section p {
  margin: 8px 0;
  font-size: 14px;
  color: #4b5563;
}

.input-date {
  width: 100%;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  margin-bottom: 10px;
}

.btn-save-date {
  padding: 8px 15px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save-date:hover {
  background: #059669;
}

.quantity-input {
  width: 70px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.quantity-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.status-select {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.status-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
</style>
