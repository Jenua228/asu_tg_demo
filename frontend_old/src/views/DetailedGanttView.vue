<template>
  <div class="detailed-gantt-view" v-show="isShow">
    <!-- Заголовок с информацией о родительской записи -->
    <header class="detail-header">
      <button class="btn-back" @click="goBack">
        {{ $t('detail.backToReports') }}
      </button>
      <div class="parent-info" v-if="parentReport">
        <h2>{{ parentReport.nameRETIndex }}</h2>
        <span class="serial">{{ $t('detail.serialNumber') }} {{ parentReport.factoryNumber }}</span>
        
      </div>
      <span class="people-sum">{{ $t('detail.totalPeople') }} {{ totalPeople }}</span>
      <span class="total-days">{{ $t('detail.totalDays') }} {{ totalDays }}</span>
      <button 
        class="btn-warehouse" 
        :disabled="!selectedStageId"
        @click="goToWarehouse"
      >
        {{ $t('detail.goToWarehouse') }}
      </button>
    </header>

    <!-- Toolbar -->
    <div class="toolbar">
      <button class="btn-add" @click="addNewStage">{{ $t('detail.add') }}</button>
      <button class="btn-delete" @click="deleteSelectedStage" :disabled="!selectedStageId">
        {{ $t('detail.delete') }}
      </button>
      <button class="btn-edit" @click="toggleEditMode" :disabled="!selectedStageId">
        {{ isEditing ? $t('detail.save') : $t('detail.edit') }}
      </button>

      <button 
        class="btn-pdf" 
        :class="{ 'btn-pdf-active': selectedStageId }" 
        :disabled="!selectedStageId" 
        @click="openAttachModal"
      >
        {{ $t('detail.attachDocument') }}
      </button>
      <button 
        class="btn-pdf" 
        :class="{ 'btn-pdf-active': selectedPdfUrl }" 
        :disabled="!selectedPdfUrl" 
        @click="isPdfModalOpen = true"
      >
        {{ $t('detail.showDocument') }}
      </button>
    </div>
    
    <!-- Таблица этапов -->
    <div class="stages-table" :style="{ height: tableHeight + 'px' }">
      <ag-grid-vue
        class="ag-theme-alpine"
        style="width: 100%; height: 100%;"
        :columnDefs="columnDefs"
        :rowData="stages"
        :defaultColDef="defaultColDef"
        rowSelection="single"
        :localeText="localeRu"
        :rowDeselection="true"
        :rowMultiSelectWithClick="true"
        
        @selection-changed="onSelectionChanged"
        @cell-value-changed="onCellChanged"
        @grid-ready="onGridReady"
        
      />
    </div>

    <!-- Разделитель для изменения размера -->
    <div class="resize-divider" @mousedown="startResize">
        <div class="resize-handle">⋯</div>
        <button class="resize-btn" @click="expandGantt">▲</button>
        <button class="resize-btn" @click="collapseGantt">▼</button>
    </div>
    
    <!-- Диаграмма Ганта по этапам -->
    <div class="stages-gantt">
      <GanttChart 
        ref="ganttChartRef"
        :tasks="ganttTasks" 
        :connections="ganttConnections"
        :selectedTaskId="selectedStageId"
        :hideExpandButton="true"
        scale="day"
        :readonly="false"
        @create-connection="handleCreateConnection"
        @delete-connection="handleDeleteConnection"
        @task-selected="onGanttTaskSelected"
        @focus-table="focusTable"
        @update-task="handleUpdateTask"
        @update-task-live="handleUpdateTaskLive"
      />
    </div>
  </div>
  <div v-show="!isShow">
      <Store />
  </div>

  <PdfModal 
  v-model="isPdfModalOpen" 
  :pdfUrl="selectedPdfUrl"
  :isEditMode="isEditPdfMode"
  @update-pdf="handleAttachPdf"
  @update:modelValue="(val) => { if(!val) isEditPdfMode = false }" 
