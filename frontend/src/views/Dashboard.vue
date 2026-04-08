<template>
  <div class="dashboard">
    <!-- Заголовок -->
    <div class="dashboard-header">
      <h1>{{ $t('dashboard.title') }}</h1>
      <div class="header-stats">
        <div class="stat-card">
          <div class="stat-value">{{ workshops.length }}</div>
          <div class="stat-label">{{ $t('dashboard.tcr') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ equipment.length }}</div>
          <div class="stat-label">{{ $t('dashboard.equipmentUnits') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalWorkload.toFixed(1) }}%</div>
          <div class="stat-label">{{ $t('dashboard.averageLoad') }}</div>
        </div>
      </div>
    </div>

    <!-- Навигация -->
    <div class="dashboard-nav">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="nav-tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" class="tab-icon" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Основной контент -->
    <div class="dashboard-content">
      <!-- Диаграммы -->
      <div v-if="activeTab === 'charts'" class="tab-content">
        <WorkshopCharts 
          :workshops="workshops"
          :total-workload="totalWorkload"
          @workshop-select="handleWorkshopSelect"
        />
      </div>

      <!-- Блок-схемы -->
      <div v-if="activeTab === 'blocks'" class="tab-content">
        <WorkshopBlocks 
          :workshops="workshops"
          :equipment="equipment"
          @show-equipment="handleShowEquipment"
          @section-select="handleSectionSelect"
        />
      </div>

      <!-- Таблица оборудования -->
      <div v-if="activeTab === 'table'" class="tab-content">
        <EquipmentTable 
          :equipment="equipment"
          :workshops="workshops"
          @equipment-details="handleEquipmentDetails"
        />
      </div>

      <!-- Диаграмма Ганта -->
      <div v-if="activeTab === 'gantt'" class="tab-content">
        <GanttChart 
          :tasks="maintenanceTasks"
          @task-select="handleTaskSelect"
        />
      </div>
    </div>

    <!-- Детальная информация о цехе -->
    <div v-if="showWorkshopDetail" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <WorkshopDetail 
          :workshop="selectedWorkshop"
          :equipment="selectedWorkshopEquipment"
          :tasks="selectedWorkshopTasks"
          @close="closeModal"
        />
      </div>
    </div>
  </div>
</template>
src\components\dashboard
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDashboardStore } from '../components/dashboard/dashboard'
import WorkshopCharts from '../components/dashboard/WorkshopCharts.vue'
import WorkshopBlocks from '../components/dashboard//WorkshopBlocks.vue'
import EquipmentTable from '../components/dashboard/EquipmentTable.vue'
import GanttChart from '../components/dashboard//GanttChart.vue'
import WorkshopDetail from '../components/dashboard//WorkshopDetail.vue'

// Иконки для табов
import ChartsIcon from '../components/dashboard/icons/ChartsIcon.vue'
import BlocksIcon from '../components/dashboard/icons/BlocksIcon.vue'
import TableIcon from '../components/dashboard/icons/TableIcon.vue'
import GanttIcon from '../components/dashboard/icons/GanttIcon.vue'

// Используем хранилище
const store = useDashboardStore()

// Локальные состояния
const activeTab = ref('charts')
const showWorkshopDetail = ref(false)
const selectedWorkshop = ref(null)
const selectedWorkshopEquipment = ref([])
const selectedWorkshopTasks = ref([])
const { t } = useI18n()

// Табы навигации
const tabs = computed(() =>[
  { id: 'charts', label: t('dashboard.tabs.charts'), icon: ChartsIcon },
  // { id: 'blocks', label: t('dashboard.tabs.blocks'), icon: BlocksIcon },
  { id: 'table', label: t('dashboard.tabs.equipment'), icon: TableIcon },
  { id: 'gantt', label: t('dashboard.tabs.gantt'), icon: GanttIcon }
])

// Получаем данные из хранилища
const workshops = store.workshops
const equipment = store.equipment
const maintenanceTasks = store.maintenanceTasks
const totalWorkload = store.totalWorkload

// Обработчики событий
const handleWorkshopSelect = (workshop) => {
  selectedWorkshop.value = workshop
  selectedWorkshopEquipment.value = store.getWorkshopEquipment(workshop.id)
  selectedWorkshopTasks.value = store.getWorkshopTasks(workshop.id)
  showWorkshopDetail.value = true
}

const handleShowEquipment = (workshopId) => {
  // Переключаемся на вкладку таблицы
  activeTab.value = 'table'
  // Здесь можно добавить фильтрацию оборудования по цеху
  console.log('Показать оборудование цеха:', workshopId)
}

const handleSectionSelect = (section) => {
  console.log('Выбран участок:', section)
  // Можно открыть детали участка или выделить его на других диаграммах
}

const handleEquipmentDetails = (equipment) => {
  console.log('Детали оборудования:', equipment)
  // Здесь можно открыть модалку с деталями оборудования
}

const handleTaskSelect = (task) => {
  console.log('Выбрана задача:', task)
  // Здесь можно открыть модалку с деталями задачи
}

const closeModal = () => {
  showWorkshopDetail.value = false
  selectedWorkshop.value = null
}

// Инициализация при монтировании
onMounted(() => {
  console.log('Дашборд загружен')
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 32px;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-width: 150px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

/* Навигация */
.dashboard-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  padding: 10px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background: none;
  border: none;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-tab:hover {
  background: #f8f9fa;
  color: #333;
}

.nav-tab.active {
  background: #4CAF50;
  color: white;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.tab-icon {
  width: 20px;
  height: 20px;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
}

@media (max-width: 768px) {
  .header-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-card {
    min-width: unset;
  }
  
  .dashboard-nav {
    flex-direction: column;
  }
  
  .nav-tab {
    padding: 10px;
    font-size: 13px;
  }
}
</style>