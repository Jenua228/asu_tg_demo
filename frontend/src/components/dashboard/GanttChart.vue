<template>
  <div class="gantt-container">
    <div class="gantt-header">
      <h2>{{ $t('sched.shed') }}</h2>
      <div class="date-range">
        {{ formatDate(rangeStart) }} - {{ formatDate(rangeEnd) }}
      </div>
    </div>

    <div class="gantt-content">
      <div class="timeline">
        <div class="timeline-header">
          <div class="timeline-cell"></div>
          <div 
            v-for="date in timelineDates" 
            :key="date.getTime()"
            class="timeline-cell"
            :class="{ 'weekend': isWeekend(date) }"
          >
            <div class="date-day">{{ formatDay(date) }}</div>
            <div class="date-number">{{ date.getDate() }}</div>
          </div>
        </div>

        <div class="gantt-body">
          <div 
            v-for="task in tasks" 
            :key="task.id"
            class="task-row"
          >
            <div class="task-info">
              <div class="task-name">{{ task.equipmentName }}</div>
              <div class="task-details">
                <span class="task-type" :class="task.type">{{ getTaskTypeText(task.type) }}</span>
                <span class="task-assigned">{{ task.assignedTo }}</span>
              </div>
            </div>
            
            <div class="task-timeline">
              <div 
                class="task-bar"
                :style="getTaskStyle(task)"
                :class="[task.status, task.type]"
                @click="$emit('task-select', task)"
                @mouseenter="hoveredTask = task"
                @mouseleave="hoveredTask = null"
              >
                <div class="task-duration">{{ task.duration }} {{ $t('sched.dn') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="hoveredTask" class="task-tooltip">
      <h4>{{ hoveredTask.equipmentName }}</h4>
      <div class="tooltip-info">
        <div><strong>{{ $t('connectionPopup.type') }}</strong> {{ getTaskTypeText(hoveredTask.type) }}</div>
        <div><strong>{{ $t('sched.status') }}</strong> {{ getStatusText(hoveredTask.status) }}</div>
        <div><strong>{{ $t('sched.start') }}</strong> {{ formatDate(hoveredTask.startDate) }}</div>
        <div><strong>{{ $t('sched.end') }}</strong> {{ formatDate(hoveredTask.endDate) }}</div>
        <div><strong>{{ $t('sched.otv') }}</strong> {{ hoveredTask.assignedTo }}</div>
      </div>
    </div>

    <div class="gantt-legend">
      <div class="legend-title">{{ $t('sched.leg') }}</div>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-color scheduled"></div>
          <span>{{ $t('sched.plan') }}</span>
        </div>
        <div class="legend-item">
          <div class="legend-color emergency"></div>
          <span>{{ $t('sched.emer') }}</span>
        </div>
        <div class="legend-item">
          <div class="legend-color preventive"></div>
          <span>{{ $t('sched.prof') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['task-select'])

const hoveredTask = ref(null)

// Определяем диапазон дат
const rangeStart = computed(() => {
  if (props.tasks.length === 0) return new Date()
  const dates = props.tasks.map(t => new Date(t.startDate))
  return new Date(Math.min(...dates.map(d => d.getTime())))
})

const rangeEnd = computed(() => {
  if (props.tasks.length === 0) return new Date()
  const dates = props.tasks.map(t => new Date(t.endDate))
  return new Date(Math.max(...dates.map(d => d.getTime())))
})

// Генерируем даты для таймлайна
const timelineDates = computed(() => {
  const dates = []
  const current = new Date(rangeStart.value)
  const end = new Date(rangeEnd.value)
  
  while (current <= end) {
    dates.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }
  
  return dates
})

// Методы
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('ru-RU')
}

const formatDay = (date) => {
  const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
  return days[date.getDay()]
}

const isWeekend = (date) => {
  const day = date.getDay()
  return day === 0 || day === 6
}

const getTaskTypeText = (type) => {
  const types = {
    scheduled: 'Плановое',
    emergency: 'Аварийное',
    preventive: 'Профилактическое'
  }
  return types[type] || type
}

const getStatusText = (status) => {
  const statuses = {
    planned: 'Запланировано',
    'in-progress': 'В процессе',
    completed: 'Завершено',
    delayed: 'Отложено'
  }
  return statuses[status] || status
}

const getTaskStyle = (task) => {
  const startDate = new Date(task.startDate)
  const endDate = new Date(task.endDate)
  const totalDays = (rangeEnd.value - rangeStart.value) / (1000 * 60 * 60 * 24) + 1
  const taskStart = (startDate - rangeStart.value) / (1000 * 60 * 60 * 24)
  const taskDuration = task.duration
  
  const cellWidth = 40
  const left = (taskStart / totalDays) * 100 + '%'
  const width = ((taskDuration * cellWidth) / (totalDays * cellWidth)) * 100 + '%'
  
  return {
    left: left,
    width: width
  }
}

const getTaskColor = (type) => {
  const colors = {
    scheduled: '#4CAF50',
    emergency: '#F44336',
    preventive: '#2196F3'
  }
  return colors[type] || '#9E9E9E'
}
</script>

<style scoped>
.gantt-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.gantt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.gantt-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.date-range {
  background: #f8f9fa;
  padding: 8px 16px;
  border-radius: 6px;
  color: #666;
  font-weight: 500;
}

.gantt-content {
  overflow-x: auto;
  margin-bottom: 20px;
}

.timeline {
  min-width: 800px;
}

.timeline-header {
  display: flex;
  border-bottom: 2px solid #e9ecef;
  background: #f8f9fa;
}

.timeline-cell {
  width: 40px;
  padding: 8px 4px;
  text-align: center;
  border-right: 1px solid #e9ecef;
}

.timeline-cell:first-child {
  width: 200px;
  text-align: left;
  padding-left: 16px;
}

.timeline-cell.weekend {
  background: #fff5f5;
}

.date-day {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
}

.date-number {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.gantt-body {
  border: 1px solid #e9ecef;
  border-top: none;
}

.task-row {
  display: flex;
  height: 60px;
  border-bottom: 1px solid #e9ecef;
}

.task-row:last-child {
  border-bottom: none;
}

.task-info {
  width: 200px;
  padding: 12px 16px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.task-details {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.task-type {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
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

.task-assigned {
  color: #666;
}

.task-timeline {
  flex: 1;
  position: relative;
  background: #fafafa;
}

.task-bar {
  position: absolute;
  height: 36px;
  margin-top: 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.task-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.task-bar.scheduled {
  background: #4CAF50;
}

.task-bar.emergency {
  background: #F44336;
}

.task-bar.preventive {
  background: #2196F3;
}

.task-bar.planned {
  opacity: 0.7;
}

/* .task-bar['in-progress'] {
  border: 2px dashed white;
} */

.task-duration {
  color: white;
  font-size: 12px;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.task-tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  max-width: 300px;
}

.task-tooltip h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.tooltip-info div {
  margin-bottom: 4px;
  font-size: 14px;
}

.tooltip-info strong {
  color: #666;
}

.gantt-legend {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.legend-title {
  font-weight: 500;
  color: #666;
}

.legend-items {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.scheduled {
  background: #4CAF50;
}

.legend-color.emergency {
  background: #F44336;
}

.legend-color.preventive {
  background: #2196F3;
}
</style>