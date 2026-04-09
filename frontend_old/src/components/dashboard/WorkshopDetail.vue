<template>
  <div class="workshop-detail">
    <div class="detail-header">
      <h2>{{ workshop.name }}</h2>
      <button class="btn-close" @click="$emit('close')">×</button>
    </div>

    <div class="detail-content">
      <!-- Основная информация -->
      <div class="info-section">
        <h3>{{ $t('workshopdetail.mainInf') }}</h3>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">{{ $t('workshopdetail.load') }}</div>
            <div class="info-value" :style="{ color: getColorForWorkload(workshop.workload) }">
              {{ workshop.workload }}%
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('workshop.regions') }}</div>
            <div class="info-value">{{ workshop.sections.length }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ $t('workshopdetail.full') }}</div>
            <div class="info-value">
              {{ ((workshop.warehouse.currentStock / workshop.warehouse.capacity) * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Участки цеха -->
      <div class="info-section">
        <h3>{{ $t('workshopdetail.workReg') }}</h3>
        <div class="sections-list">
          <div v-for="section in workshop.sections" :key="section.id" class="section-item">
            <div class="section-header">
              <span class="section-name">{{ section.name }}</span>
              <span class="section-workload" :style="{ color: getColorForWorkload(section.workload) }">
                {{ section.workload }}%
              </span>
            </div>
            <div class="section-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ 
                    width: `${section.workload}%`,
                    backgroundColor: getColorForWorkload(section.workload)
                  }"
                ></div>
              </div>
              <div class="section-capacity">
                {{ section.currentLoad }} / {{ section.capacity }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Склад -->
      <div class="info-section">
        <h3>{{ workshop.warehouse.name }}</h3>
        <div class="warehouse-info">
          <div class="warehouse-stats">
            <div class="stat">
              <div class="stat-label">{{ $t('workshopdetail.fullness') }}</div>
              <div class="stat-value">
                {{ workshop.warehouse.currentStock }} / {{ workshop.warehouse.capacity }}
              </div>
            </div>
          </div>
          <div class="materials-list">
            <h4>{{ $t('workshopdetail.mat') }}</h4>
            <div v-for="material in workshop.warehouse.materials" :key="material.id" class="material-item">
              <span class="material-name">{{ material.name }}</span>
              <span class="material-quantity">{{ material.quantity }} {{ material.unit }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Оборудование цеха -->
      <div class="info-section">
        <h3>{{ $t('workshopdetail.eq') }} ({{ equipment.length }})</h3>
        <div class="equipment-list">
          <div v-for="item in equipment" :key="item.id" class="equipment-item">
            <div class="equipment-header">
              <div class="equipment-name">{{ item.name }}</div>
              <span class="equipment-status" :class="item.status">
                {{ getStatusText(item.status) }}
              </span>
            </div>
            <div class="equipment-details">
              <div class="detail">Тип: {{ item.type }}</div>
              <div class="detail">Загрузка: {{ item.workload }}%</div>
              <div class="detail">Следующее ТО: {{ formatDate(item.nextService) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Задачи обслуживания -->
      <div v-if="tasks.length > 0" class="info-section">
        <h3>{{ $t('common.task') }}</h3>
        <div class="tasks-list">
          <div v-for="task in tasks" :key="task.id" class="task-item" :class="task.status">
            <div class="task-header">
              <span class="task-equipment">{{ task.equipmentName }}</span>
              <span class="task-type" :class="task.type">{{ getTaskTypeText(task.type) }}</span>
            </div>
            <div class="task-dates">
              {{ formatDate(task.startDate) }} - {{ formatDate(task.endDate) }}
              ({{ task.duration }} дн.)
            </div>
            <div class="task-assigned">Ответственный: {{ task.assignedTo }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  workshop: {
    type: Object,
    default: () => ({})
  },
  equipment: {
    type: Array,
    default: () => []
  },
  tasks: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const getColorForWorkload = (workload) => {
  if (workload >= 80) return '#f44336'
  if (workload >= 60) return '#ff9800'
  if (workload >= 40) return '#4CAF50'
  return '#2196F3'
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

const getTaskTypeText = (type) => {
  const typeMap = {
    scheduled: 'Плановое',
    emergency: 'Аварийное',
    preventive: 'Профилактическое'
  }
  return typeMap[type] || type
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.workshop-detail {
  min-width: 600px;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  background: white;
  border-radius: 12px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.detail-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.btn-close:hover {
  background-color: #f5f5f5;
}

.detail-content {
  padding: 24px;
}

.info-section {
  margin-bottom: 30px;
}

.info-section h3 {
  margin: 0 0 16px 0;
  color: #444;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.info-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-name {
  font-weight: 500;
  color: #333;
}

.section-workload {
  font-weight: bold;
  font-size: 18px;
}

.section-progress {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.section-capacity {
  font-size: 14px;
  color: #666;
  min-width: 80px;
  text-align: right;
}

.warehouse-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.warehouse-stats {
  margin-bottom: 20px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.materials-list h4 {
  margin: 0 0 12px 0;
  color: #444;
}

.material-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.material-item:last-child {
  border-bottom: none;
}

.material-name {
  color: #333;
}

.material-quantity {
  font-weight: 500;
  color: #2196F3;
}

.equipment-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.equipment-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.equipment-item .equipment-status.maintenance {
  border-left-color: #FF9800;
}

.equipment-item .equipment-status.repair {
  border-left-color: #F44336;
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.equipment-name {
  font-weight: 500;
  color: #333;
}

.equipment-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.equipment-status.operational {
  background: #E8F5E9;
  color: #2E7D32;
}

.equipment-status.maintenance {
  background: #FFF3E0;
  color: #EF6C00;
}

.equipment-status.repair {
  background: #FFEBEE;
  color: #D32F2F;
}

.equipment-status.idle {
  background: #F5F5F5;
  color: #616161;
}

.equipment-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.equipment-details .detail {
  color: #666;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.task-item.planned {
  border-left-color: #9E9E9E;
}
/* 
.task-item['in-progress'] {
  border-left-color: #FF9800;
} */

.task-item.completed {
  border-left-color: #4CAF50;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-equipment {
  font-weight: 500;
  color: #333;
}

.task-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.task-type.scheduled {
  background: #E8F5E9;
  color: #2E7D32;
}

.task-type.emergency {
  background: #FFEBEE;
  color: #D32F2F;
}

.task-type.preventive {
  background: #E3F2FD;
  color: #1565C0;
}

.task-dates {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.task-assigned {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .workshop-detail {
    min-width: unset;
    width: 95vw;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .equipment-list {
    grid-template-columns: 1fr;
  }
}
</style>