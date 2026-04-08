<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ChartsTab from '../components/charts/ChartsTab.vue'
import ForeCastChart from '../components/charts/ForeCastChart.vue';
import YearlyComparisonChart from '../components/charts/YearlyComparisonChart.vue';
import GroupBreakdowns from '../components/charts/GroupBreakdowns.vue';
import { useDataStore } from '../components/charts/dataStore';
import { storeToRefs } from 'pinia';

// const props = defineProps({
//   data: {
//     type: Array,
//     required: true,
//     validator: (value) => { return value !== null && typeof value === 'object' }
//   },
// });
const dataStore = useDataStore()

const { jsonData, isLoading, error } = storeToRefs(dataStore)

dataStore.loadData()

const props = {data: jsonData.value}
// Данные
const rawData = ref([])
const headers = ref([])
const numericHeaders = ref([])
const dateColumns = ref([])

// Выбор колонок
const selectedColumn1 = ref('')
const selectedColumn2 = ref('')
const aggregationType = ref('unique')

// Фильтры
const filterColumn = ref('')
const filterValue = ref('')
const filterValues = ref([])

// Фильтр дат
const dateColumn = ref('')
const startDate = ref('')
const endDate = ref('')

const chartData = ref([])
const filteredData = ref([])

const aggregationLabels = {
  count: 'Количество строк',
  unique: 'Уникальные значения',
  sum: 'Сумма значений'
}

const loadData = () => {
  if (!props.data.length > 0) {
  rawData.value = props.data
  processHeaders()
  selectedColumn1.value = headers.value[0]
  selectedColumn2.value = numericHeaders.value.length > 0 ? numericHeaders.value[0] : ''
  updateChart()
  }  
}


// Обработка заголовков
const processHeaders = () => {
  headers.value = Object.keys(rawData.value[0])  
  numericHeaders.value = headers.value.filter(header => 
    typeof +rawData.value[0][header] === 'number'
  )
  
  dateColumns.value = headers.value.filter(header => 
    isDateColumn(rawData.value[0][header])
  )
}

// Проверка, является ли колонка датой
const isDateColumn = (value) => {
  if (typeof value === 'string') {
    return !isNaN(Date.parse(value)) && value.includes('-')
  }
  return value instanceof Date
}

// Обновление доступных значений для фильтра
const updateFilterValues = () => {
  if (!filterColumn.value) {
    filterValues.value = []
    filterValue.value = ''
    return
  }
  
  const values = new Set()
  rawData.value.forEach(item => {
    const value = item[filterColumn.value]
    if (value !== null && value !== undefined) {
      values.add(value.toString())
    }
  })
  
  filterValues.value = Array.from(values).sort()
  filterValue.value = ''
}

// Обновление диапазона дат
const updateDateRange = () => {
  if (!dateColumn.value) {
    startDate.value = ''
    endDate.value = ''
    return
  }
  
  // Автоматически устанавливаем минимальную и максимальную даты
  const dates = rawData.value.map(item => new Date(item[dateColumn.value])).filter(date => !isNaN(date.getTime())).sort((a, b) => a - b)
  if (dates.length > 0) {
    startDate.value = formatDateInput(dates[0])
    endDate.value = formatDateInput(dates[dates.length - 1])
  }
  
  updateChart()
}

// Обработчики событий
const selectedItem = ref(null);
const showModal = ref(false);

const handleBarClick = (item) => {
    selectedItem.value = {
        label: item.label,
        value: item.value,
        items: item.items
    };
    showModal.value = true;
};

// Форматирование даты для input[type="date"]
const formatDateInput = (date) => {
  return date.toISOString().split('T')[0]
}

// Фильтрация данных
const applyFilters = () => {
  let data = [...rawData.value]

  // Фильтр по значению
  if (filterColumn.value && filterValue.value) {
    data = data.filter(item => 
      item[filterColumn.value]?.toString() === filterValue.value
    )
  }

  // Фильтр по дате
  if (dateColumn.value && startDate.value && endDate.value) {
    const start = new Date(startDate.value)
    const end = new Date(endDate.value)
    end.setHours(23, 59, 59, 999) // Включить весь конечный день

    data = data.filter(item => {
      const itemDate = new Date(item[dateColumn.value])
      return itemDate >= start && itemDate <= end
    })
  }

  filteredData.value = data
}

