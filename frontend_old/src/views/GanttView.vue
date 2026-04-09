<template>
  <div class="gantt-view">
    <header class="gantt-header">
      <div class="logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="4" rx="1" />
          <rect x="3" y="10" width="14" height="4" rx="1" />
          <rect x="3" y="16" width="10" height="4" rx="1" />
        </svg>
        <span>{{ $t('app.title') }}</span>
      </div>
      
      <div class="header-controls">
        <!-- Language Selector -->
        <!-- <div class="language-selector">
          <button 
            v-for="lang in languages" 
            :key="lang.code"
            :class="['lang-btn', { active: currentLanguage === lang.code }]"
            @click="changeLanguage(lang.code)"
            :title="lang.name"
          >
            {{ lang.flag }}
          </button>
        </div> -->
        
        <div class="time-scale-selector">
          <button 
            v-for="scale in timeScales" 
            :key="scale.value"
            :class="['scale-btn', { active: currentScale === scale.value }]"
            @click="currentScale = scale.value"
          >
            {{ $t(`scales.${scale.value}`) }}
          </button>
        </div>
        
        <!-- <button class="btn btn-secondary" @click="loadDemoData">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
          {{ $t('app.loadDemo') }}
        </button> -->
        
        <button class="btn btn-primary" @click="openCreateTaskModal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {{ $t('app.addTask') }}
        </button>
      </div>
    </header>
    
    <!--<main class="gantt-main">
      <GanttChart 
        :tasks="tasks" 
        :connections="connections"
        :scale="currentScale"
        :readonly="true"
        @update-task="updateTask"
        @update-task-live="updateTaskLive"
        @delete-task="deleteTask"
        @create-connection="createConnection"
        @delete-connection="deleteConnection"
        @edit-task="editTask"
        @edit-connection="editConnection"
        @change-scale="changeScale"
      />
    </main>-->


    <!-- <main class="gantt-main">
      <GanttChart 
        :tasks="tasks" 
        :connections="connections"
        :scale="currentScale"
        :readonly="true"
        @change-scale="changeScale"
        @create-connection="createConnection"
        @delete-connection="deleteConnection"
        @edit-connection="editConnection"
      />
    </main> -->

    <main class="gantt-main">
      <GanttChart 
        :tasks="tasks" 
        :connections="connections"
        :scale="currentScale"
        :readonly="true"
        @change-scale="changeScale"
        @update-task="updateTask"
        @update-task-live="updateTaskLive"
      />
    </main> 
    
    <!-- Task Modal -->
    <TaskModal
      :show="showTaskModal"
      :editing-task="editingTask"
      :tasks="tasks"
      :connections="connections"
      @close="closeTaskModal"
      @save="saveTask"
      @remove-connection="removeConnection"
    />
    
    <!-- Connection Modal -->
    <ConnectionModal
      :show="showConnectionModal"
      :editing-connection="editingConnection"
      @close="closeConnectionModal"
      @save="saveConnection"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import GanttChart from '../components/GanttChart.vue'
import TaskModal from '../components/TaskModal.vue'
import ConnectionModal from '../components/ConnectionModal.vue'
//import { taskApi, connectionApi, ganttDataApi, reportConnectionApi } from '../api'
import { reportApi, ganttApi, reportConnectionApi, ganttDataApi } from '../api'
import { setLanguage } from '../i18n'

const { t, locale } = useI18n()

// ===================
// State
// ===================
const tasks = ref([])
const connections = ref([])
const currentScale = ref('month')

// Modal state
const showTaskModal = ref(false)
const showConnectionModal = ref(false)
const editingTask = ref(null)
const editingConnection = ref(null)

// ===================
// Language Support
// ===================
const languages = [
  { code: 'ru', name: 'Русский', flag: 'RU' },
  { code: 'en', name: 'English', flag: 'EN' },
  //{ code: 'ar', name: 'العربية', flag: 'AR' }
]

const currentLanguage = computed(() => locale.value)

const changeLanguage = (lang) => {
  setLanguage(lang)
}

// ===================
// Time Scales
// ===================
const timeScales = [
  { value: 'day' },
  { value: 'week' },
  { value: 'month' }
]

const changeScale = (newScale) => {
  currentScale.value = newScale
}

// ===================
// Task Helpers
// ===================