/>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import GanttChart from '../components/GanttChart.vue'
import { repairDetailApi } from '../api'
import Store from './Store.vue'
import PdfModal from '../components/store/PdfModal.vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const isShow = ref(true)

// Русская локализация фильтров
const localeRu = {
  // Фильтры
  contains: t('agGrid.contains'),
  notContains: t('agGrid.notContains'),
  equals: t('agGrid.equals'),
  notEqual: t('agGrid.notEqual'),
  startsWith: t('agGrid.startsWith'),
  endsWith: t('agGrid.endsWith'),
  blank: t('agGrid.blank'),
  notBlank: t('agGrid.notBlank'),
  
  // Числовые фильтры
  lessThan: t('agGrid.lessThan'),
  greaterThan: t('agGrid.greaterThan'),
  lessThanOrEqual: t('agGrid.lessThanOrEqual'),
  greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
  inRange: t('agGrid.inRange'),
  
  // Условия
  andCondition: t('agGrid.andCondition'),
  orCondition: t('agGrid.orCondition'),
  
  // Панель фильтров
  filterOoo: t('agGrid.filterOoo'),
  applyFilter: t('agGrid.applyFilter'),
  resetFilter: t('agGrid.resetFilter'),
  clearFilter: t('agGrid.clearFilter'),
  
  // Прочее
  noRowsToShow: t('agGrid.noRowsToShow'),
    loading: t('agGrid.loading')
}

const props = defineProps({
  reportId: { type: Number, required: true },
  //tasks: { type: Array, default: () => [] }
})

const emit = defineEmits(['back'])

const parentReport = ref(null)
const stages = ref([])
const localConnections = ref([])
const gridApi = ref(null)
const selectedStageId = ref(null)
const ganttChartRef = ref(null)
const selectedPdfUrl = ref(null)
const isPdfModalOpen = ref(false)
const isEditPdfMode = ref(false)

const focusTable = () => {
  // Найди элемент таблицы и вызови focus()
  const gridEl = document.querySelector('.ag-theme-alpine .ag-root');
  if (gridEl) gridEl.focus();
};



