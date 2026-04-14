<template>
  <div class="inventory-management">
    <!-- Заголовок с кнопками управления -->
    <div class="inventory-header">
      <h2>{{ $t('inventory.warehouseTitle') }}</h2>
      
      <div class="header-actions">
        <button @click="openAddItemModal" class="btn-add">
          ➕ {{ $t('inventory.addItem') }}
        </button>
        
        <button @click="checkLowStock" class="btn-check" :disabled="isLoading">
          ⚠️ {{ $t('inventory.checkLowStock') }}
        </button>
        
        <button @click="refreshInventory" class="btn-refresh" :disabled="isLoading">
          🔄 {{ $t('inventory.refresh') }}
        </button>
      </div>
    </div>
    
    <!-- Статистика -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ items.length }}</div>
        <div class="stat-label">{{ $t('inventory.totalItems') }}</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ lowStockCount }}</div>
        <div class="stat-label">{{ $t('inventory.lowStockItems') }}</div>
      </div>
      <div class="stat-card critical">
        <div class="stat-value">{{ criticalStockCount }}</div>
        <div class="stat-label">{{ $t('inventory.criticalItems') }}</div>
      </div>
    </div>
    
    <!-- Таблица товаров -->
    <div class="inventory-table-container" v-if="items.length > 0">
      <table class="inventory-table">
        <thead>
          <tr>
            <th>{{ $t('inventory.article') }}</th>
            <th>{{ $t('inventory.name') }}</th>
            <th>{{ $t('inventory.currentStock') }}</th>
            <th>{{ $t('inventory.minStock') }}</th>
            <th>{{ $t('inventory.available') }}</th>
            <th>{{ $t('inventory.storage') }}</th>
            <th>{{ $t('inventory.activeRequests') }}</th>
            <th>{{ $t('inventory.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="item in items" 
            :key="item.id"
            :class="getRowClass(item)"
          >
            <td class="article-cell"><strong>{{ item.article }}</strong></td>
            <td class="name-cell">{{ item.nameRus }}</td>
            <td class="stock-cell">
              <input 
                v-model.number="item.currentCount"
                type="number"
                @blur="updateItemCount(item)"
                @keyup.enter="updateItemCount(item)"
                class="inline-input"
              />
            </td>
            <td class="min-stock-cell">
              <span class="badge-min">{{ item.minStock }}</span>
            </td>
            <td :class="getAvailabilityClass(item)">
              {{ item.availableCount || 0 }}
            </td>
            <td>{{ item.storageName || '—' }}</td>
            <td class="requests-cell">
              <span class="badge-requests">{{ getActiveRequestCount(item.id) }}</span>
            </td>
            <td class="actions-cell">
              <button 
                @click="editItem(item)"
                class="btn-edit"
                :title="$t('inventory.edit')"
              >
                ✏️
              </button>
              <button 
                @click="viewItemRequests(item)"
                class="btn-requests"
                :title="$t('inventory.viewRequests')"
              >
                📦
              </button>
              <button 
                @click="createRequestForItem(item)"
                class="btn-request"
                :title="$t('inventory.createRequest')"
              >
                ➕
              </button>
              <button 
                @click="deleteItem(item.id)"
                class="btn-delete"
                :title="$t('inventory.delete')"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Пустое состояние -->
    <div v-else class="empty-state">
      <p>{{ $t('inventory.noItems') }}</p>
      <button @click="openAddItemModal" class="btn-add-primary">
        {{ $t('inventory.addFirstItem') }}
      </button>
    </div>
    
    <!-- Модальное окно дтя добавления/редактирования товара -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingItem.id ? $t('inventory.editItem') : $t('inventory.addItem') }}</h3>
          <button class="close-btn" @click="closeEditModal">&times;</button>
        </div>
        
        <div class="form-content">
          <div class="form-group">
            <label>{{ $t('inventory.article') }} *</label>
            <input v-model="editingItem.article" type="text" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('inventory.nameRus') }} *</label>
            <input v-model="editingItem.nameRus" type="text" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('inventory.nameEng') }}</label>
            <input v-model="editingItem.nameEng" type="text" class="form-input" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('inventory.currentCount') }} *</label>
              <input v-model.number="editingItem.currentCount" type="number" class="form-input" />
            </div>
            
            <div class="form-group">
              <label>{{ $t('inventory.minStock') }} *</label>
              <input v-model.number="editingItem.minStock" type="number" class="form-input" />
            </div>
          </div>
          
          <div class="form-group">
            <label>{{ $t('inventory.storage') }}</label>
            <input v-model="editingItem.storageName" type="text" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('inventory.comment') }}</label>
            <textarea v-model="editingItem.comment" class="form-input" rows="3"></textarea>
          </div>
          
          <div class="form-group">
            <label>{{ $t('inventory.pdfUrl') }}</label>
            <input v-model="editingItem.pdfUrl" type="text" class="form-input" placeholder="https://..." />
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeEditModal" class="btn-cancel">
            {{ $t('common.cancel') }}
          </button>
          <button @click="saveItem" class="btn-save">
            {{ $t('common.save') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для просмотра заявок товара -->
    <div v-if="showRequestsModal && selectedItem" class="modal-overlay" @click="closeRequestsModal">
      <div class="modal-content modal-wide" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('inventory.requestsFor') }}: {{ selectedItem.nameRus }}</h3>
          <button class="close-btn" @click="closeRequestsModal">&times;</button>
        </div>
        
        <div class="requests-list">
          <div v-if="selectedItemRequests.length > 0" class="request-items">
            <div v-for="req in selectedItemRequests" :key="req.id" class="request-item">
              <span class="req-qty">{{ req.requestedQuantity }} шт.</span>
              <span class="req-status" :class="`status-${req.status}`">{{ req.status }}</span>
              <span class="req-reason">{{ req.reason === 'auto' ? '🤖 Авто' : '👤 Ручная' }}</span>
              <span class="req-date">{{ formatDate(req.createdAt) }}</span>
            </div>
          </div>
          <div v-else class="no-requests">
            {{ $t('inventory.noRequestsForItem') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { inventoryApi, inventoryRequestApi } from '../../api'

const { t } = useI18n()

const items = ref([])
const requests = ref([])
const editingItem = ref({})
const selectedItem = ref(null)
const showEditModal = ref(false)
const showRequestsModal = ref(false)
const isLoading = ref(false)

const lowStockCount = computed(() => {
  return items.value.filter(item => getAvailability(item) < item.minStock).length
})

const criticalStockCount = computed(() => {
  return items.value.filter(item => getAvailability(item) <= 0).length
})

const selectedItemRequests = computed(() => {
  if (!selectedItem.value) return []
  return requests.value.filter(req => req.inventoryItem.id === selectedItem.value.id)
})

const getAvailability = (item) => {
  const qty = requests.value
    .filter(req => req.inventoryItem.id === item.id && ['новая', 'в_процессе'].includes(req.status))
    .reduce((sum, req) => sum + req.requestedQuantity, 0)
  return item.currentCount - qty
}

const getRowClass = (item) => {
  const availability = getAvailability(item)
  if (availability <= 0) return 'row-critical'
  if (availability < item.minStock) return 'row-warning'
  return ''
}

const getAvailabilityClass = (item) => {
  const availability = getAvailability(item)
  if (availability <= 0) return 'availability-critical'
  if (availability < item.minStock) return 'availability-warning'
  return 'availability-ok'
}

const getActiveRequestCount = (itemId) => {
  return requests.value.filter(
    req => req.inventoryItem.id === itemId && ['новая', 'в_процессе'].includes(req.status)
  ).length
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU')
}

const refreshInventory = async () => {
  isLoading.value = true
  try {
    const [itemsRes, requestsRes] = await Promise.all([
      inventoryApi.getAll(),
      inventoryRequestApi.getAll()
    ])
    items.value = itemsRes.data
    requests.value = requestsRes.data
  } catch (error) {
    console.error('Ошибка при загрузке:', error)
  } finally {
    isLoading.value = false
  }
}

const openAddItemModal = () => {
  editingItem.value = { currentCount: 0, minStock: 0 }
  showEditModal.value = true
}

const editItem = (item) => {
  editingItem.value = { ...item }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingItem.value = {}
}

const saveItem = async () => {
  try {
    if (editingItem.value.id) {
      await inventoryApi.update(editingItem.value.id, editingItem.value)
    } else {
      await inventoryApi.create(editingItem.value)
    }
    await refreshInventory()
    closeEditModal()
  } catch (error) {
    console.error('Ошибка:', error)
    alert(t('inventory.saveError'))
  }
}

const updateItemCount = async (item) => {
  try {
    await inventoryApi.update(item.id, { currentCount: item.currentCount })
    } catch (error) {
    console.error('Ошибка при обновлении:', error)
  }
}

const deleteItem = async (itemId) => {
  if (!confirm(t('inventory.confirmDelete'))) return
  try {
    await inventoryApi.delete(itemId)
    await refreshInventory()
  } catch (error) {
    console.error('Ошибка:', error)
  }
}

const viewItemRequests = (item) => {
  selectedItem.value = item
  showRequestsModal.value = true
}

const closeRequestsModal = () => {
  showRequestsModal.value = false
  selectedItem.value = null
}

const createRequestForItem = async (item) => {
  const quantity = prompt(t('inventory.enterQuantity'))
  if (!quantity) return
  
  try {
    await inventoryRequestApi.create({
      inventoryItemId: item.id,
      requestedQuantity: parseInt(quantity),
      reason: 'manual'
    })
    await refreshInventory()
    alert(t('inventory.requestCreated'))
  } catch (error) {
    console.error('Ошибка:', error)
    alert(t('inventory.requestError'))
  }
}

const checkLowStock = async () => {
  isLoading.value = true
  try {
    await inventoryApi.checkLowStock()
    await refreshInventory()
    alert(t('inventory.checkCompleted'))
  } catch (error) {
    console.error('Ошибка:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  refreshInventory()
})
</script>

<style scoped>
.inventory-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.inventory-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-add, .btn-check, .btn-refresh {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-add {
  background: #4b5563;
  color: white;
}

.btn-add:hover {
  background: #374151;
}

.btn-check {
  background: #f59e0b;
  color: white;
}

.btn-check:hover:not(:disabled) {
  background: #d97706;
}

.btn-refresh {
  background: #6b7280;
  color: white;
}

.btn-refresh:hover:not(:disabled) {
  background: #4b5563;
}

.btn-add:disabled, .btn-check:disabled, .btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
}

.stat-card.warning {
  border-left-color: #f59e0b;
}

.stat-card.critical {
  border-left-color: #ef4444;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
}

.inventory-table-container {
  overflow-x: auto;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
}

.inventory-table thead {
  background: #f3f4f6;
  font-weight: 600;
}

.inventory-table th {
  padding: 12px;
  text-align: left;
  font-size: 13px;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.inventory-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
}

.inventory-table tbody tr:hover {
  background: #f9fafb;
}

.row-critical {
  background: #fee2e2 !important;
}

.row-warning {
  background: #fef3c7 !important;
}

.article-cell {
  color: #1f2937;
  font-family: monospace;
}

.name-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-cell {
  font-weight: 600;
  text-align: center;
}

.inline-input {
  width: 60px;
  padding: 4px;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  text-align: center;
}

.min-stock-cell {
  text-align: center;
}

.badge-min {
  display: inline-block;
  padding: 4px 8px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 3px;
  font-size: 12px;
}

.availability-ok {
  color: #10b981;
  font-weight: 600;
}

.availability-warning {
  color: #f59e0b;
  font-weight: 600;
}

.availability-critical {
  color: #ef4444;
  font-weight: 700;
}

.requests-cell {
  text-align: center;
}

.badge-requests {
  display: inline-block;
  padding: 4px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.actions-cell {
  display: flex;
  gap: 4px;
}

.btn-edit, .btn-requests, .btn-request, .btn-delete {
  padding: 4px 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
}

.btn-edit:hover {
  background: #dbeafe;
  border-radius: 3px;
}

.btn-requests:hover {
  background: #fef3c7;
  border-radius: 3px;
}

.btn-request:hover {
  background: #dbeafe;
  border-radius: 3px;
}

.btn-delete:hover {
  background: #fee2e2;
  border-radius: 3px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.btn-add-primary {
  margin-top: 20px;
  padding: 12px 24px;
  background: #4b5563;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
}

.btn-add-primary:hover {
  background: #374151;
}

/* Modal Styles */
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
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.modal-wide {
  max-width: 700px;
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

.form-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #4b5563;
  box-shadow: 0 0 0 2px rgba(75, 85, 99, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-cancel, .btn-save {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-cancel {
  background: #e5e7eb;
  color: #374151;
}

.btn-cancel:hover {
  background: #d1d5db;
}

.btn-save {
  background: #4b5563;
  color: white;
}

.btn-save:hover {
  background: #374151;
}

.requests-list {
  max-height: 400px;
  overflow-y: auto;
}

.request-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.request-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 13px;
}

.req-qty {
  font-weight: 600;
  color: #1f2937;
  min-width: 60px;
}

.req-status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.req-status.status-новая {
  background: #dbeafe;
  color: #1e40af;
}

.req-status.status-в_процессе {
  background: #fed7aa;
  color: #7c2d12;
}

.req-status.status-выполнена {
  background: #d1fae5;
  color: #065f46;
}

.req-reason {
  min-width: 80px;
}

.req-date {
  margin-left: auto;
  color: #6b7280;
  font-size: 12px;
}

.no-requests {
  text-align: center;
  padding: 20px;
  color: #6b7280;
}
</style>