// Map for O(1) task lookup
const tasksMap = computed(() => {
  const map = new Map()
  tasks.value.forEach(t => map.set(t.id, t))
  return map
})

// Calculate parent date span from children
const updateParentDatesFromChildren = (parentId) => {
  const children = tasks.value.filter(t => t.parent_id === parentId)
  if (children.length === 0) return null
  
  let minStart = new Date(children[0].start_date)
  let maxEnd = new Date(children[0].end_date)
  
  children.forEach(child => {
    const start = new Date(child.start_date)
    const end = new Date(child.end_date)
    if (start < minStart) minStart = start
    if (end > maxEnd) maxEnd = end
  })
  
  return {
    start_date: minStart.toISOString(),
    end_date: maxEnd.toISOString()
  }
}

// ===================
// API Operations
// ===================

/*const loadTasks = async () => {
  try {
    const [tasksRes, ganttRes, connectionsRes] = await Promise.all([
      reportApi.getAll(), //было taskApi
      ganttDataApi.getAll(),
      reportConnectionApi.getAll()
    ])
    
    // Если есть данные из report_records, используем их
    // Иначе используем старые tasks
    if (ganttRes.data && ganttRes.data.length > 0) {
      // Преобразуем данные из БД отчётов в формат для Ганта
      tasks.value = ganttRes.data.map((record, index) => ({
        id: record.id,
        title: record.title,
        start_date: parseDate(record.start_date),
        end_date: parseDate(record.end_date),
        progress: record.progress || 0,
        color: '#4A90D9',
        row_index: index,
        parent_id: null
      }))
    } else {
      tasks.value = tasksRes.data
    }
    
    connections.value = connectionsRes.data
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}*/

const loadTasks = async () => {
  try {
    const response = await ganttApi.getAll()
    
    // response.data содержит { tasks: [...], connections: [...] }
    const { tasks: ganttTasks, connections: ganttConnections } = response.data
    
    // Преобразуем даты из формата "ДД.ММ.ГГГГ" в ISO
    tasks.value = ganttTasks.map((record, index) => ({
      id: record.id,
      title: record.title,
      start_date: parseDate(record.start_date),
      end_date: parseDate(record.end_date),
      status: record.status || 'предстоящая',
      color: record.color || '#4A90D9',
      row_index: index,
      parent_id: null,
      // Дополнительные данные из отчёта
      division: record.division,
      factoryNumber: record.factoryNumber,
      repairType: record.repairType,
      responsibleRepair: record.responsibleRepair
    }))
    
    connections.value = ganttConnections
  } catch (error) {
    console.error('Failed to load Gantt data:', error)
  }
}

// Функция для преобразования даты из формата "ДД.ММ.ГГГГ" в ISO
const parseDate = (dateStr) => {
  if (!dateStr) return new Date().toISOString()
  const parts = dateStr.split('.')
  if (parts.length === 3) {
    const [day, month, year] = parts
    return new Date(year, month - 1, day).toISOString()
  }
  return new Date().toISOString()
}

const loadDemoData = async () => {
  try {
    await taskApi.seed()
    await loadTasks()
  } catch (error) {
    console.error('Failed to load demo data:', error)
  }
}

// Live update - only update local state, no server sync
const updateTaskLive = (updates) => {
  const parentsToUpdate = new Set()
  const movedParentIds = new Set()
  
  // First pass: identify which parents are being moved
  updates.forEach(update => {
    const task = tasks.value.find(t => t.id === update.id)
    if (task && !task.parent_id) {
      // This is a root-level task (potential parent)
      const hasChildren = tasks.value.some(t => t.parent_id === task.id)
      if (hasChildren && (update.start_date || update.end_date)) {
        movedParentIds.add(task.id)
      }
    }
  })
  
  // Calculate date deltas for moved parents to apply to children
  const parentDateDeltas = new Map()
  movedParentIds.forEach(parentId => {
    const update = updates.find(u => u.id === parentId)
    const parent = tasks.value.find(t => t.id === parentId)
    if (update && parent && update.start_date) {
      const oldStart = new Date(parent.start_date)
      const newStart = new Date(update.start_date)
      const deltaMs = newStart.getTime() - oldStart.getTime()
      parentDateDeltas.set(parentId, deltaMs)
    }
  })
  
  // Apply updates
  updates.forEach(update => {
    const taskIndex = tasks.value.findIndex(t => t.id === update.id)
    if (taskIndex !== -1) {
      const task = tasks.value[taskIndex]
      // Track parent for date update (only if parent is NOT being moved)
      if (task.parent_id && !movedParentIds.has(task.parent_id)) {
        parentsToUpdate.add(task.parent_id)
      }
      // Merge update into existing task
      tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...update }
    }
  })
  
  // Move children of moved parents
  parentDateDeltas.forEach((deltaMs, parentId) => {
    tasks.value.forEach((task, index) => {
      if (task.parent_id === parentId) {
        const oldStart = new Date(task.start_date)
        const oldEnd = new Date(task.end_date)
        tasks.value[index] = {
          ...task,
          start_date: new Date(oldStart.getTime() + deltaMs).toISOString(),
          end_date: new Date(oldEnd.getTime() + deltaMs).toISOString()
        }
      }
    })
  })
  
  // Update parent dates to span children (only for parents that weren't explicitly moved)
  parentsToUpdate.forEach(parentId => {
    const parentIndex = tasks.value.findIndex(t => t.id === parentId)
    if (parentIndex !== -1) {
      const newDates = updateParentDatesFromChildren(parentId)
      if (newDates) {
        tasks.value[parentIndex] = { ...tasks.value[parentIndex], ...newDates }
      }
    }
  })
}

