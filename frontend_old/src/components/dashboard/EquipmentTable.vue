<template>
  <div class="equipment-container">
    <div class="table-header">
      <h2>{{ $t('eq.workEq') }}</h2>
      <div class="filters">
        <select v-model="selectedWorkshop" class="filter-select">
          <option value="all">{{ $t('eq.all') }}</option>
          <option v-for="workshop in workshops" :key="workshop.id" :value="workshop.id">
            {{ workshop.name }}
          </option>
        </select>
        <select v-model="selectedStatus" class="filter-select">
          <option value="all">{{ $t('eq.allStat') }}</option>
          <option value="operational">Рабочее</option>
          <option value="maintenance">На обслуживании</option>
          <option value="repair">В ремонте</option>
          <option value="idle">Простой</option>
        </select>
      </div>
    </div>

    <div class="table-responsive">
      <table class="equipment-table">
        <thead>
          <tr>
            <th>{{ $t('eq.columns.name') }}</th>
            <th>{{ $t('eq.columns.reg') }}</th>
            <th>{{ $t('eq.columns.tcr') }}</th>
            <th>{{ $t('eq.columns.status') }}</th>
            <th>{{ $t('eq.columns.load') }}</th>
            <th>{{ $t('eq.columns.last') }}</th>
            <th>{{ $t('eq.columns.next') }}</th>
            <th>{{ $t('eq.columns.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredEquipment" :key="item.id">
            <td class="equipment-name">
              <div class="name-cell">
                <div class="status-indicator" :class="item.status"></div>
                {{ item.name }}
              </div>
            </td>
            <td>{{ item.type }}</td>
            <td>
              <span class="workshop-badge" :style="{ backgroundColor: getWorkshopColor(item.workshopId) }">
                {{ getWorkshopName(item.workshopId) }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="item.status">
                {{ getStatusText(item.status) }}
              </span>
            </td>
            <td>
              <div class="workload-cell">
                <div class="workload-bar">
                  <div 
                    class="workload-fill" 
                    :style="{ 
                      width: `${item.workload}%`,
                      backgroundColor: getColorForWorkload(item.workload)
                    }"
                  ></div>
                </div>
                <span class="workload-value">{{ item.workload }}%</span>
              </div>
            </td>
            <td>{{ formatDate(item.lastService) }}</td>
            <td>{{ formatDate(item.nextService) }}</td>
            <td>
              <button 
                class="btn-details"
                @click="$emit('equipment-details', item)"
              >
                {{ $t('workshopdetail.learn') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="table-footer">
      <div class="summary">
        {{$t('dashboard2.showing')}} {{ filteredEquipment.length }} {{$t('dashboard2.of')}} {{ equipment.length }} {{$t('eq.piece')}}
      </div>
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">{{ $t('eq.workers') }}</span>
          <span class="stat-value operational">{{ operationalCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">{{ $t('eq.OnTO') }}</span>
          <span class="stat-value maintenance">{{ maintenanceCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">{{ $t('eq.InRepair') }}</span>
          <span class="stat-value repair">{{ repairCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  equipment: {
    type: Array,
    default: () => []
  },
  workshops: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['equipment-details'])

const selectedWorkshop = ref('all')
const selectedStatus = ref('all')

const filteredEquipment = computed(() => {
  return props.equipment.filter(item => {
    const workshopMatch = selectedWorkshop.value === 'all' || 
      item.workshopId === parseInt(selectedWorkshop.value)
    const statusMatch = selectedStatus.value === 'all' || 
      item.status === selectedStatus.value
    return workshopMatch && statusMatch
  })
})

const operationalCount = computed(() => {
  return props.equipment.filter(e => e.status === 'operational').length
})

const maintenanceCount = computed(() => {
  return props.equipment.filter(e => e.status === 'maintenance').length
})

const repairCount = computed(() => {
  return props.equipment.filter(e => e.status === 'repair').length
})

const getWorkshopName = (workshopId) => {
  const workshop = props.workshops.find(w => w.id === workshopId)
  return workshop?.name || 'Неизвестно'
}

const getWorkshopColor = (workshopId) => {
  const workshop = props.workshops.find(w => w.id === workshopId)
  return workshop?.color || '#ccc'
}

const getStatusText = (status) => {
  const statusMap = {
    operational: 'Рабочее',
    maintenance: 'На обслуживании',
    repair: 'В ремонте',
    idle: 'Простой'
  }
  return statusMap[status] || status
}

const getColorForWorkload = (workload) => {
  if (workload >= 80) return '#f44336'
  if (workload >= 60) return '#ff9800'
  if (workload >= 40) return '#4CAF50'
  return '#2196F3'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.equipment-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.filters {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: #4CAF50;
}

.table-responsive {
  overflow-x: auto;
  margin-bottom: 20px;
}

.equipment-table {
  width: 100%;
  border-collapse: collapse;
}

.equipment-table th {
  background: #f8f9fa;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
  white-space: nowrap;
}

.equipment-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.equipment-table tbody tr:hover {
  background-color: #f8f9fa;
}

.equipment-name {
  font-weight: 500;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.operational {
  background-color: #4CAF50;
}

.status-indicator.maintenance {
  background-color: #FF9800;
}

.status-indicator.repair {
  background-color: #F44336;
}

.status-indicator.idle {
  background-color: #9E9E9E;
}

.workshop-badge {
  padding: 4px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

.status-badge.operational {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.status-badge.maintenance {
  background-color: #FFF3E0;
  color: #EF6C00;
}

.status-badge.repair {
  background-color: #FFEBEE;
  color: #D32F2F;
}

.status-badge.idle {
  background-color: #F5F5F5;
  color: #616161;
}

.workload-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.workload-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.workload-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.workload-value {
  min-width: 40px;
  text-align: right;
  font-weight: 500;
}

.btn-details {
  padding: 6px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-details:hover {
  background: #45a049;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.summary {
  color: #666;
  font-size: 14px;
}

.stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  font-weight: bold;
  font-size: 16px;
}

.stat-value.operational {
  color: #4CAF50;
}

.stat-value.maintenance {
  color: #FF9800;
}

.stat-value.repair {
  color: #F44336;
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filters {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>