// Определения колонок
const columnDefs =  [
  //{ field: 'productName', headerName: 'Название изделия', width: 200, editable: false, filter: 'agTextColumnFilter', cellStyle: { fontWeight: 'bold' } },
  //{ field: 'serialNumber', headerName: 'Серийный номер', width: 120, editable: false, filter: 'agTextColumnFilter',cellStyle: { fontWeight: 'bold' } },
  { field: 'stageName', headerName: t('detail.columns.stageName'), width: 130, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter'},
  { field: 'division', headerName: t('detail.columns.division'), width: 100, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'plannedStartDate', headerName: t('detail.columns.plannedStartDate'), width: 110, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'startDate', headerName: t('detail.columns.startDate'), width: 110, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'plannedEndDate', headerName: t('detail.columns.plannedEndDate'), width: 110, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'endDate', headerName: t('detail.columns.endDate'), width: 110, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { 
  field: 'status', 
  headerName: t('detail.columns.status'), 
  width: 120, 
  editable: true,
  cellEditor: 'agSelectCellEditor',
  filter: 'agTextColumnFilter',
  cellEditorParams: {
    values: ['предстоящая', 'в работе', 'выполнено', 'просрочено']
  },
  cellRenderer: (params) => {
    if (!params.value) return ''
    const color = getStatusColor(params.value)
    return `<span style="
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      background-color: ${color}30;
      color: ${color};
      font-weight: bold;
      font-size: 11px;
    ">${params.value}</span>`
  }
  // cellStyle: (params) => {
  //   const color = getStatusColor(params.value)
  //   return { 
  //     backgroundColor: color + '30',  // 30 = прозрачность 20%
  //     color: color,
  //     fontWeight: 'bold'
  //   }
  // }
},
  { field: 'plannedHours', headerName: t('detail.columns.plannedHours'), width: 110, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'spentHours', headerName: t('detail.columns.spentHours'), width: 100, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter'},
  //{ field: 'predecessor', headerName: 'Предыдущая', width: 200, editable: true, filter: 'agTextColumnFilter' },
  //{ field: 'parentName', headerName: 'Родительская', width: 150, editable: false, filter: 'agTextColumnFilter', cellStyle: { fontWeight: 'bold' } },
  { field: 'responsible', headerName: t('detail.columns.responsible'), width: 130, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'visualSigns', headerName: t('detail.columns.visualSigns'), width: 100, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'peopleCount', headerName: t('detail.columns.peopleCount'), width: 80, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
  { field: 'usedZip', headerName: t('detail.columns.usedZip'), width: 105, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value },
  { field: 'comment', headerName: t('detail.columns.comment'), width: 150, editable: (params) => isEditing.value && params.data?.id === selectedStageId.value, filter: 'agTextColumnFilter' },
{ 
  field: "pdfUrl",
  headerName: t('detail.columns.document'),
  width: 100,
  cellClass: 'grid-cell-centered',
  cellRenderer: params => {
    const hasPdf = params.value && params.value.trim().length > 0;
    return hasPdf 
      ? `<span title="Документ прикреплен" style="color: #059669; font-size: 1.2rem;">📄</span>` 
      : `<span title="Нет документа" style="color: #94a3b8; opacity: 0.5;">—</span>`;
  }
}
]

const defaultColDef = {
  resizable: true,
  sortable: false,           // Отключаем сортировку!
  filter: true,
  floatingFilter: true,      // Показываем фильтры под заголовками
  wrapText: true,
  autoHeight: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
}

// Преобразование этапов для диаграммы Ганта
const ganttTasks = computed(() => {
  return stages.value.map((stage, index) => ({
    id: stage.id,
    title: stage.stageName,
    start_date: stage.startDate ? parseDate(stage.startDate) : null,
    end_date: stage.endDate ? parseDate(stage.endDate) : null,
    status: stage.status,
    color: getStatusColor(stage.status),
    row_index: index
  })).filter(t => t.start_date && t.end_date)
})


const isEditing = ref(false)

// Функция добавления новой строки
const addNewStage = async () => {
  try {
    const response = await repairDetailApi.create(props.reportId, {
      stageName: 'Новый этап',
      division: '',
      status: 'предстоящая'
    })
    stages.value.push(response.data)
    // Обновить таблицу
    await loadData()
  } catch (error) {
    console.error('Ошибка добавления:', error)
    alert(t('detail.addError'))
  }
}

// Функция удаления выбранной строки
const deleteSelectedStage = async () => {
  if (!selectedStageId.value) return
  
  if (!confirm(t('detail.del'))) return
  
  try {
    await repairDetailApi.delete(selectedStageId.value)
    // Обновить данные
    await loadData()
    selectedStageId.value = null
  } catch (error) {
    console.error('Ошибка удаления:', error)
    alert(t('detail.delError'))
  }
}

// Переключение режима редактирования
// const toggleEditMode = () => {
//   isEditing.value = !isEditing.value
//   gridApi.value?.refreshCells({ force: true })
// }

const toggleEditMode = () => {
  if (isEditing.value) {
    // Выходим из режима редактирования
    isEditing.value = false
  } else {
    // Входим в режим редактирования — запоминаем ID редактируемой строки
    isEditing.value = true
  }
  gridApi.value?.refreshCells({ force: true })
}


const totalDays = computed(() => {
  const starts = stages.value.map(s => s.startDate).filter(Boolean).map(d => parseDate(d))
  const ends = stages.value.map(s => s.endDate).filter(Boolean).map(d => parseDate(d))
  if (!starts.length || !ends.length) return 0

  const minStart = new Date(Math.min(...starts.map(d => new Date(d).getTime())))
  const maxEnd = new Date(Math.max(...ends.map(d => new Date(d).getTime())))

  return Math.floor((maxEnd - minStart) / (1000 * 60 * 60 * 24)) + 1
})






// Связи для Ганта (последовательные этапы)
const ganttConnections = computed(() => {
    return localConnections.value
})

// Хелперы
const parseDate = (dateStr) => {
  if (!dateStr) return null
  // Формат ДД.ММ.ГГГГ
  const parts = dateStr.split('.')
  if (parts.length === 3) {
    return new Date(parts[2], parts[1] - 1, parts[0]).toISOString()
  }
  return new Date(dateStr)
}

const getStatusColor = (status) => {
  switch (status) {
    case 'выполнено': return '#22c55e'      // зелёный
    case 'в работе': return '#f59e0b'        // оранжевый
    case 'просрочено': return '#ef4444'      // красный
    case 'предстоящая': return '#9ca3af'     // серый
    default: return '#9ca3af'                // серый по умолчанию
  }
}

const totalPeople = computed(() => {
  return stages.value.reduce((sum, stage) => {
    const val = Number(stage.peopleCount)
    return sum + (isNaN(val) ? 0 : val)
  }, 0)
})

// Высота таблицы (можно менять)
const tableHeight = ref(400)
const isResizing = ref(false)
const startY = ref(0)
const startHeight = ref(0)

// Начало изменения размера
const startResize = (event) => {
  isResizing.value = true
  startY.value = event.clientY
  startHeight.value = tableHeight.value
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}

// Изменение размера
const onResize = (event) => {
  if (!isResizing.value) return
  const deltaY = event.clientY - startY.value
  tableHeight.value = Math.max(0, Math.min(600, startHeight.value + deltaY))
}

// Остановка изменения размера
const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

const expandGantt = () => {
  tableHeight.value = 0
}
const collapseGantt = () => {
  tableHeight.value = 600
}

// Загрузка данных
const loadData = async () => {
  try {
    // Сначала инициализируем этапы, если их нет
    await repairDetailApi.init(props.reportId)
    
    // Загружаем данные
    const response = await repairDetailApi.getByReportId(props.reportId)
    parentReport.value = response.data.parentReport
    stages.value = response.data.details
  } catch (error) {
    console.error('Failed to load repair details:', error)
  }
}


// Сохранение изменений и обновление диаграммы
const onCellChanged = async (event) => {
  const { data, colDef, newValue } = event

  // Сохраняем изменение в БД
  try {
    const recordId = event.data.id
    const field = event.colDef.field
    const updateData = { [field]: event.newValue }
    await repairDetailApi.update(recordId, updateData)
    console.log('Сохранено в БД')
  } catch (error) {
    console.error('Ошибка сохранения:', error)
    alert('Ошибка сохранения данных!')
  }
  
  try {
    // Сохраняем текущую позицию скролла
    const scrollTop = gridApi.value?.getBodyViewportElement()?.scrollTop;

    await repairDetailApi.update(data.id, {
      [colDef.field]: newValue
    })

    
    // Обновляем локальный массив для реактивности
    const index = stages.value.findIndex(s => s.id === data.id)
    if (index !== -1) {
      // Создаём новый объект чтобы Vue увидел изменения
      stages.value[index] = { 
        ...stages.value[index], 
        [colDef.field]: newValue 
      }

      // Если изменилось Название первой строки (index 0) — обновляем parentName у всех
      if (colDef.field === 'stageName' && index === 0) {
        // Обновляем parentName у всех записей
        for (let i = 0; i < stages.value.length; i++) {
          stages.value[i].parentName = newValue
          // Сохраняем в API
          await repairDetailApi.update(stages.value[i].id, { parentName: newValue })
        }
      }
      // Принудительно обновляем массив
      stages.value = [...stages.value]

      // Восстанавливаем позицию скролла
      if (typeof scrollTop === 'number' && gridApi.value) {
        setTimeout(() => {
        gridApi.value.getBodyViewportElement().scrollTop = scrollTop;
        }, 0);
      }
    }
    
    console.log('Данные обновлены, диаграмма перестроена')
  } catch (error) {
    console.error('Failed to update:', error)
  }
}

const onSelectionChanged = () => {
  const selectedNodes = gridApi.value?.getSelectedNodes() || []
  
  if (selectedNodes.length > 0) {
    const newSelectedId = selectedNodes[0].data.id
    
    // Если выбрана та же строка — не сбрасываем редактирование
    if (selectedStageId.value !== newSelectedId) {
      selectedStageId.value = newSelectedId
      // Выключаем режим редактирования только при смене строки
      if (isEditing.value) {
        isEditing.value = false
        gridApi.value?.refreshCells({ force: true })
      }
    }

    const data = selectedNodes[0].data
    if (data.pdfUrl && data.pdfUrl.trim().length > 0) {
      selectedPdfUrl.value = data.pdfUrl
    } else {
      selectedPdfUrl.value = null
    }
    
    // Прокручиваем диаграмму к выбранной задаче
    if (ganttChartRef.value) {
      ganttChartRef.value.selectAndScrollToTask(newSelectedId)
    }
  } else if (!isEditing.value) {
    // Сбрасываем только если не редактируем
    selectedStageId.value = null
    selectedPdfUrl.value = null
  }
}


const onGridReady = (params) => {
  gridApi.value = params.api
}

// Обработчик выбора строки в таблице
const onRowSelected = (event) => {
  if (event.node.isSelected()) {
    selectedStageId.value = event.data.id
    
    // Прокручиваем диаграмму к выбранной задаче
    if (ganttChartRef.value) {
      ganttChartRef.value.selectAndScrollToTask(event.data.id)
    }
  } else {
    // Сбрасываем ТОЛЬКО если не в режиме редактирования
    // или если снимается выделение с другой строки
    if (!isEditing.value) {
      selectedStageId.value = null
    }
  }
}

// Обратная синхронизация: выбор в Ганте → выбор в таблице
const onGanttTaskSelected = (taskId) => {
  selectedStageId.value = taskId
  
  // Выбираем строку в таблице
  if (gridApi.value) {
    gridApi.value.forEachNode((node) => {
      if (node.data.id === taskId) {
        node.setSelected(true)
        // Прокручиваем таблицу к строке
        gridApi.value.ensureNodeVisible(node, 'middle')
      } else {
        node.setSelected(false)
      }
    })
  }
}

const goBack = () => {
  emit('back')
}

const goToWarehouse = () => {
  // Здесь будет логика перехода на склад
  // Пока просто выводим ID выбранного этапа
  isShow.value = false
  console.log('Переход на склад для этапа:', selectedStageId.value)
  // Например: router.push(`/warehouse/${selectedStageId.value}`)
}

// Создание связи
const handleCreateConnection = (connection) => {
  const newId = localConnections.value.length > 0 
    ? Math.max(...localConnections.value.map(c => c.id)) + 1 
    : 1
  
  localConnections.value.push({
    id: newId,
    from_task_id: connection.from_task_id,
    to_task_id: connection.to_task_id,
    arrow_color: '#666',
    arrow_style: 'solid',
    arrow_type: connection.arrow_type || 'finish-to-start'
  })
  
  console.log('Создана связь:', connection)
}

// Удаление связи (правый клик)
const handleDeleteConnection = (connectionId) => {
  const index = localConnections.value.findIndex(c => c.id === connectionId)
  if (index !== -1) {
    localConnections.value.splice(index, 1)
    console.log('Удалена связь:', connectionId)
  }
}

// Хелпер для форматирования даты в формат ДД.ММ.ГГГГ
const formatDateToDDMMYYYY = (isoDate) => {
  if (!isoDate) return ''
  const date = new Date(isoDate)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Live update - обновляет только локальное состояние (во время перетаскивания)
const handleUpdateTaskLive = (updates) => {
  updates.forEach(update => {
    const stageIndex = stages.value.findIndex(s => s.id === update.id)
    if (stageIndex !== -1) {
      // Обновляем локально даты
      if (update.start_date) {
        stages.value[stageIndex].startDate = formatDateToDDMMYYYY(update.start_date)
      }
      if (update.end_date) {
        stages.value[stageIndex].endDate = formatDateToDDMMYYYY(update.end_date)
      }
    }
  })
  // Принудительно обновляем массив для реактивности
  stages.value = [...stages.value]
}

// Final update - сохраняет в БД (после отпускания мыши)
const handleUpdateTask = async (update) => {
  const stageIndex = stages.value.findIndex(s => s.id === update.id)
  if (stageIndex === -1) return
  
  try {
    const updateData = {}
    
    if (update.start_date) {
      updateData.startDate = formatDateToDDMMYYYY(update.start_date)
    }
    if (update.end_date) {
      updateData.endDate = formatDateToDDMMYYYY(update.end_date)
    }
    
    // Сохраняем в БД
    await repairDetailApi.update(update.id, updateData)
    
    // Обновляем локальные данные
    stages.value[stageIndex] = {
      ...stages.value[stageIndex],
      ...updateData
    }
    stages.value = [...stages.value]
    
    console.log('Даты обновлены через Ганта:', updateData)
  } catch (error) {
    console.error('Ошибка обновления дат:', error)
    alert('Ошибка сохранения дат!')
    // Перезагружаем данные при ошибке
    await loadData()
  }
}

const handleAttachPdf = (newUrl) => {
  if (!selectedStageId.value) return
  
  const index = stages.value.findIndex(s => s.id === selectedStageId.value)
  if (index !== -1) {
    stages.value[index].pdfUrl = newUrl
    gridApi.value?.applyTransaction({ update: [stages.value[index]] })
    selectedPdfUrl.value = newUrl
  }
}

const openAttachModal = () => {
  isEditPdfMode.value = true;
  isPdfModalOpen.value = true;
}

onMounted(() => {
  loadData()
  setTimeout(() => {
    console.log('stages.value:', stages.value)
  }, 1000)
})
</script>

<style scoped>
.detailed-gantt-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  gap: 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.btn-back {
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-back:hover {
  background: #e2e8f0;
}

.parent-info h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.parent-info .serial {
  font-size: 14px;
  color: #64748b;
}

.stages-gantt {
  flex: 1;
  min-height: 300px;
}

.stages-table {
  flex-shrink: 0;
  overflow: hidden;
  transition: height 0.05s ease;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #f1f5f9;
  color: #475569;
}

.btn-add {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(34, 197, 94, 0.4);
}

.btn-delete {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.btn-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(239, 68, 68, 0.4);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-edit {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-edit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.resize-divider {
  position: relative;
  height: 12px;
  background: #e2e8f0;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 4px;
  margin: 4px 0;
  transition: background 0.2s;
}

.resize-btn {
  position: absolute;
  right: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 14px;
}

.resize-btn:first-of-type {
  top: -20px;
}
.resize-btn:last-of-type {
  top: 5px;
}

.resize-divider:hover {
  background: #cbd5e1;
}

.resize-handle {
  color: #94a3b8;
  font-size: 14px;
  letter-spacing: 2px;
  user-select: none;
}

.btn-warehouse {
  padding: 8px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-left: auto;
  transition: background-color 0.2s, opacity 0.2s;
}

.btn-warehouse:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-warehouse:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #9ca3af;
}

.btn-pdf {
  background-color: #94a3b8;
  transition: all 0.3s ease;
  cursor: not-allowed;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  color: white;
}

.btn-pdf-active {
  background-color: #f1dd01;
  cursor: pointer;
  /* border: 1px solid #00000079; */
  color: #333;
}
</style>