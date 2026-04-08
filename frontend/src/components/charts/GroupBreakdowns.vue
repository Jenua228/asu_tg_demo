<script setup>
import { ref, computed, onMounted, toRefs } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const props = defineProps({
sharedData: {
    type: Array,
    required: true,
    validator: value => value.every(item =>
        typeof item === 'object' &&
        'label' in item &&
        'value' in item
        )
},
})
const { sharedData } = toRefs(props)
const { sData } = toRefs(props)
let idI = 0;

const rawData = sharedData.value.slice(1, 15).map(item => ({  
  name: item['Номер'],
  type: item['Дефектация'],
  element: item['ПКИ'],
  date: item['Дата ремонта'],
  quantity: +item['Количество']
}))
console.log(rawData)

// const rawData = ref([
// { id: 1, name: 'Станок №1', type: 'Механика', element: 'Подшипник А', date: '2024-01-15', quantity: 2 },
// { id: 2, name: 'Станок №2', type: 'Электроника', element: 'Датчик давления', date: '2024-01-16', quantity: 1 },
// { id: 3, name: 'Станок №1', type: 'Механика', element: 'Подшипник А', date: '2024-01-18', quantity: 1 },
// { id: 4, name: 'Станок №3', type: 'Гидравлика', element: 'Клапан ВК-12', date: '2024-01-20', quantity: 1 },
// { id: 5, name: 'Станок №1', type: 'Электроника', element: 'Контроллер', date: '2024-01-22', quantity: 1 },
// { id: 6, name: 'Станок №2', type: 'Электроника', element: 'Датчик давления', date: '2024-01-25', quantity: 1 },
// { id: 7, name: 'Станок №4', type: 'Механика', element: 'Ремень ГРМ', date: '2024-01-26', quantity: 1 },
// { id: 8, name: 'Станок №2', type: 'Электроника', element: 'Контроллер', date: '2024-01-27', quantity: 1 },
// ])

const groupByField = ref('element')
const chartType = ref('bar')
const highlightIndex = ref(-1)
const sortField = ref('count')
const sortDirection = ref('desc')

// Цветовая палитра
const colors = ref([
'#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', 
'#118AB2', '#EF476F', '#7B68EE', '#FF9A76',
'#f18AB2', '#bF476F', '#aB68EE', '#aF9A76',
'#b18AB2', '#ab476F', '#4B68EE', '#3F9A76'
])

// Размеры графика
const chartWidth = ref(800)
const chartHeight = ref(400)
const barWidth = ref(60)
const margin = ref({ top: 20, right: 150, bottom: 60, left: 50 })

// Агрегированные данные
const aggregatedData = ref([])

// Метод подсчёта статистики
const calculateStats = () => {
const groups = {}

rawData.forEach(record => {
    const key = record[groupByField.value]
    
    if (!groups[key]) {
    groups[key] = {
        name: key,
        count: 0,
        total: 0,
        equipment: new Set()
    }
    }
    
    groups[key].count++
    groups[key].total += record.quantity
    groups[key].equipment.add(record.name)
})

// Преобразуем в массив
aggregatedData.value = Object.values(groups).map(g => ({
    ...g,
    equipmentCount: g.equipment.size
}))

// Сортируем по умолчанию
sortData()
}

// Вычисляемые свойства
const groupByLabel = computed(() => {
const labels = {
    element: 'Элемент',
    type: 'Тип элемента',
    equipment: 'Оборудование'
}
return labels[groupByField.value]
})

const totalCount = computed(() => 
aggregatedData.value.reduce((sum, item) => sum + item.count, 0)
)

const totalQuantity = computed(() => 
aggregatedData.value.reduce((sum, item) => sum + item.total, 0)
)

const uniqueItems = computed(() => aggregatedData.value.length)

const avgPerItem = computed(() => 
uniqueItems.value > 0 ? totalCount.value / uniqueItems.value : 0
)

const topItem = computed(() => 
aggregatedData.value.length > 0 
    ? aggregatedData.value.reduce((max, item) => item.count > max.count ? item : max)
    : { name: '-', count: 0 }
)

