<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { reportApi } from '../api'
import { useI18n } from 'vue-i18n'

// Emit for navigation
const emit = defineEmits(['navigate-to-detail'])
const { t } = useI18n()

// ===== РУССКАЯ ЛОКАЛИЗАЦИЯ ФИЛЬТРОВ =====
const localeRu = computed(()  => ({
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
  
  // Пагинация
  page: t('agGrid.page'),
  more: t('agGrid.more'),
  of: t('agGrid.of'),
  to: t('agGrid.to'),
  nextPage: t('agGrid.nextPage'),
  previousPage: t('agGrid.previousPage'),
  firstPage: t('agGrid.firstPage'),
  lastPage: t('agGrid.lastPage'),
  pageSize: t('agGrid.pageSize'),
  pageSizeSelectorLabel: t('agGrid.pageSizeSelectorLabel'),
  
  // Выделение
  selectAll: t('agGrid.selectAll'),
  selectAllSearchResults: t('agGrid.selectAllSearchResults'),
  searchOoo: t('agGrid.searchOoo'),
  noMatches: t('agGrid.noMatches'),
  
  // Прочее
  noRowsToShow: t('agGrid.noRowsToShow'),
  loading: t('agGrid.loading'),
  pinColumn: t('agGrid.pinColumn'),
  autosizeThiscolumn: t('agGrid.autosizeThiscolumn'),
  autosizeAllColumns: t('agGrid.autosizeAllColumns'),
  resetColumns: t('agGrid.resetColumns'),
  copy: t('agGrid.copy'),
  copyWithHeaders: t('agGrid.copyWithHeaders'),
  paste: t('agGrid.paste'),
  export: t('agGrid.export'),
  csvExport: t('agGrid.csvExport'),
  excelExport: t('agGrid.excelExport'),
}))

const gridApi = ref(null)
const searchText = ref('')
const selectedRows = ref([])
const showAddModal = ref(false)
const showColumnPanel = ref(false)
const editingRowId = ref(null)

// Функция для проверки, можно ли выбрать строку
const isRowSelectable = (node) => {
  return !node.data?.isColumnNumbers && !node.data?.isSectionHeader
}

// Можно ли открыть детализацию (выбрана одна просроченная строка)
const canOpenDetail = computed(() => {
  return selectedRows.value.length === 1 
})

// Проверяем, является ли выбранная строка просроченной
const isSelectedRowOverdue = computed(() => {
  return selectedRows.value.length === 1 && 
         selectedRows.value[0]?.status === 'просрочено'
})

// Цвета для статусов
const getStatusColor = (status) => {
  switch (status) {
    case 'выполнено': return '#22c55e'      // зелёный
    case 'в работе': return '#f59e0b'        // оранжевый
    case 'просрочено': return '#ef4444'      // красный
    case 'предстоящая': return '#9ca3af'     // серый
    default: return '#9ca3af'
  }
}

// Открыть детализацию
const handleDetailClick = () => {
  if (canOpenDetail.value) {
    emit('navigate-to-detail', selectedRows.value[0])
  }
}

// Set of hidden column fields
const hiddenFieldsSet = ref(new Set())

// Base column definitions with multi-level headers (headerGroup)
// Колонки по структуре DOC.xlsx