// Агрегация данных
const aggregateData = () => {
  if (!selectedColumn1.value || filteredData.value.length === 0) return []  
  const groups = {}  
  filteredData.value.forEach(item => {
    const groupKey = item[selectedColumn1.value]
    if (groupKey === null || groupKey === undefined) return
    
    if (!groups[groupKey]) {
      groups[groupKey] = {
        label: String(groupKey),
        count: 0,
        uniqueValues: new Set(),
        sum: 0,
        items: [],
      }
    }    
    groups[groupKey].count++
    groups[groupKey].items.push(item);    
    if (selectedColumn2.value) {
      const value = item[selectedColumn2.value]
      if (value !== null && value !== undefined) {
        groups[groupKey].uniqueValues.add(value)
        groups[groupKey].sum += +item['Количество']        
      }
    }
  })  
  return Object.values(groups).map(group => ({
    label: group.label,
    value: getAggregatedValue(group),
    items: group.items
  }))
}

const getAggregatedValue = (group) => {
  switch (aggregationType.value) {
    case 'count': return group.count
    case 'unique': return selectedColumn2.value ? group.uniqueValues.size : group.count
    case 'sum': return selectedColumn2.value ? group.sum : group.count
    default: return group.count
  }
}

// Обновление графика
const updateChart = () => {
  applyFilters()
  chartData.value = aggregateData()
}

const updateFilters = () => {
  updateFilterValues()
  updateChart()
}

// Сброс фильтров
const resetFilters = (name) => {
  if (name == 'date') {
    dateColumn.value = ''
    startDate.value = ''
    endDate.value = ''
  }
  else {
  filterColumn.value = ''
  filterValue.value = ''
  }
  updateChart()
}

// Вычисляемые свойства
const filterColumnOptions = computed(() => 
  headers.value.filter(header => header !== selectedColumn1.value)
)

const hasDateColumns = computed(() => dateColumns.value.length > 0)

const totalItems = computed(() => 
  chartData.value.reduce((sum, item) => sum + item.value, 0)
)

const formatDateRange = computed(() => {
  if (!dateColumn.value || !startDate.value || !endDate.value) return ''
  return `${startDate.value} - ${endDate.value}`
})
// Новые функции
//Распределение количества неисправностей по типам ячеек .groupby(plate_name)[num_name].nunique().reset_index()
function groupbyNunique(data, plateName, numName) {
  const groups = data.reduce((acc, item) => {
    const key = item[plateName];
    if (!acc[key]) {
      acc[key] = new Set();      
    }
    acc[key].add(item[numName]);
    return acc;
  }, {});
  return Object.entries(groups).map(([key, uniqueValues]) => ({
    label: key,
    value: uniqueValues.size,    
  }));
}
//Распределение неисправностей по типам элементов для ячейки df[df[plate_name]==name].groupby(def_name).size().reset_index()
function filterGroupbySize(data, plateName, name, defName) {
  const filteredData = data.filter(item => item[plateName] === name);
  const groups = filteredData.reduce((acc, item) => {
    const key = item[defName];
    acc[key] = (acc[key] || 0) + 1;
    return acc
  }, {});
  return Object.entries(groups).map(([key, count]) => ({
    label: key,
    value: count,    
  }));
}
// aggregation function
const aggFunctions = {
  sum: (values) => values.reduce((a, b) => +a + +b, 0)
}
//Распределение неисправностей по элементам для ячеек определенного типа
function groupbyAgg(data, elColumnName, numColName, aggFunc) {
  const groups = data.reduce((acc, item) => {
    const key = item[elColumnName];
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item[numColName]);
      return acc;    
  }, {});
  return Object.entries(groups).map(([key, values]) => ({
    label: key,
    value: aggFunc(values),    
  }));
}
// Частота поломок отдельного элемента в зависимости от ячейки, в которой он установлен 
// df[df[el_column_name]==element_name].groupby(plate_name).agg({num_col_name: 'sum'}).reset_index().sort_values(by=num_col_name)
function filterGroupbyAggSort(data, elColumnName, elementName, plateName, numColName) {
  // filter
  const filteredData = data.filter(item => item[elColumnName] === elementName);
  // group 
  const groups = filteredData.reduce((acc, item) => {
    const key = item[plateName];
    if (!acc[key]) {
      acc[key] = 0;
    }
    acc[key] += +item[numColName];
    return acc;
  }, {});
  //
  let result = Object.entries(groups).map(([key, sum]) => ({label: key, value: sum}));
  //sort
  result.sort((a, b) => a[numColName] - b[numColName]);
  return result;
}
// Статистика количества ячеек, поступающих на ремонт, по годам
function addYearColumn(data, dateColumnName, newColumnName = 'Год') {
  return data.map(item => {
    const date = new Date(item[dateColumnName]);
    return {
      ...item, [newColumnName]: date.getFullYear((a, b) => a[newColumnName] - b[newColumnName])
    };
  });
}



