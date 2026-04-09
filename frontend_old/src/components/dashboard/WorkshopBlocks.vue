<template>
  <div class="workshop-blocks-container">
    <div class="section-header">
      <h2>{{ $t('blockDiag.block') }}</h2>
      <div class="view-controls">
        <button 
          class="btn-view" 
          :class="{ active: viewMode === 'grid' }"
          @click="viewMode = 'grid'"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <rect x="2" y="2" width="6" height="6" rx="1"/>
            <rect x="12" y="2" width="6" height="6" rx="1"/>
            <rect x="2" y="12" width="6" height="6" rx="1"/>
            <rect x="12" y="12" width="6" height="6" rx="1"/>
          </svg>
          {{ $t('blockDiag.grid') }}
        </button>
        <button 
          class="btn-view" 
          :class="{ active: viewMode === 'list' }"
          @click="viewMode = 'list'"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <rect x="2" y="3" width="16" height="2" rx="1"/>
            <rect x="2" y="9" width="16" height="2" rx="1"/>
            <rect x="2" y="15" width="16" height="2" rx="1"/>
          </svg>
          {{ $t('blockDiag.list') }}
        </button>
      </div>
    </div>

    <!-- Сеточный вид -->
    <div v-if="viewMode === 'grid'" class="workshop-grid">
      <div 
        v-for="workshop in workshops" 
        :key="workshop.id"
        class="workshop-block"
        :class="{ expanded: expandedWorkshop === workshop.id }"
        :style="{ borderColor: workshop.color }"
      >
        <!-- Заголовок цеха -->
        <div 
          class="workshop-header"
          :style="{ backgroundColor: workshop.color }"
          @click="toggleWorkshop(workshop.id)"
        >
          <div class="workshop-title">
            <h2>ТЦР № {{ workshop.id }}</h2>
            <h3>{{ workshop.name }}</h3>
            <div class="workshop-stats">
              <span class="stat-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                  <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/>
                </svg>
                {{ workshop.workload }}%
              </span>
              <span class="stat-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                </svg>
                {{ workshop.sections.length }}
              </span>
              <span class="stat-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
                </svg>
                {{ workshop.warehouse.currentStock }}/{{ workshop.warehouse.capacity }}
              </span>
            </div>
          </div>
          <div class="workshop-toggle">
            <svg 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="currentColor"
              :class="{ rotated: expandedWorkshop === workshop.id }"
            >
              <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
            </svg>
          </div>
        </div>

        <!-- Содержимое (участки) -->
        <div v-if="expandedWorkshop === workshop.id" class="workshop-content">
          <!-- Диаграмма загрузки -->
          <div class="workload-chart">
            <div class="chart-title">{{$t('blockDiag.load')}}</div>
            <div class="chart-bars">
              <div 
                v-for="section in workshop.sections" 
                :key="section.id"
                class="chart-bar-container"
                @click="selectSection(section)"
              >
                <div class="bar-label">{{ section.name }}</div>
                <div class="bar-wrapper">
                  <div 
                    class="bar-fill"
                    :style="{
                      width: `${section.workload}%`,
                      backgroundColor: getColorForWorkload(section.workload)
                    }"
                  ></div>
                  <div class="bar-value">{{ section.workload }}%</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Участки цеха -->
          <div class="sections-container">
            <h4>{{$t('workshopdetail.workReg')}}</h4>
            <div class="sections-grid">
              <div 
                v-for="section in workshop.sections" 
                :key="section.id"
                class="section-block"
                :class="{ active: selectedSection?.id === section.id }"
                @click="selectSection(section)"
              >
                <div class="section-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
                    <path d="M7 12h10v2H7zm0-4h10v2H7z"/>
                  </svg>
                </div>
                <div class="section-info">
                  <div class="section-name">{{ section.name }}</div>
                  <div class="section-details">
                    <span class="detail-item">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                      </svg>
                      {{ section.workload }}%
                    </span>
                    <span class="detail-item">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                      </svg>
                      {{ section.currentLoad }}/{{ section.capacity }}
                    </span>
                  </div>
                </div>
                <div class="section-arrow">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Склад -->
          <div class="warehouse-container">
            <div class="warehouse-header">
              <h4>{{ workshop.warehouse.name }}</h4>
              <div class="warehouse-fill">
                <div class="fill-bar">
                  <div 
                    class="fill-progress"
                    :style="{
                      width: `${(workshop.warehouse.currentStock / workshop.warehouse.capacity) * 100}%`,
                      backgroundColor: workshop.color
                    }"
                  ></div>
                </div>
                <span class="fill-percentage">
                  {{ Math.round((workshop.warehouse.currentStock / workshop.warehouse.capacity) * 100) }}%
                </span>
              </div>
            </div>
            <div class="materials-list">
              <div v-for="material in workshop.warehouse.materials" :key="material.id" class="material-item">
                <div class="material-name">{{ material.name }}</div>
                <div class="material-quantity">{{ material.quantity }} {{ material.unit }}</div>
                <div class="material-bar">
                  <div 
                    class="material-fill"
                    :style="{
                      width: `${(material.quantity / 1000) * 100}%`,
                      backgroundColor: workshop.color
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Оборудование -->
          <div class="equipment-preview">
            <div class="preview-header">
              <h4>{{ $t('workshopdetail.eq') }} ({{ getWorkshopEquipment(workshop.id).length }})</h4>
              <button class="btn-view-all" @click="$emit('show-equipment', workshop.id)">
                {{ $t('blockDiag.showAll') }}
              </button>
            </div>
            <div class="equipment-cards">
              <div 
                v-for="eq in getWorkshopEquipment(workshop.id).slice(0, 3)" 
                :key="eq.id"
                class="equipment-card"
                :class="eq.status"
              >
                <div class="card-header">
                  <div class="card-title">{{ eq.name }}</div>
                  <div class="card-status" :class="eq.status">{{ getStatusText(eq.status) }}</div>
                </div>
                <div class="card-details">
                  <div class="detail">Тип: {{ eq.type }}</div>
                  <div class="detail">Загрузка: {{ eq.workload }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Списковый вид -->
    <div v-else class="workshop-list">
      <div 
        v-for="workshop in workshops" 
        :key="workshop.id"
        class="workshop-list-item"
        :class="{ expanded: expandedWorkshop === workshop.id }"
        @click="toggleWorkshop(workshop.id)"
      >
        <div class="list-item-header" :style="{ borderLeftColor: workshop.color }">
          <div class="list-item-title">
            <h3>{{ workshop.name }}</h3>
            <div class="list-item-stats">
              <span class="stat">
                <span class="stat-label">Загрузка:</span>
                <span class="stat-value" :style="{ color: getColorForWorkload(workshop.workload) }">
                  {{ workshop.workload }}%
                </span>
              </span>
              <span class="stat">
                <span class="stat-label">Участков:</span>
                <span class="stat-value">{{ workshop.sections.length }}</span>
              </span>
              <span class="stat">
                <span class="stat-label">Оборудования:</span>
                <span class="stat-value">{{ getWorkshopEquipment(workshop.id).length }}</span>
              </span>
            </div>
          </div>
          <div class="list-item-toggle">
            <svg 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="currentColor"
              :class="{ rotated: expandedWorkshop === workshop.id }"
            >
              <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
            </svg>
          </div>
        </div>

        <div v-if="expandedWorkshop === workshop.id" class="list-item-content">
          <div class="sections-list-compact">
            <div 
              v-for="section in workshop.sections" 
              :key="section.id"
              class="section-list-item"
              @click.stop="selectSection(section)"
            >
              <div class="section-list-icon" :style="{ color: workshop.color }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                  <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/>
                </svg>
              </div>
              <div class="section-list-info">
                <div class="section-list-name">{{ section.name }}</div>
                <div class="section-list-stats">
                  <span class="stat">Загрузка: {{ section.workload }}%</span>
                  <span class="stat">Мощность: {{ section.currentLoad }}/{{ section.capacity }}</span>
                </div>
              </div>
              <div class="section-list-arrow">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно с деталями участка -->
    <div v-if="showSectionDetail" class="modal-overlay" @click="closeSectionDetail">
      <div class="modal-content section-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedSection?.name }}</h3>
          <button class="btn-close-modal" @click="closeSectionDetail">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedSection" class="section-detail-content">
            <div class="detail-section">
              <h4>Основная информация</h4>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">Загрузка</div>
                  <div class="info-value" :style="{ color: getColorForWorkload(selectedSection.workload) }">
                    {{ selectedSection.workload }}%
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Текущая нагрузка</div>
                  <div class="info-value">{{ selectedSection.currentLoad }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Мощность</div>
                  <div class="info-value">{{ selectedSection.capacity }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Использование</div>
                  <div class="info-value">
                    {{ Math.round((selectedSection.currentLoad / selectedSection.capacity) * 100) }}%
                  </div>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Оборудование участка</h4>
              <div class="equipment-list">
                <div 
                  v-for="eq in getSectionEquipment(selectedSection.id)" 
                  :key="eq.id"
                  class="equipment-detail-item"
                >
                  <div class="equipment-detail-header">
                    <div class="equipment-name">{{ eq.name }}</div>
                    <div class="equipment-status" :class="eq.status">
                      {{ getStatusText(eq.status) }}
                    </div>
                  </div>
                  <div class="equipment-details">
                    <div class="detail">Тип: {{ eq.type }}</div>
                    <div class="detail">Загрузка: {{ eq.workload }}%</div>
                    <div class="detail">Следующее ТО: {{ formatDate(eq.nextService) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  workshops: {
    type: Array,
    default: () => []
  },
  equipment: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-equipment', 'section-select'])

// Локальные состояния
const viewMode = ref('grid')
const expandedWorkshop = ref(null)
const selectedSection = ref(null)
const showSectionDetail = ref(false)

// Методы
const toggleWorkshop = (workshopId) => {
  if (expandedWorkshop.value === workshopId) {
    expandedWorkshop.value = null
  } else {
    expandedWorkshop.value = workshopId
  }
}

const selectSection = (section) => {
  selectedSection.value = section
  showSectionDetail.value = true
  emit('section-select', section)
}

const closeSectionDetail = () => {
  showSectionDetail.value = false
  selectedSection.value = null
}

const getColorForWorkload = (workload) => {
  if (workload >= 80) return '#f44336'
  if (workload >= 60) return '#ff9800'
  if (workload >= 40) return '#4CAF50'
  return '#2196F3'
}

const getWorkshopEquipment = (workshopId) => {
  return props.equipment.filter(eq => eq.workshopId === workshopId)
}

const getSectionEquipment = (sectionId) => {
  return props.equipment.filter(eq => eq.sectionId === sectionId)
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

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.workshop-blocks-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.view-controls {
  display: flex;
  gap: 8px;
}

.btn-view {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #e9ecef;
  border-color: #ddd;
}

.btn-view.active {
  background: #4CAF50;
  border-color: #4CAF50;
  color: white;
}

/* Сеточный вид */
.workshop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.workshop-block {
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s;
  background: white;
}

.workshop-block.expanded {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.workshop-header {
  padding: 16px 20px;
  color: white;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.3s;
}

.workshop-header:hover {
  filter: brightness(1.1);
}

.workshop-title {
  flex: 1;
}

.workshop-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.workshop-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  opacity: 0.9;
}

.workshop-toggle {
  transition: transform 0.3s;
}

.workshop-toggle svg.rotated {
  transform: rotate(180deg);
}

/* Содержимое цеха */
.workshop-content {
  padding: 20px;
  background: linear-gradient(to bottom, #fafafa, #f0f0f0);
}

.workload-chart {
  margin-bottom: 24px;
}

.chart-title {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin-bottom: 12px;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-bar-container {
  cursor: pointer;
  transition: transform 0.2s;
}

.chart-bar-container:hover {
  transform: translateX(4px);
}

.bar-label {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
}

.bar-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-fill {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar-value {
  width: 40px;
  text-align: right;
  font-size: 12px;
  font-weight: 500;
  color: #666;
}

/* Участки */
.sections-container {
  margin-bottom: 24px;
}

.sections-container h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.sections-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-block {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.section-block:hover {
  border-color: #4CAF50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
}

.section-block.active {
  border-color: #4CAF50;
  background: #f8fff8;
}

.section-icon {
  color: #4CAF50;
}

.section-info {
  flex: 1;
}

.section-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.section-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.section-arrow {
  color: #999;
}

/* Склад */
.warehouse-container {
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.warehouse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.warehouse-header h4 {
  margin: 0;
  color: #333;
}

.warehouse-fill {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fill-bar {
  width: 100px;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.fill-progress {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.fill-percentage {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.materials-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.material-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.material-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.material-quantity {
  width: 80px;
  text-align: right;
  font-size: 14px;
  font-weight: 500;
  color: #4CAF50;
}

.material-bar {
  width: 60px;
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.material-fill {
  height: 100%;
  border-radius: 2px;
}

/* Оборудование */
.equipment-preview {
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-header h4 {
  margin: 0;
  color: #333;
}

.btn-view-all {
  padding: 6px 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-view-all:hover {
  background: #45a049;
}

.equipment-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.equipment-card {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #4CAF50;
}

.equipment-card.maintenance {
  border-left-color: #FF9800;
}

.equipment-card.repair {
  border-left-color: #F44336;
}

.equipment-card.idle {
  border-left-color: #9E9E9E;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.card-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
}

.card-status.operational {
  background: #E8F5E9;
  color: #2E7D32;
}

.card-status.maintenance {
  background: #FFF3E0;
  color: #EF6C00;
}

.card-status.repair {
  background: #FFEBEE;
  color: #D32F2F;
}

.card-status.idle {
  background: #F5F5F5;
  color: #616161;
}

.card-details {
  font-size: 11px;
  color: #666;
}

.card-details .detail {
  margin-bottom: 2px;
}

/* Списковый вид */
.workshop-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.workshop-list-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.workshop-list-item:hover {
  border-color: #4CAF50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
}

.workshop-list-item.expanded {
  border-color: #4CAF50;
}

.list-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-left: 4px solid #4CAF50;
}

.list-item-title {
  flex: 1;
}

.list-item-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.list-item-stats {
  display: flex;
  gap: 20px;
}

.stat {
  display: flex;
  gap: 4px;
  font-size: 14px;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 500;
  color: #333;
}

.list-item-toggle svg.rotated {
  transform: rotate(180deg);
}

.list-item-content {
  padding: 20px;
  background: #fafafa;
  border-top: 1px solid #e0e0e0;
}

.sections-list-compact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.section-list-item:hover {
  border-color: #4CAF50;
  transform: translateX(4px);
}

.section-list-info {
  flex: 1;
}

.section-list-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.section-list-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.section-detail-modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 24px;
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

.btn-close-modal:hover {
  background-color: #f5f5f5;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #444;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.info-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
}

.info-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.equipment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.equipment-detail-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #4CAF50;
}

.equipment-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
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

.equipment-details {
  font-size: 12px;
  color: #666;
}

.equipment-details .detail {
  margin-bottom: 2px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .workshop-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .view-controls {
    width: 100%;
  }
  
  .btn-view {
    flex: 1;
    justify-content: center;
  }
  
  .workshop-stats {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .list-item-stats {
    flex-direction: column;
    gap: 4px;
  }
  
  .section-detail-modal {
    width: 95vw;
    margin: 10px;
  }
}
</style>