// Debounce helper for batching server updates
const pendingUpdates = new Map()
let updateDebounceTimer = null

const updateTask = async (task) => {
  // Add to pending updates
  pendingUpdates.set(task.id, { ...pendingUpdates.get(task.id), ...task })
  
  const currentTask = tasks.value.find(t => t.id === task.id)
  
  // If this is a parent task being moved, also add children to pending updates
  const hasChildren = tasks.value.some(t => t.parent_id === task.id)
  if (hasChildren && !currentTask?.parent_id) {
    tasks.value.filter(t => t.parent_id === task.id).forEach(child => {
      pendingUpdates.set(child.id, {
        ...pendingUpdates.get(child.id),
        id: child.id,
        start_date: child.start_date,
        end_date: child.end_date
      })
    })
  }
  
  // Check if this task has a parent and update parent's dates
  if (currentTask?.parent_id) {
    const newDates = updateParentDatesFromChildren(currentTask.parent_id)
    if (newDates) {
      pendingUpdates.set(currentTask.parent_id, { 
        ...pendingUpdates.get(currentTask.parent_id), 
        id: currentTask.parent_id,
        ...newDates 
      })
    }
  }
  
  // Debounce server sync
  if (updateDebounceTimer) {
    clearTimeout(updateDebounceTimer)
  }
  
  updateDebounceTimer = setTimeout(async () => {
    const updates = Array.from(pendingUpdates.values())
    pendingUpdates.clear()
    
    try {
      // Используем ganttDataApi вместо taskApi
      await Promise.all(updates.map(u => ganttDataApi.update(u.id, u)))
    } catch (error) {
      console.error('Failed to update tasks:', error)
      await loadTasks()
    }
  }, 100)
}