const graph_1 = groupbyNunique(props.data, 'Наименование', 'Номер')
const graph_2 = filterGroupbySize(props.data, 'Наименование', 'НЩ200-41А', 'Дефектация')
const graph_3 = groupbyAgg(props.data, 'ПКИ', 'Количество',  aggFunctions.sum)
const graph_4 = filterGroupbyAggSort(props.data, 'ПКИ', '1533ЛА1', 'Наименование', 'Количество')
const dataWith = addYearColumn(props.data, 'Дата ремонта')
const graph_5 = groupbyNunique(dataWith, 'Год', 'Номер').sort((a, b) => b['label'] - a['label'])


const graph_8 = [
  {label: '1', value: '111'},
  {label: '1', value: '111'},
  {label: '1', value: '111'},
]

// Инициализация
//onMounted(loadData)
onMounted(() => {
  loadData();  
})

//Реагируем на изменения данных
watch(() => props.data, loadData, { deep: true })
   
</script>

<template>
  
  <div style="margin: 0 150px;">
      <!-- Графики -->
    <h2>{{ $t('faultAnalyze.graph1') }}</h2>
    <div>
      <ChartsTab :sharedData="graph_1" @bar-click="handleBarClick" :xAxisTitle="$t('faultAnalyze.xAxis.name')" :itemCount1="10"/>   
      <h2>{{ $t('faultAnalyze.graph2') }}</h2>
      <ChartsTab :sharedData="graph_2" @bar-click="handleBarClick" :xAxisTitle="$t('faultAnalyze.xAxis.defectTypes')" :itemCount1="10"/>   
      <h2>{{ $t('faultAnalyze.graph3') }}</h2>
      <ChartsTab :sharedData="graph_3" @bar-click="handleBarClick" :itemCount1="25"/>   
      <h2>{{ $t('faultAnalyze.graph4') }}</h2>
      <ChartsTab :sharedData="graph_4" @bar-click="handleBarClick" :xAxisTitle="$t('faultAnalyze.xAxis.element1533')" :itemCount1="1"/>   
      <h2>{{ $t('faultAnalyze.graph5') }}</h2>
      <ChartsTab :sharedData="graph_5" @bar-click="handleBarClick" :itemCount1="1"/>   
    </div>
    <h2>{{ $t('faultAnalyze.graph5_2') }}</h2>
    <ForeCastChart :data="graph_5" />   
    <h2>{{ $t('faultAnalyze.graph6') }}</h2>
    <YearlyComparisonChart :data="dataWith"/>   
    <GroupBreakdowns :sharedData="props.data"/>
  </div>

</template>

<style scoped>
.controls {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.control-group {
  margin-bottom: 15px;
}

.control-group:last-child {
  margin-bottom: 0;
}

.radio-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.radio-options label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.date-filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.date-filters > div {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

select, input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 150px;
}

input[type="date"] {
  min-width: 140px;
}

label {
  font-weight: 600;
  color: #495057;
  min-width: 120px;
}

.reset-btn {
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 100px;
}

.reset-btn:hover {
  background-color: #c82333;
}

.chart-container {
  border: 1px solid #dee2e6;
  padding: 20px;
  border-radius: 8px;
  background-color: white;
  margin-bottom: 20px;
}

.chart-info {
  padding: 15px;
  background-color: #e7f3ff;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.chart-info p {
  margin: 5px 0;
  color: #495057;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 90%;
    max-height: 80vh;
    overflow: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.close-modal {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #999;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

.data-table th,
.data-table td {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
    font-size: 12px;
}

.data-table th {
    background: #f8f9fa;
}

</style>