const baseColumnDefs = [
  { 
    field: 'id', 
    headerName: t('reports.tableColumns.id'), 
    width: 50,
    minWidth: 70,
    //headerCheckboxSelection: true,
    filter: 'agTextColumnFilter',
    // Для заголовков секций показываем sectionTitle, для обычных строк - id
    valueGetter: (params) => {
      return params.data?.id
    },
    comparator: (valueA, valueB, nodeA, nodeB) => {
      if (valueA == valueB) return 0
      return valueA > valueB ? 1 : -1
    }
  },
  { field: 'tcr', headerName: t('reports.tableColumns.tcr'), editable: (params) => params.data?.id === editingRowId.value, sortable: true, filter: 'agTextColumnFilter', width: 105 },
  { field: 'nameRETIndex', headerName: t('reports.tableColumns.nameRETIndex'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 105 },
  { field: 'factoryNumber', headerName: t('reports.tableColumns.factoryNumber'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 80 },
  { field: 'repairType', headerName: t('reports.tableColumns.repairType'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 140 },
  { field: 'dueDate', headerName: t('reports.tableColumns.dueDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'plannedStartDate', headerName: t('reports.tableColumns.plannedStartDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'beginRepairDate', headerName: t('reports.tableColumns.beginRepairDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'status', headerName: t('reports.tableColumns.status'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 120, cellEditor: 'agSelectCellEditor', cellEditorParams: {
    values: ['предстоящая', 'в работе', 'выполнено', 'просрочено']
  }, cellRenderer: (params) => {
    if (!params.value || params.data?.isSectionHeader) return params.value || ''
    const color = getStatusColor(params.value)
    return `<span style="
      display: inline-block;
      padding: 2px 8px;
      border-radius: 20px;
      background-color: ${color}30;
      color: ${color};
      font-weight: bold;
      font-size: 11px;
    ">${params.value}</span>`
  }}, 
  { field: 'plannedEndDate', headerName: t('reports.tableColumns.plannedEndDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'endRepairDate', headerName: t('reports.tableColumns.endRepairDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },

  { field: 'receivingDate', headerName: t('reports.tableColumns.receivingDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'category', headerName: t('reports.tableColumns.category'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 75 },
  { field: 'makeDate', headerName: t('reports.tableColumns.makeDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 95 },
  { field: 'failureDate', headerName: t('reports.tableColumns.failureDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 90 },
  { field: 'capitalRepairs', headerName: t('reports.tableColumns.capitalRepairs'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'militaryRepairs', headerName: t('reports.tableColumns.militaryRepairs'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 100 },
  { field: 'hoursFromStart', headerName: t('reports.tableColumns.hoursFromStart'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 130 },
  { field: 'hoursFromLastRepair', headerName: t('reports.tableColumns.hoursFromLastRepair'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 140 },
  { field: 'responsibleRepair', headerName: t('reports.tableColumns.responsibleRepair'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 150 },
  { field: 'laborCost', headerName: t('reports.tableColumns.laborCost'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 95 },
  { field: 'usedZIP', headerName: t('reports.tableColumns.usedZIP'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 95 },
  { field: 'issueDate', headerName: t('reports.tableColumns.issueDate'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 95 },
  { field: 'responsibleTransfer', headerName: t('reports.tableColumns.responsibleTransfer'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 150 },
  { field: 'destination', headerName: t('reports.tableColumns.destination'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', width: 170 },
  { field: 'comments', headerName: t('reports.tableColumns.comments'), editable: (params) => params.data?.id === editingRowId.value, filter: 'agTextColumnFilter', minWidth: 150 }
]
/*const baseColumnDefs = [
  { 
    field: 'id', 
    headerName: '№ п/п', 
    width: 120,
    minWidth: 100,
    checkboxSelection: true,
    headerCheckboxSelection: true,
    filter: 'agTextColumnFilter',
    colSpan: (params) => {
      if (params.data?.isSectionHeader) {
        return 22
      }
      return 1
    },
    cellClass: (params) => {
      if (params.data?.isSectionHeader) {
        return 'section-header-cell'
      }
      return null
    },
    // Для заголовков секций показываем sectionTitle, для обычных строк - id
    valueGetter: (params) => {
      if (params.data?.isSectionHeader) {
        return params.data.sectionTitle || ''
      }
      if (params.data?.isColumnNumbers) {
        return ' '  // Пробел вместо пустой строки
      }
      return params.data?.id
    },
    comparator: (valueA, valueB, nodeA, nodeB) => {
      // Заголовки секций всегда остаются на месте
      if (nodeA.data?.isSectionHeader) return -1
      if (nodeB.data?.isSectionHeader) return 1
      // Обычная сортировка
      if (valueA == valueB) return 0
      return valueA > valueB ? 1 : -1
    }
  },
  { field: 'receivingDate', headerName: 'Дата приема на ТО, в ремонт', editable: true, filter: 'agTextColumnFilter', width: 130 },
  { field: 'division', headerName: 'Подразделение', editable: true, filter: 'agTextColumnFilter', width: 130 },
  { field: 'nameRETIndex', headerName: 'Наименование, индекс РЭТ', editable: true, filter: 'agTextColumnFilter', minWidth: 200 },
  { field: 'factoryNumber', headerName: 'Заводской номер', editable: true, filter: 'agTextColumnFilter', width: 120 },
  { field: 'category', headerName: 'Категория', editable: true, filter: 'agTextColumnFilter', width: 100 },
  
  // Группа "Дата" (изготовления, выхода из строя)
  {
    headerName: 'Дата',
    marryChildren: true,
    children: [
      { field: 'makeDate', headerName: 'изготовления', editable: true, filter: 'agTextColumnFilter', width: 110 },
      { field: 'failureDate', headerName: 'выхода из строя', editable: true, filter: 'agTextColumnFilter', width: 120 },
    ]
  },
  
  { field: 'repairType', headerName: 'Вид требуемого ремонта (обслуживания, регламентных работ)', editable: true, filter: 'agTextColumnFilter', minWidth: 220 },
  { field: 'dueDate', headerName: 'Срок выполнения работ', editable: true, filter: 'agTextColumnFilter', width: 140 },
  
  // Группа "Количество проведенных ремонтов"
  {
    headerName: 'Количество проведенных ремонтов',
    marryChildren: true,
    children: [
      { field: 'capitalRepairs', headerName: 'капитальных', editable: true, filter: 'agTextColumnFilter', width: 100 },
      { field: 'militaryRepairs', headerName: 'войсковых', editable: true, filter: 'agTextColumnFilter', width: 100 },
    ]
  },
  
  // Группа "Количество отработанных часов км"
  {
    headerName: 'Количество отработанных часов км',
    marryChildren: true,
    children: [
      { field: 'hoursFromStart', headerName: 'с начала эксплуатации', editable: true, filter: 'agTextColumnFilter', width: 140 },
      { field: 'hoursFromLastRepair', headerName: 'после последнего ремонта', editable: true, filter: 'agTextColumnFilter', width: 160 },
    ]
  },
  
  { field: 'responsibleRepair', headerName: 'Ответственный за ремонт (должность, в/звание, фамилия и инициалы, подпись)', editable: true, filter: 'agTextColumnFilter', minWidth: 250 },
  { field: 'beginRepairDate', headerName: 'Дата начала ремонта', editable: true, filter: 'agTextColumnFilter', width: 130 },
  { field: 'workType', headerName: 'Вид работ', editable: true, filter: 'agTextColumnFilter', width: 150 },
  { field: 'laborCost', headerName: 'Трудозатраты (чел.-ч.)', editable: true, filter: 'agTextColumnFilter', width: 130 },
  { field: 'usedZIP', headerName: 'Израсходованный ЗИП и материалы', editable: true, filter: 'agTextColumnFilter', minWidth: 200 },
  
  // Группа "Дата" (окончания, выдачи)
  {
    headerName: 'Дата',
    marryChildren: true,
    children: [
      { field: 'endRepairDate', headerName: 'окончания ремонта', editable: true, filter: 'agTextColumnFilter', width: 130 },
      { field: 'issueDate', headerName: 'выдачи из ремонта', editable: true, filter: 'agTextColumnFilter', width: 130 },
    ]
  },
  
  { field: 'responsibleTransfer', headerName: 'Ответственный за передачу (в/звание, фамилия и инициалы, подпись)', editable: true, filter: 'agTextColumnFilter', minWidth: 250 },
  { field: 'destination', headerName: 'Куда направлено № и дата документа', editable: true, filter: 'agTextColumnFilter', minWidth: 200 },
]*/


// Обработчик кнопки "Просрочено" - toggle (вкл/выкл)
const handleOverdueClick = async () => {
  if (selectedRows.value.length === 1) {
    const row = selectedRows.value[0]
    
    // Определяем: снимаем или ставим статус "просрочено"
    const isCurrentlyOverdue = row.status === 'просрочено'
    
    // Новые значения (toggle)
    const newStatus = isCurrentlyOverdue ? 'предстоящая' : 'просрочено'
    const newColor = isCurrentlyOverdue ? '#4A90D9' : '#fee2e2'
    
    try {
      // Обновляем статус в БД
      await reportApi.update(row.id, { 
        status: newStatus,
        color: newColor
      })
      
      // Обновляем локально
      const index = rowData.value.findIndex(r => r.id === row.id)
      if (index !== -1) {
        rowData.value[index].status = newStatus
        rowData.value[index].color = newColor
      }
      
      // Обновляем грид
      gridApi.value?.refreshCells({ force: true })
      gridApi.value?.redrawRows()
      
      if (isCurrentlyOverdue) {
        console.log('Статус "просрочено" снят:', row.id)
      } else {
        console.log('Строка помечена как просроченная:', row.id)
      }
    } catch (error) {
      console.error('Ошибка обновления статуса:', error)
      alert('Ошибка при обновлении статуса!')
    }
  }
}

// Computed column definitions - БЕЗ кастомного header (он ломает отображение в Community)
const columnDefsWithHide = computed(() => {
  const processColumn = (col) => {
    // If it's a group (has children), process children recursively
    if (col.children) {
      const filteredChildren = col.children
        .filter(child => !hiddenFieldsSet.value.has(child.field))
      
      if (filteredChildren.length === 0) return null
      return { ...col, children: filteredChildren }
    }
    
    // Regular column
    if (hiddenFieldsSet.value.has(col.field)) return null
    return col
  }
  
  return baseColumnDefs.map(processColumn).filter(Boolean)
})

// Get all leaf columns for hidden columns bar
const getAllLeafColumns = () => {
  const leaves = []
  const traverse = (cols) => {
    for (const col of cols) {
      if (col.children) traverse(col.children)
      else leaves.push(col)
    }
  }
  traverse(baseColumnDefs)
  return leaves
}

// All leaf columns for column panel
const allLeafColumns = computed(() => getAllLeafColumns())

// List of hidden columns for the bar
const hiddenColumns = computed(() => {
  return getAllLeafColumns().filter(col => hiddenFieldsSet.value.has(col.field))
})

// Toggle column visibility
const toggleColumn = (field) => {
  const newSet = new Set(hiddenFieldsSet.value)
  if (newSet.has(field)) {
    newSet.delete(field)
  } else {
    newSet.add(field)
  }
  hiddenFieldsSet.value = newSet
}

// Hide a column
const hideColumn = (field) => {
  hiddenFieldsSet.value = new Set([...hiddenFieldsSet.value, field])
}

// Show a column
const showColumn = (field) => {
  const newSet = new Set(hiddenFieldsSet.value)
  newSet.delete(field)
  hiddenFieldsSet.value = newSet
}

// Context for grid (used by header component)
const gridContext = { hideColumn }

// ===== PINNED TOP ROWS =====
// Row with column numbers 1-22
// ===== PINNED TOP ROWS =====
// Row with column numbers 1-22
/*const columnNumbersRow = {
  isColumnNumbers: true,
  id: ' ',
  receivingDate: '1', division: '2', nameRETIndex: '3', factoryNumber: '4',
  category: '5', makeDate: '6', failureDate: '7', repairType: '8', dueDate: '9',
  capitalRepairs: '10', militaryRepairs: '11', hoursFromStart: '12', hoursFromLastRepair: '13',
  responsibleRepair: '14', beginRepairDate: '15', workType: '16', laborCost: '17',
  usedZIP: '18', endRepairDate: '19', issueDate: '20', responsibleTransfer: '21',
  destination: '22'
}*/

//const pinnedTopRows = ref([columnNumbersRow])

// Стилизация строк по статусу
const getRowStyle = (params) => {  
  // Красный фон для просроченных
  if (params.data?.status === 'просрочено') {
    return { 
      background: '#fee2e2',  // светло-красный
      cursor: 'pointer'       // указатель что кликабельно
    }
  }
  
  return null
}

// Заголовки секций не должны сортироваться - сохраняем их позиции
const postSortRows = (params) => {
  const rowNodes = params.nodes
  
  // Находим индексы заголовков секций и их позиции
  const sectionHeaders = []
  const regularRows = []
  
  // Получаем оригинальные данные с заголовками
  const originalData = rowData.value
  
  // Разделяем на заголовки и обычные строки
  rowNodes.forEach(node => {
    if (node.data?.isSectionHeader) {
      sectionHeaders.push(node)
    } else {
      regularRows.push(node)
    }
  })
  
  // Если нет заголовков секций, ничего не делаем
  if (sectionHeaders.length === 0) return
  
  // Восстанавливаем оригинальный порядок с заголовками на своих местах
  const result = []
  let regularIndex = 0
  
  originalData.forEach(item => {
    if (item.isSectionHeader) {
      // Находим соответствующий заголовок по sectionTitle
      const header = sectionHeaders.find(h => h.data.sectionTitle === item.sectionTitle)
      if (header) result.push(header)
    } else {
      // Берём следующую отсортированную обычную строку
      if (regularIndex < regularRows.length) {
        result.push(regularRows[regularIndex++])
      }
    }
  })
  
  // Заменяем содержимое массива
  rowNodes.length = 0
  result.forEach(node => rowNodes.push(node))
}

// Row height
const getRowHeight = (params) => {
  return 35
}

// Новая строка для добавления
const newRow = reactive({
  receivingDate: '',
  // division: '',
  tcr: '',
  nameRETIndex: '',
  factoryNumber: '',
  category: '',
  makeDate: '',
  failureDate: '',
  repairType: '',
  dueDate: '',
  plannedStartDate: '',
  capitalRepairs: '',
  militaryRepairs: '',
  hoursFromStart: '',
  hoursFromLastRepair: '',
  responsibleRepair: '',
  beginRepairDate: '',
  status: '',
  laborCost: '',
  usedZIP: '',
  endRepairDate: '',
  issueDate: '',
  responsibleTransfer: '',
  destination: '',
  comments: ''
})

const resetNewRow = () => {
  Object.keys(newRow).forEach(key => {
    newRow[key] = ''
  })
}

const defaultColDef = ref({
  sortable: false,
  resizable: true,
  filter: true,
  floatingFilter: true,
  wrapText: true,
  autoHeight: true,
  wrapHeaderText: true,
  autoHeaderHeight: true,
})

const toggleEditMode = () => {
  if (selectedRows.value.length === 1) {
    const row = selectedRows.value[0]
    if (editingRowId.value === row.id) {
      // Выходим из режима редактирования
      editingRowId.value = null
    } else {
      // Входим в режим редактирования
      editingRowId.value = row.id
    }
    gridApi.value?.refreshCells({ force: true })
  }
}

// Данные таблицы - загружаются из API базы данных
const rowData = ref([])
const isLoading = ref(true)

// Загрузка данных из API
const loadData = async () => {
  try {
    isLoading.value = true
    const response = await reportApi.getAll()
    if (response.data && response.data.length > 0) {
      rowData.value = response.data
    } else {
      // Если в БД пусто, загрузим начальные данные из JSON
      await loadInitialData()
    }
  } catch (error) {
    console.error('Ошибка загрузки данных из API:', error)
    // Fallback на JSON
    await loadInitialData()
  } finally {
    isLoading.value = false
  }
}

// Загрузка начальных данных из JSON (один раз)
const loadInitialData = async () => {
  try {
    const response = await fetch('/data.json')
    const json = await response.json()
    const rows = json.rows || []
    
    // Сохраняем каждую строку в БД
    for (const row of rows) {
      await reportApi.create(row)
    }
    
    // Перезагружаем из БД
    const dbResponse = await reportApi.getAll()
    rowData.value = dbResponse.data || []
  } catch (error) {
    console.error('Ошибка загрузки начальных данных:', error)
    rowData.value = []
  }
}

// Загрузка при монтировании
onMounted(async () => {
  await loadData()
})

const onGridReady = (params) => {
  gridApi.value = params.api
}

// const onSelectionChanged = () => {
//   selectedRows.value = gridApi.value?.getSelectedRows() || []
// }

const onSelectionChanged = () => {
  selectedRows.value = gridApi.value?.getSelectedRows() || []
  // Сбрасываем режим редактирования при смене строки
  editingRowId.value = null
}

// const onSelectionChanged = () => {
//   const newSelectedRows = gridApi.value?.getSelectedRows() || []
  
//   // Сбрасываем режим редактирования ТОЛЬКО если сменилась строка
//   if (editingRowId.value !== null) {
//     const stillSelected = newSelectedRows.some(row => row.id === editingRowId.value)
//     if (!stillSelected) {
//       editingRowId.value = null
//     }
//   }
  
//   selectedRows.value = newSelectedRows
// }

const onCellValueChanged = async (event) => {
  console.log('Изменено:', event.colDef.field, '→', event.newValue)
  
  // Не сохраняем специальные строки
  if (event.data?.isSectionHeader || event.data?.isColumnNumbers) {
    return
  }

  gridApi.value?.redrawRows()
  
  // Сохраняем изменение в БД
  try {
    const recordId = event.data.id
    const field = event.colDef.field
    const updateData = { [field]: event.newValue }
    await reportApi.update(recordId, updateData)
    console.log('Сохранено в БД')
  } catch (error) {
    console.error('Ошибка сохранения:', error)
    alert('Ошибка сохранения данных!')
  }
}

const onSearch = () => {
  gridApi.value?.setQuickFilter(searchText.value)
}

const openAddModal = () => {
  resetNewRow()
  showAddModal.value = true
}

const addRow = async () => {
  if (!newRow.nameRETIndex.trim()) {
    alert('Введите наименование РЭТ!')
    return
  }
  
  try {
    // Создаём запись в БД
    const response = await reportApi.create({
      ...JSON.parse(JSON.stringify(newRow))
    })
    
    // Добавляем в локальный массив
    rowData.value = [...rowData.value, response.data]
    showAddModal.value = false
    console.log('Запись добавлена в БД')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    alert('Ошибка добавления записи!')
  }
}

const deleteSelected = async () => {
  if (confirm(`Удалить ${selectedRows.value.length} записей?`)) {
    try {
      const idsToDelete = selectedRows.value.map(r => r.id)
      
      // Удаляем из БД
      for (const id of idsToDelete) {
        await reportApi.delete(id)
      }
      
      // Удаляем из локального массива
      rowData.value = rowData.value.filter(r => !idsToDelete.includes(r.id))
      selectedRows.value = []
      console.log('Записи удалены из БД')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      alert('Ошибка удаления записей!')
    }
  }
}

const exportCsv = () => {
  gridApi.value?.exportDataAsCsv({ fileName: 'data.csv' })
}
</script>

<template>
  <div class="card reports-card">
    <div class="demo-header">
      <!-- <h2>📊 Учет работ</h2> -->
       <h2>{{ $t('reports.title') }}</h2>
    </div>
    
    <!-- Hidden columns bar -->
    <div v-if="hiddenColumns.length > 0" class="hidden-columns-bar">
      <span class="hc-label">{{ $t('reports.hiddenColumns') }}</span>
      <span 
        v-for="col in hiddenColumns" 
        :key="col.field" 
        class="hidden-column-tag"
        @click="showColumn(col.field)"
        title="Нажмите, чтобы показать"
      >
        {{ col.headerName || col.field }} ✕
      </span>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-group">
        <!-- <button class="btn-add" @click="openAddModal">➕ Добавить</button> -->
         <button class="btn-add" @click="openAddModal">{{ $t('reports.add') }}</button>
        <button class="btn-delete" @click="deleteSelected" :disabled="selectedRows.length === 0">
          <!-- 🗑️ Удалить ({{ selectedRows.length }}) -->
            {{ $t('reports.delete') }}
        </button>
        <!-- <button 
          class="btn-overdue" 
          :class="{ 'btn-overdue-active': isSelectedRowOverdue }"
          @click="handleOverdueClick" 
          :disabled="selectedRows.length !== 1"
          :title="isSelectedRowOverdue ? 'Снять статус просрочено' : 'Пометить как просроченную'"
        >
          {{ isSelectedRowOverdue ? '🔴 Снять просрочку' : '🔴 Пометить просроченным' }}
        </button> -->

        <button 
          class="btn-edit" 
          @click="toggleEditMode" 
          :disabled="selectedRows.length !== 1"
        >
          {{ editingRowId === selectedRows[0]?.id ? $t('reports.save') : $t('reports.edit') }}
        </button>

        <button 
          class="btn-detail" 
          @click="handleDetailClick" 
          :disabled="!canOpenDetail"
          title="Открыть детализацию выбранной строки"
        >
          <!-- 🔍 Детализация -->
           {{ $t('reports.detail') }}
        </button>
        <!-- <button class="btn-secondary" @click="exportCsv">📥 Экспорт CSV</button> -->
        <button class="btn-secondary" @click="showColumnPanel = !showColumnPanel">
          <!-- 👁️ Столбцы -->
           {{ $t('reports.columns') }}
        </button>
      </div>
      
      <div class="toolbar-group">
        <input type="text" v-model="searchText" @input="onSearch" :placeholder="$t('reports.searchPlaceholder')" class="search-input">
      </div>
    </div>
    
    <!-- Column visibility panel -->
    <div v-if="showColumnPanel" class="column-panel">
      <div class="column-panel-header">
        <strong>{{ $t('reports.showHideColumns') }}</strong>
        <button class="btn-small" @click="showColumnPanel = false">✕</button>
      </div>
      <div class="column-panel-list">
        <label v-for="col in allLeafColumns" :key="col.field" class="column-checkbox">
          <input 
            type="checkbox" 
            :checked="!hiddenFieldsSet.has(col.field)"
            @change="toggleColumn(col.field)"
          >
          {{ col.headerName }}
        </label>
      </div>
    </div>

    <!-- AG Grid -->
    <div class="ag-grid-wrapper">
      <ag-grid-vue
        class="ag-theme-alpine"
        style="width: 100%; height: 100%;"
        :columnDefs="columnDefsWithHide"
        :rowData="rowData"
        :defaultColDef="defaultColDef"        
        rowSelection="single"
        :rowDeselection="true"
        :rowMultiSelectWithClick="true"
        :isRowSelectable="isRowSelectable"
        :animateRows="true"
        :pagination="true"
        :paginationPageSize="10"
        :paginationPageSizeSelector="[5, 10, 25, 50]"
        :context="gridContext"
        :getRowStyle="getRowStyle"
        :getRowHeight="getRowHeight"
        :suppressRowClickSelection="editingRowId !== null"
        :postSortRows="postSortRows"
        :localeText="localeRu"
        @grid-ready="onGridReady"
        @selection-changed="onSelectionChanged"
        @cell-value-changed="onCellValueChanged"
        />
    </div>
    
    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal modal-wide">
        <h2>{{ $t('reports.addRecord') }}</h2>
        <div class="modal-grid">
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.receivingDate') }}</label>
            <input type="text" v-model="newRow.receivingDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.tcr') }}</label>
            <input type="text" v-model="newRow.tcr">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.nameRETIndex') }}</label>
            <input type="text" v-model="newRow.nameRETIndex">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.factoryNumber') }}</label>
            <input type="text" v-model="newRow.factoryNumber">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.repairType') }}</label>
            <input type="text" v-model="newRow.repairType">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.category') }}</label>
            <input type="text" v-model="newRow.category">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.makeDate') }}</label>
            <input type="text" v-model="newRow.makeDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.failureDate') }}</label>
            <input type="text" v-model="newRow.failureDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.dueDate') }}</label>
            <input type="text" v-model="newRow.dueDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.plannedStartDate') }}</label>
            <input type="text" v-model="newRow.plannedStartDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.capitalRepairs') }}</label>
            <input type="text" v-model="newRow.capitalRepairs">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.militaryRepairs') }}</label>
            <input type="text" v-model="newRow.militaryRepairs">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.hoursFromStart') }}</label>
            <input type="text" v-model="newRow.hoursFromStart">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.hoursFromLastRepair') }}</label>
            <input type="text" v-model="newRow.hoursFromLastRepair">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.responsibleRepair') }}</label>
            <input type="text" v-model="newRow.responsibleRepair">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.beginRepairDate') }}</label>
            <input type="text" v-model="newRow.beginRepairDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.status') }}</label>
            <select v-model="newRow.status">
              <option value="">— {{ $t('reports.select') }} —</option>
              <option value="предстоящая">{{ $t('reports.statuses.upcoming') }}</option>
              <option value="в работе">{{ $t('reports.statuses.inProgress') }}</option>
              <option value="выполнено">{{ $t('reports.statuses.completed') }}</option>
              <option value="просрочено">{{ $t('reports.statuses.overdue') }}</option>
            </select>            
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.laborCost') }}</label>
            <input type="text" v-model="newRow.laborCost">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.usedZIP') }}</label>
            <input type="text" v-model="newRow.usedZIP">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.endRepairDate') }}</label>
            <input type="text" v-model="newRow.endRepairDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.issueDate') }}</label>
            <input type="text" v-model="newRow.issueDate">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.responsibleTransfer') }}</label>
            <input type="text" v-model="newRow.responsibleTransfer">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.destination') }}</label>
            <input type="text" v-model="newRow.destination">
          </div>
          <div class="modal-field">
            <label>{{ $t('reports.tableColumns.comments') }}</label>
            <textarea v-model="newRow.comments" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-buttons">
          <button class="btn-secondary" @click="showAddModal = false">{{ $t('reports.cancel') }}</button>
          <button class="btn-add" @click="addRow">{{ $t('reports.add') }}</button>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
.demo-header {
  margin-bottom: 20px;
}

.demo-header h2 {
  color: #0284c7;
  margin-bottom: 8px;
}

/* Кнопка "Просрочено" */
.btn-overdue {
  padding: 8px 16px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s, transform 0.1s;
}

.btn-overdue:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-overdue:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  opacity: 0.6;
}

.demo-desc {
  color: #64748b;
  font-size: 14px;
}

.demo-desc a {
  color: #0284c7;
}

.btn-detail {
  padding: 10px 20px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-detail:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(34, 45, 197, 0.4);
}

.btn-detail:disabled {
  
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
}

.btn-edit {
  padding: 10px 20px;
  background-color: #ec9349;
  color: white;
  border: none;
  font-weight: 600;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  cursor: pointer;
}
.btn-edit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(232, 156, 35, 0.4);
}

.features-box {
  margin-top: 20px;
  padding: 20px;
  background: rgba(2, 132, 199, 0.05);
  border-radius: 8px;
  border-left: 4px solid #0284c7;
}

.features-box h3 {
  color: #0284c7;
  margin-bottom: 15px;
}

.features-box ul {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 8px;
}

.features-box li {
  padding: 6px 0;
  color: #475569;
}

.hidden-columns-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 10px 15px;
  background: rgba(234, 179, 8, 0.1);
  border-radius: 6px;
  margin-bottom: 15px;
  color: #ca8a04;
}

.hc-label {
  font-weight: 600;
}

.hidden-column-tag {
  padding: 4px 10px;
  background: rgba(234, 179, 8, 0.2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.hidden-column-tag:hover {
  background: rgba(234, 179, 8, 0.4);
}

.btn-upload {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;
}

.btn-upload:hover {
  opacity: 0.9;
}

.loading-bar {
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 6px;
  color: #3b82f6;
  text-align: center;
  margin-bottom: 15px;
  font-weight: 500;
}



.column-panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.column-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e2e8f0;
}

.column-panel-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.column-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #475569;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.column-checkbox:hover {
  background: #f1f5f9;
}

.column-checkbox input {
  cursor: pointer;
}

/* Растягивание на всю высоту */
.reports-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
}

.btn-small {
  padding: 4px 8px;
  border: none;
  background: #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-small:hover {
  background: #cbd5e1;
}

.ag-grid-wrapper {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  flex: 1;
  min-height: 0;
}
</style>

<style>
/* Перенос текста в ячейках - только по пробелам */
.ag-theme-alpine .ag-cell {
  white-space: pre-wrap !important;
  padding-left: 2px !important;
  padding-right: 2px !important;
  font-size: 12px !important;
  word-break: keep-all !important;         /* НЕ разрывать слова */
  overflow-wrap: normal !important;        /* перенос только по пробелам */
  hyphens: none !important;                /* без переносов */
  line-height: 1.4 !important;
  padding: 8px !important;
  overflow: visible !important; 
  text-overflow: clip !important;
}

/* Стили для просроченных строк */
.ag-theme-alpine .ag-row[data-status="просрочено"] {
  background-color: #fee2e2 !important;
  cursor: pointer !important;
}

.ag-theme-alpine .ag-row[data-status="просрочено"]:hover {
  background-color: #fecaca !important;  /* темнее при наведении */
}

/* Иконка "кликни" для просроченных строк */
.ag-theme-alpine .ag-row[data-status="просрочено"]::after {
  content: '→';
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #dc2626;
  opacity: 0;
  transition: opacity 0.2s;
}

.ag-theme-alpine .ag-row[data-status="просрочено"]:hover::after {
  opacity: 1;
}

/* ===== ЗАГОЛОВКИ ТАБЛИЦЫ ===== */

/* Убираем все отступы и иконки, которые сдвигают текст */
.ag-theme-alpine .ag-header-cell {
  padding: 0 !important;
}

.ag-theme-alpine .ag-header-cell-comp-wrapper {
  width: 100% !important;
  padding: 4px 6px !important;
}

/* Скрываем иконки меню и сортировки, которые занимают место (но НЕ чекбоксы) */
.ag-theme-alpine .ag-header-icon:not(.ag-header-select-all) {
  display: none !important;
}

/* Центрирование чекбокса в заголовке */
.ag-theme-alpine .ag-header-select-all {
  margin: 0 auto !important;
}

.ag-theme-alpine .ag-header-cell-comp-wrapper {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* Основной контейнер заголовка */
.ag-theme-alpine .ag-header-cell-label {
  white-space: normal !important;
  font-size: 12px; /*ШРИФТ*/
  word-break: keep-all !important;         /* НЕ разрывать слова */
  overflow-wrap: normal !important;        /* перенос только по пробелам */
  overflow: visible !important;
  text-overflow: clip !important;          /* БЕЗ многоточий */
  width: 100% !important;
  line-height: 1.3 !important;
  justify-content: center !important;
  text-align: center !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* Текст заголовка */
.ag-theme-alpine .ag-header-cell-text {
  white-space: normal !important;
  word-break: keep-all !important;         /* НЕ разрывать слова */
  overflow: visible !important;
  text-overflow: clip !important;          /* БЕЗ многоточий */
  text-align: center !important;
  display: block !important;
  width: 100% !important;
}

/* Заголовки групп колонок */
.ag-theme-alpine .ag-header-group-cell {
  padding: 4px 6px !important;
  text-align: center !important;
}

.ag-theme-alpine .ag-header-group-cell-label {
  white-space: normal !important;
  word-break: keep-all !important;         /* НЕ разрывать слова */
  overflow: visible !important;
  text-overflow: clip !important;          /* БЕЗ многоточий */
  justify-content: center !important;
  text-align: center !important;
  width: 100% !important;
}

.ag-theme-alpine .ag-header-group-text {
  text-align: center !important;
  word-break: keep-all !important;
}

/* Строка с номерами колонок */
.ag-theme-alpine .ag-floating-top-container .ag-row {
  background: #f8fafc !important;
}

.ag-theme-alpine .ag-floating-top-container .ag-cell {
  font-weight: 700 !important;
  text-align: center !important;
  justify-content: center !important;
}

/* Центрирование текста в ячейках с данными */
.ag-theme-alpine .ag-center-cols-container .ag-cell {
  display: flex !important;
  align-items: center !important;
}

/* Стили для первой колонки (№ п/п) - но не для заголовков секций */
.ag-theme-alpine .ag-pinned-left-cols-container .ag-cell:not(.section-header-cell),
.ag-theme-alpine .ag-cell:first-child:not(.section-header-cell) {
  font-weight: 600 !important;
  text-align: center !important;
  justify-content: center !important;
}

</style>