// Данные для графика (с процентами)
const chartData = computed(() => {
return aggregatedData.value
    .map(item => ({
    ...item,
    percentage: totalCount.value > 0 ? (item.count / totalCount.value) * 100 : 0
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10) // Ограничиваем для графика
})

// Данные для круговой диаграммы
const pieData = computed(() => {
const data = chartData.value // Для круговой берём меньше сегментов
let cumulativeAngle = 0

return data.map(item => {
    const angle = (item.count / totalCount.value) * 360
    const segment = {
    ...item,
    startAngle: cumulativeAngle,
    endAngle: cumulativeAngle + angle,
    angle: angle
    }
    cumulativeAngle += angle
    return segment
})
})

// Сортировка данных
const sortedData = computed(() => {
return [...aggregatedData.value].sort((a, b) => {
    const multiplier = sortDirection.value === 'asc' ? 1 : -1
    
    if (sortField.value === 'name') {
    return multiplier * a.name.localeCompare(b.name)
    } else if (sortField.value === 'count') {
    return multiplier * (a.count - b.count)
    } else if (sortField.value === 'total') {
    return multiplier * (a.total - b.total)
    }
    return 0
})
})

// Разметка оси Y
const yTicks = computed(() => {
if (chartData.value.length === 0) return []

const maxCount = Math.max(...chartData.value.map(item => item.count))
const tickCount = 5
const tickStep = Math.ceil(maxCount / tickCount)

return Array.from({ length: tickCount + 1 }, (_, i) => ({
    value: i * tickStep,
    label: i * tickStep
}))
})

// Методы для столбчатой диаграммы
const getYPosition = (value) => {
if (chartData.value.length === 0) return 0

const maxCount = Math.max(...chartData.value.map(item => item.count))
const scale = (chartHeight.value - margin.value.top - margin.value.bottom) / maxCount

return chartHeight.value - margin.value.bottom - (value * scale)
}

const getBarX = (index) => {
return margin.value.left + index * (barWidth.value + 20)
}

const getBarY = (value) => {
return getYPosition(value)
}

const getBarHeight = (value) => {
const yPos = getYPosition(value)
return chartHeight.value - margin.value.bottom - yPos
}

// Методы для круговой диаграммы
const getPiePath = (segment, index) => {
const radius = 120
const innerRadius = 60

const startRad = (segment.startAngle * Math.PI) / 180
const endRad = (segment.endAngle * Math.PI) / 180

const x1 = Math.cos(startRad) * radius
const y1 = Math.sin(startRad) * radius
const x2 = Math.cos(endRad) * radius
const y2 = Math.sin(endRad) * radius

const xInner1 = Math.cos(startRad) * innerRadius
const yInner1 = Math.sin(startRad) * innerRadius
const xInner2 = Math.cos(endRad) * innerRadius
const yInner2 = Math.sin(endRad) * innerRadius

const largeArcFlag = segment.angle > 180 ? 1 : 0

return [
    `M ${xInner1} ${yInner1}`,
    `L ${x1} ${y1}`,
    `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
    `L ${xInner2} ${yInner2}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${xInner1} ${yInner1}`,
    'Z'
].join(' ')
}

// Вспомогательные методы
const toggleChartType = () => {
chartType.value = chartType.value === 'bar' ? 'pie' : 'bar'
}

const sortBy = (field) => {
if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
} else {
    sortField.value = field
    sortDirection.value = 'desc'
}
}

const sortData = () => {
// Сортируем aggregatedData.value
aggregatedData.value.sort((a, b) => {
    const multiplier = sortDirection.value === 'asc' ? 1 : -1
    
    if (sortField.value === 'name') {
    return multiplier * a.name.localeCompare(b.name)
    } else if (sortField.value === 'count') {
    return multiplier * (a.count - b.count)
    } else if (sortField.value === 'total') {
    return multiplier * (a.total - b.total)
    }
    return 0
})
}

const showLegend = computed(() => chartData.value.length > 3)

// Инициализация
onMounted(() => {
calculateStats()
})

</script>
  
<template>
<div class="failure-analysis">
    <!-- Фильтры -->
    <div class="controls">
    <select v-model="groupByField" @change="calculateStats">
        <option value="element">{{ $t('groupBreakdowns.byElements') }}</option>
        <option value="type">{{ $t('groupBreakdowns.byElementTypes') }}</option>
        <option value="equipment">{{ $t('groupBreakdowns.byEquipment') }}</option>
    </select>
    
    <button @click="toggleChartType">
        {{ chartType === 'bar' ?  $t('groupBreakdowns.showPie') :  $t('groupBreakdowns.showBar')  }}
    </button>
    </div>

    <!-- Таблица с данными -->
    <div class="stats-table">
    <h3>{{ $t('groupBreakdowns.statsTitle') }}</h3>
    <table>
        <thead>
        <tr>
            <th @click="sortBy('name')" class="sortable">
              {{ $t(`groupBreakdowns.groupByLabels.${groupByField}`) }}
            <span v-if="sortField === 'name'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th @click="sortBy('count')" class="sortable">
              {{$t('groupBreakdowns.breakdowns')}} 
            <span v-if="sortField === 'count'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th @click="sortBy('total')" class="sortable">
              {{$t('groupBreakdowns.replaced')}}  
            <span v-if="sortField === 'total'">{{ sortDirection === 'asc' ? '▲' : '▼' }}</span>
            </th>
            <th>    {{$t('groupBreakdowns.share')}}  </th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, index) in sortedData" 
            :key="item.name"
            @mouseover="highlightIndex = index"
            @mouseleave="highlightIndex = -1">
            <td>{{ item.name }}</td>
            <td>{{ item.count }}</td>
            <td>{{ item.total }}</td>
            <td>
            <div class="percentage-bar">
                <div class="bar-fill" :style="{ width: item.percentage + '%' }"></div>
                <span>{{ item.percentage }}%</span>
            </div>
            </td>
        </tr>
        </tbody>
    </table>
    </div>

    <!-- Столбчатая диаграмма на SVG -->
    <div v-if="chartType === 'bar'" class="chart-container">
    <h3>{{ $t('groupBreakdowns.chartTitle') }}</h3>
    <svg :width="chartWidth" :height="chartHeight" class="bar-chart">
        <!-- Оси -->
        <line x1="50" y1="20" :x2="50" :y2="chartHeight - 30" stroke="#666" stroke-width="2"/>
        <line x1="50" :y1="chartHeight - 30" :x2="chartWidth - 20" :y2="chartHeight - 30" stroke="#666" stroke-width="2"/>
        
        <!-- Подписи оси Y -->
        <template v-for="(tick, i) in yTicks" :key="'ytick-' + i">
        <text x="40" :y="getYPosition(tick.value)" text-anchor="end" fill="#666" font-size="12">
            {{ tick.label }}
        </text>
        <line x1="45" :y1="getYPosition(tick.value)" x2="50" :y2="getYPosition(tick.value)" stroke="#ddd"/>
        </template>
        
        <!-- Столбцы -->
        <g v-for="(item, index) in chartData" :key="item.name">
        <!-- Столбец -->
        <rect
            :x="getBarX(index)"
            :y="getBarY(item.count)"
            :width="barWidth"
            :height="getBarHeight(item.count)"
            :fill="highlightIndex === index ? '#ff6b6b' : colors[index % colors.length]"
            @mouseover="highlightIndex = index"
            @mouseleave="highlightIndex = -1"
            class="bar"
            :class="{ highlighted: highlightIndex === index }"
        />
        
        <!-- Подпись значения -->
        <text
            :x="getBarX(index) + barWidth / 2"
            :y="getBarY(item.count) - 5"
            text-anchor="middle"
            fill="#333"
            font-size="12"
        >
            {{ item.count }}
        </text>
        
        <!-- Подпись категории -->
        <text
            :x="getBarX(index) + barWidth / 2"
            :y="chartHeight - 15"
            text-anchor="middle"
            fill="#666"
            font-size="11"
            transform="rotate(-45, {{getBarX(index) + barWidth / 2}}, {{chartHeight - 15}})"
        >
            {{ item.name }}
        </text>
        </g>
        
        <!-- Легенда -->
        <g v-if="showLegend">
        <rect :x="chartWidth*0.75" y="20" width="200" height="80" fill="white" stroke="#ddd"/>
        <text :x="chartWidth*0.8" y="40" font-size="12" font-weight="bold">{{ $t('groupBreakdowns.legend') }}</text>
        <circle v-for="(color, i) in colors.slice(0, 3)" 
                :key="'legend-' + i"
                :cx="chartWidth*0.8" 
                :cy="55 + i * 15" 
                r="5" 
                :fill="color"/>
        <text v-for="(color, i) in colors.slice(0, 3)" 
                :key="'legend-text-' + i"
                :x="chartWidth*0.85" 
                :y="58 + i * 15" 
                font-size="11">
            {{ i === 0 ? $t('groupBreakdowns.highFrequency') : i === 1 ? $t('groupBreakdowns.mediumFrequency') : $t('groupBreakdowns.lowFrequency') }}
        </text>
        </g>
    </svg>
    </div>

    <!-- Круговая диаграмма на SVG -->
    <div v-else class="chart-container">
    <h3>{{ $t('groupBreakdowns.pieTitle') }}</h3>
    <svg :width="chartWidth" :height="chartHeight" class="pie-chart">
        <!-- Круговая диаграмма -->
        <g :transform="`translate(${chartWidth/2}, ${chartHeight/2})`">
        <path
            v-for="(item, index) in pieData"
            :key="item.name"
            :d="getPiePath(item, index)"
            :fill="colors[index % colors.length]"
            @mouseover="highlightIndex = index"
            @mouseleave="highlightIndex = -1"
            :class="{ highlighted: highlightIndex === index }"
            class="pie-segment"
        />
        
        <!-- Центральный круг -->
        <circle cx="0" cy="0" r="60" fill="white"/>
        <text x="0" y="-5" text-anchor="middle" font-size="16" font-weight="bold">
            {{ totalCount }}
        </text>
        <text x="0" y="15" text-anchor="middle" font-size="12" fill="#666">
          {{$t('groupBreakdowns.summaryCards.totalBreakdowns').slice(0,6)}}
        </text>
        </g>
        
        <!-- Легенда для круговой -->
        <g :transform="`translate(${chartWidth - 200}, 50)`">
        <rect v-for="(item, index) in pieData.slice(0, 5)" 
                :key="'legend-pie-' + index"
                x="0" 
                :y="index * 25" 
                width="15" 
                height="15" 
                :fill="colors[index % colors.length]"/>
        <text v-for="(item, index) in pieData.slice(0, 5)" 
                :key="'legend-text-pie-' + index"
                x="20" 
                :y="12 + index * 25" 
                font-size="11">
            {{ item.name }} ({{ item.percentage.toFixed(1) }}%)
        </text>
        </g>
    </svg>
    </div>

    <!-- Сводная информация -->
    <div class="summary">
    <h3> {{$t('groupBreakdowns.pieTitle')}}</h3>
    <div class="summary-grid">
        <div class="summary-item">
        <div class="summary-value">{{ totalCount }}</div>
        <div class="summary-label">{{$t('groupBreakdowns.summaryCards.totalBreakdowns')}}</div>
        </div>
        <div class="summary-item">
        <div class="summary-value">{{ uniqueItems }}</div>
        <div class="summary-label">{{$t('groupBreakdowns.summaryCards.uniqueItems')}} {{ groupByLabel.toLowerCase() }}</div>
        </div>
        <div class="summary-item">
        <div class="summary-value">{{ avgPerItem.toFixed(1) }}</div>
        <div class="summary-label">{{$t('groupBreakdowns.summaryCards.avgPerItem')}}</div>
        </div>
        <div class="summary-item">
        <div class="summary-value">{{ topItem.name }}</div>
        <div class="summary-label">{{$t('groupBreakdowns.summaryCards.leader')}} ({{ topItem.count }})</div>
        </div>
    </div>
    </div>
</div>
</template>

  <style scoped>
  .failure-analysis {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Arial, sans-serif;
  }
  
  .controls {
    display: flex;
    gap: 15px;
    margin-bottom: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  select, button {
    padding: 10px 15px;
    font-size: 14px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    transition: all 0.3s;
  }
  
  button:hover {
    background: #f0f0f0;
  }
  
  .stats-table {
    margin: 30px 0;
    overflow-x: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 8px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  th, td {
    border-bottom: 1px solid #e0e0e0;
    padding: 14px 16px;
    text-align: left;
  }
  
  th {
    background: #2c3e50;
    color: white;
    font-weight: 600;
    position: sticky;
    top: 0;
  }
  
  .sortable {
    cursor: pointer;
    user-select: none;
  }
  
  .sortable:hover {
    background: #34495e;
  }
  
  tr:hover {
    background: #f8f9fa;
  }
  
  .percentage-bar {
    position: relative;
    height: 24px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4ECDC4, #44A08D);
    transition: width 0.5s ease;
  }
  
  .percentage-bar span {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
  }
  
  .chart-container {
    margin: 40px 0;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  }
  
  .bar-chart, .pie-chart {
    background: white;
    border-radius: 8px;
  }
  
  .bar {
    transition: all 0.3s;
    cursor: pointer;
  }
  
  .bar:hover, .pie-segment:hover {
    opacity: 0.8;
    transform: scale(1.05);
  }
  
  .highlighted {
    filter: drop-shadow(0 0 8px rgba(0,0,0,0.3));
  }
  
  .summary {
    margin-top: 40px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
  }
  
  .summary h3 {
    margin-top: 0;
    color: white;
  }
  
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }
  
  .summary-item {
    text-align: center;
    padding: 20px;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
  }
  
  .summary-value {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 8px;
  }
  
  .summary-label {
    font-size: 14px;
    opacity: 0.9;
  }
  
  @media (max-width: 768px) {
    .chart-container {
      overflow-x: auto;
    }
    
    .bar-chart, .pie-chart {
      min-width: 600px;
    }
    
    .summary-grid {
      grid-template-columns: 1fr;
    }
  }
  </style>