const deleteTask = async (taskId) => {
  try {
    await taskApi.delete(taskId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to delete task:', error)
  }
}

// ===================
// Task Modal
// ===================
const openCreateTaskModal = () => {
  editingTask.value = null
  showTaskModal.value = true
}

const editTask = (task) => {
  editingTask.value = task
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  editingTask.value = null
}

/*const saveTask = async (form) => {
  try {
    const data = {
      title: form.title,
      description: form.description,
      start_date: new Date(form.start_date).toISOString(),
      end_date: new Date(form.end_date).toISOString(),
      progress: form.progress,
      color: form.color,
      row_index: form.row_index,
      parent_id: form.parent_id
    }
    
    let savedTask
    if (editingTask.value) {
      const response = await reportApi.update(editingTask.value.id, data) //было TaskApi
      savedTask = response.data
    } else {
      const response = await reportApi.create(data) //было TaskApi
      savedTask = response.data
    }
    
    // Create new parent connection (arrow) if selected
    if (form.conn_parent_task_id) {
      try {
        await reportConnectionApi.create({
          from_task_id: form.conn_parent_task_id,
          to_task_id: savedTask.id,
          arrow_type: form.conn_parent_connection_type,
          arrow_color: form.color
        })
      } catch (e) {
        console.log('Parent connection may already exist')
      }
    }
    
    // Create new child connection (arrow) if selected
    if (form.conn_child_task_id) {
      try {
        await reportConnectionApi.create({
          from_task_id: savedTask.id,
          to_task_id: form.conn_child_task_id,
          arrow_type: form.conn_child_connection_type,
          arrow_color: form.color
        })
      } catch (e) {
        console.log('Child connection may already exist')
      }
    }
    
    await loadTasks()
    closeTaskModal()
  } catch (error) {
    console.error('Failed to save task:', error)
  }
}*/

const saveTask = async (form) => {
  try {
    // Преобразуем даты из ISO в формат ДД.ММ.ГГГГ
    const formatDate = (isoDate) => {
      const d = new Date(isoDate)
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      return `${day}.${month}.${year}`
    }
    
    // Данные для report_records (основная таблица)
    const reportData = {
      nameRETIndex: form.title,           // Название → Наименование РЭТ
      beginRepairDate: formatDate(form.start_date),  // Дата начала
      endRepairDate: formatDate(form.end_date),      // Дата окончания
      status: form.status,                // Статус
      color: form.color,                  // Цвет для Ганта
      division: form.division || '',      // Подразделение
      repairType: form.repairType || '',  // Вид ремонта
      responsibleRepair: form.responsibleRepair || ''  // Ответственный
    }
    
    let savedTask
    if (editingTask.value) {
      // Редактирование существующей записи
      const response = await reportApi.update(editingTask.value.id, reportData)
      savedTask = response.data
    } else {
      // Создание новой записи
      const response = await reportApi.create(reportData)
      savedTask = response.data
    }

  // Create new parent connection (arrow) if selected
    if (form.conn_parent_task_id) {
      try {
        await reportConnectionApi.create({
          from_task_id: form.conn_parent_task_id,
          to_task_id: savedTask.id,
          arrow_type: form.conn_parent_connection_type,
          arrow_color: form.color
        })
      } catch (e) {
        console.log('Parent connection may already exist')
      }
    }
    
    // Create new child connection (arrow) if selected
    if (form.conn_child_task_id) {
      try {
        await reportConnectionApi.create({
          from_task_id: savedTask.id,
          to_task_id: form.conn_child_task_id,
          arrow_type: form.conn_child_connection_type,
          arrow_color: form.color
        })
      } catch (e) {
        console.log('Child connection may already exist')
      }
    }
    
    await loadTasks()
    closeTaskModal()
  } catch (error) {
    console.error('Failed to save task:', error)
  }
}

// ===================
// Connection Operations
// ===================
const createConnection = async (connection) => {
  try {
    await reportConnectionApi.create(connection)
    await loadTasks()
  } catch (error) {
    console.error('Failed to create connection:', error)
  }
}

const deleteConnection = async (connectionId) => {
  try {
    await reportConnectionApi.delete(connectionId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to delete connection:', error)
  }
}

const removeConnection = async (connectionId) => {
  try {
    await reportConnectionApi.delete(connectionId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to remove connection:', error)
  }
}

// ===================
// Connection Modal
// ===================
const editConnection = (connection) => {
  editingConnection.value = connection
  showConnectionModal.value = true
}

const closeConnectionModal = () => {
  showConnectionModal.value = false
  editingConnection.value = null
}

const saveConnection = async (form) => {
  try {
    await reportConnectionApi.update(editingConnection.value.id, form)
    await loadTasks()
    closeConnectionModal()
  } catch (error) {
    console.error('Failed to update connection:', error)
  }
}

// ===================
// Lifecycle
// ===================
onMounted(() => {
  loadTasks()
})

onUnmounted(() => {
  if (updateDebounceTimer) {
    clearTimeout(updateDebounceTimer)
  }
})
</script>

<style scoped>
.gantt-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.gantt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-primary);
}

.logo svg {
  color: var(--accent-primary);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.language-selector {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 2px;
  border: 1px solid var(--border-subtle);
  gap: 2px;
}

.lang-btn {
  padding: 6px 10px;
  border: none;
  background: transparent;
  font-size: 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
}

.lang-btn:hover {
  background: var(--bg-elevated);
}

.lang-btn.active {
  background: var(--accent-primary);
}

.time-scale-selector {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 4px;
  border: 1px solid var(--border-subtle);
}

.scale-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.scale-btn:hover {
  color: var(--text-primary);
}

.scale-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

.gantt-main {
  flex: 1;
  overflow: hidden;
}
</style>
