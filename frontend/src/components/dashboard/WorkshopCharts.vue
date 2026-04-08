<template>
  <div class="charts-container">
    <!-- Панель управления диаграммами -->
    <div class="charts-control-panel">
      <h2>{{ $t('workshop.workshopAnalytics') }}</h2>
      
      <!-- <div class="controls-row">
        <div class="control-group">
          <label>Период:</label>
          <select v-model="timeRange" class="control-select">
            <option value="day">День</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
            <option value="quarter">Квартал</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>Группировка:</label>
          <select v-model="groupBy" class="control-select">
            <option value="workshop">По цехам</option>
            <option value="section">По участкам</option>
            <option value="type">По типам</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>Показать:</label>
          <select v-model="showTopN" class="control-select">
            <option :value="10">Топ-10</option>
            <option :value="20">Топ-20</option>
            <option :value="30">Топ-30</option>
            <option :value="0">Все</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>Тип графика:</label>
          <div class="chart-type-toggle">
            <button 
              class="type-btn" 
              :class="{ active: chartType === 'bar' }"
              @click="chartType = 'bar'"
              title="Столбчатая"
            >
              █
            </button>
            <button 
              class="type-btn" 
              :class="{ active: chartType === 'line' }"
              @click="chartType = 'line'"
              title="Линейная"
            >
              ─
            </button>
            <button 
              class="type-btn" 
              :class="{ active: chartType === 'heatmap' }"
              @click="chartType = 'heatmap'"
              title="Тепловая карта"
            >
              ■
            </button>
            <button 
              class="type-btn" 
              :class="{ active: chartType === 'scatter' }"
              @click="chartType = 'scatter'"
              title="Точечная"
            >
              •
            </button>
          </div>
        </div>
      </div> -->
      
      <div class="search-filter">
        <input
          v-model="chartSearch"
          type="text"
          :placeholder="$t('workshop.search')"
          class="search-input"
        />
        <button 
          class="btn-reset"
          @click="resetFilters"
          title="Сбросить фильтры"
        >
          {{ $t('workshop.reset') }}
        </button>
      </div>
    </div>

    <!-- Основной контейнер для диаграмм -->
    <div class="charts-main-container">
      <!-- Левая колонка: Основные метрики -->
      <div class="metrics-sidebar">
        <div class="metric-card" :style="{ borderColor: totalColor }">
          <div class="metric-header">
            <h3>{{ $t('workshop.totalLoad') }}</h3>
            <div class="metric-trend" :class="trendClass">
              {{ trendValue > 0 ? '+' : '' }}{{ trendValue }}%
            </div>
          </div>
          <div class="metric-value" :style="{ color: totalColor }">
            {{ totalWorkload.toFixed(1) }}%
          </div>
          <div class="metric-progress">
            <div 
              class="progress-fill" 
              :style="{ 
                width: `${totalWorkload}%`,
                background: totalColor
              }"
            ></div>
          </div>
          <div class="metric-subtext">
            <span>{{ $t('workshop.workshops') }} {{ workshops.length }}</span>
            <span>{{ $t('workshop.regions') }} {{ totalSections }}</span>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <h3>{{ $t('workshop.loadDistribution') }}</h3>
          </div>
          <div class="distribution-stats">
            <div class="dist-item" v-for="dist in workloadDistribution" :key="dist.label">
              <div class="dist-label">
                <div class="dist-color" :style="{ backgroundColor: dist.color }"></div>
                {{ dist.label }}
              </div>
              <div class="dist-value">{{ dist.count }} ({{ dist.percentage }}%)</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <h3>{{ $t('workshop.Top') }}</h3>
          </div>
          <div class="top-list">
            <div 
              v-for="(workshop, index) in topWorkshops" 
              :key="workshop.id"
              class="top-item"
              @click="highlightWorkshop(workshop)"
              :class="{ highlighted: highlightedWorkshop === workshop.id }"
            >
              <div class="top-rank">#{{ index + 1 }}</div>
              <div class="top-name">{{ $t('dashboard2.columns.tcr') }}{{ workshop.name.slice(3) }}</div>
              <div 
                class="top-value"
                :style="{ color: getColorForWorkload(workshop.workload) }"
              >
                {{ workshop.workload }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Центральная область: Основная диаграмма -->
      <div class="main-chart-area">
        <div class="chart-header">
          <h3>{{ $t('workshop.chartTitle') }}</h3>
          <div class="chart-actions">
            <button 
              class="action-btn"
              @click="exportChart"
              title="Экспортировать"
            >
              📊
            </button>
            <button 
              class="action-btn"
              @click="toggleFullscreen"
              title="На весь экран"
            >
              ⛶
            </button>
          </div>
        </div>
        
        <!-- Контейнер для SVG диаграммы -->
        <div class="chart-container" ref="chartContainer">
          <!-- Адаптивная SVG диаграмма -->
          <svg 
            ref="chartSvg"
            class="main-chart"
            :width="chartWidth"
            :height="chartHeight"
            @mousemove="handleMouseMove"
            @mouseleave="handleMouseLeave"
          >
            <!-- Сетка -->
            <g class="grid-lines">
              <line 
                v-for="i in 5" 
                :key="`grid-${i}`"
                :x1="margin.left" 
                :y1="margin.top + (i * (innerHeight / 5))"
                :x2="chartWidth - margin.right"
                :y2="margin.top + (i * (innerHeight / 5))"
                stroke="#eee"
                stroke-width="1"
              />
            </g>
            
            <!-- Оси -->
            <g class="axes">
              <!-- Ось Y -->
              <line
                :x1="margin.left"
                :y1="margin.top"
                :x2="margin.left"
                :y2="chartHeight - margin.bottom"
                stroke="#333"
                stroke-width="2"
              />
              
              <!-- Ось X -->
              <line
                :x1="margin.left"
                :y1="chartHeight - margin.bottom"
                :x2="chartWidth - margin.right"
                :y2="chartHeight - margin.bottom"
                stroke="#333"
                stroke-width="2"
              />
            </g>
            
            <!-- Подписи оси Y -->
            <g class="y-axis-labels">
              <text
                v-for="i in 6"
                :key="`y-label-${i}`"
                :x="margin.left - 10"
                :y="margin.top + ((i-1) * (innerHeight / 5))"
                text-anchor="end"
                dominant-baseline="middle"
                font-size="12"
                fill="#666"
              >
                {{ 100 - ((i-1) * 20) }}%
              </text>
            </g>
            
            <!-- Данные диаграммы -->
            <g class="chart-data">
              <!-- Для столбчатой диаграммы -->
              <g v-if="chartType === 'bar' && groupBy === 'workshop'">
                <rect
                  v-for="(workshop, index) in visibleData"
                  :key="workshop.id"
                  :x="getBarX(index)"
                  :y="getBarY(workshop.workload)"
                  :width="barWidth"
                  :height="innerHeight - getBarY(workshop.workload)"
                  :fill="getBarColor(workshop)"
                  :class="{ highlighted: highlightedWorkshop === workshop.id }"
                  @click="selectWorkshop(workshop)"
                  @mouseenter="showTooltip(workshop, $event)"
                />
                
                <!-- Подписи под столбцами -->
                <g class="bar-labels">
                  <text
                    v-for="(workshop, index) in visibleData"
                    :key="`label-${workshop.id}`"
                    :x="getBarX(index) + barWidth / 2"
                    :y="chartHeight - margin.bottom + 40"
                    text-anchor="middle"
                    font-size="11"
                    fill="#666"
                    class="bar-label"
                    @click="selectWorkshop(workshop)"
                  >
                    TRC № {{ workshop.id }}
                  </text>
                  <text
                    v-for="(workshop, index) in visibleData"
                    :key="`value-${workshop.id}`"
                    :x="getBarX(index) + barWidth / 2"
                    :y="getBarY(workshop.workload) - 5"
                    text-anchor="middle"
                    font-size="11"
                    font-weight="bold"
                    :fill="getBarColor(workshop)"
                    class="bar-value"
                  >
                    {{ workshop.workload }}%
                  </text>
                </g>
              </g>
              
              <!-- Для тепловой карты -->
              <g v-if="chartType === 'heatmap'" class="heatmap">
                <rect
                  v-for="cell in heatmapCells"
                  :key="cell.key"
                  :x="cell.x"
                  :y="cell.y"
                  :width="cellSize"
                  :height="cellSize"
                  :fill="getHeatmapColor(cell.value)"
                  :stroke="highlightedWorkshop === cell.workshopId ? '#333' : '#fff'"
                  stroke-width="highlightedWorkshop === cell.workshopId ? 2 : 1"
                  @click="selectWorkshop({ id: cell.workshopId, name: cell.workshopName })"
                  @mouseenter="showHeatmapTooltip(cell, $event)"
                />
                
                <!-- Подписи для тепловой карты -->
                <g class="heatmap-labels">
                  <text
                    v-for="(label, index) in heatmapXLabels"
                    :key="`x-label-${index}`"
                    :x="margin.left + index * cellSize + cellSize / 2"
                    :y="chartHeight - margin.bottom + 20"
                    text-anchor="middle"
                    font-size="11"
                    fill="#666"
                    transform="rotate(-45, 
                      ${margin.left + index * cellSize + cellSize / 2}, 
                      ${chartHeight - margin.bottom + 20})"
                  >
                    {{ label }}
                  </text>
                </g>
              </g>
              
              <!-- Для линейной диаграммы -->
              <g v-if="chartType === 'line'" class="line-chart">
                <path
                  :d="linePath"
                  fill="none"
                  stroke="#4CAF50"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                
                <!-- Точки на линии -->
                <circle
                  v-for="(point, index) in linePoints"
                  :key="`point-${index}`"
                  :cx="point.x"
                  :cy="point.y"
                  r="4"
                  fill="#4CAF50"
                  stroke="white"
                  stroke-width="2"
                  @mouseenter="showLineTooltip(point, $event)"
                />
              </g>
            </g>
            
            <!-- Легенда -->
            <g class="legend" :transform="`translate(${chartWidth - margin.right - 150}, ${margin.top})`">
              <rect width="150" height="120" fill="white" stroke="#ddd" stroke-width="1" />
              <text x="10" y="20" font-size="12" font-weight="bold">{{ $t('workshop.legend') }}</text>
              <g v-for="(item, index) in legendItems" :key="index" :transform="`translate(10, ${35 + index * 20})`">
                <rect width="12" height="12" :fill="item.color" />
                <text x="20" y="10" font-size="11" fill="#666">{{ item.label }}</text>
              </g>
            </g>
            
            <!-- Интерактивная подсказка -->
            <g 
              v-if="tooltip.visible" 
              class="tooltip"
              :transform="`translate(${tooltip.x}, ${tooltip.y})`"
            >
              <rect 
                width="tooltip.width" 
                height="tooltip.height" 
                rx="4" 
                ry="4" 
                fill="white" 
                stroke="#ddd"
                stroke-width="1"
                filter="url(#shadow)"
              />
              <text x="10" y="20" font-size="12" font-weight="bold">{{ tooltip.title }}</text>
              <text x="10" y="40" font-size="11" fill="#666">{{ $t('workshop.Loading') }} {{ tooltip.value }}%</text>
              <text v-if="tooltip.sections" x="10" y="60" font-size="11" fill="#666">
                {{ $t('workshop.regions') }} {{ tooltip.sections }}
              </text>
            </g>
            
            <!-- Фильтр для тени -->
            <defs>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.2)"/>
              </filter>
            </defs>
          </svg>
          
          <!-- Полоса прокрутки для большого количества данных -->
          <div v-if="showScrollbar" class="chart-scrollbar">
            <input
              type="range"
              v-model="scrollPosition"
              :min="0"
              :max="scrollMax"
              class="scrollbar"
              @input="handleScroll"
            />
          </div>
        </div>
        
        <!-- Легенда загрузки -->
        <div class="workload-legend">
          <div class="legend-title">{{ $t('workshop.LoadScale') }}</div>
          <div class="legend-gradient">
            <div 
              v-for="i in 5" 
              :key="i"
              class="gradient-segment"
              :style="{ backgroundColor: getColorForWorkload(i * 20) }"
            ></div>
          </div>
          <div class="legend-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <!-- Правая колонка: Фильтры и детали -->
      <div class="filters-sidebar">
        <div class="filter-section">
          <h4>{{ $t('workshop.filters') }}</h4>
          <div class="filter-slider">
            <div class="slider-labels">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
            <input
              type="range"
              v-model="workloadRange[0]"
              min="0"
              max="100"
              class="range-slider"
              @input="updateWorkloadFilter"
            />
            <input
              type="range"
              v-model="workloadRange[1]"
              min="0"
              max="100"
              class="range-slider"
              @input="updateWorkloadFilter"
            />
            <div class="slider-values">
              {{ workloadRange[0] }}% - {{ workloadRange[1] }}%
            </div>
          </div>
        </div>
        
        <div class="filter-section">
          <h4>{{ $t('workshop.quickFilters') }}</h4>
          <div class="quick-filters">
            <button 
              v-for="filter in quickFilters"
              :key="filter.label"
              class="quick-filter-btn"
              :class="{ active: activeQuickFilter === filter.label }"
              @click="applyQuickFilter(filter)"
            >
              {{ filter.label }}
              <span class="filter-count">{{ filter.count }}</span>
            </button>
          </div>
        </div>
        
        <div class="filter-section">
          <h4>{{ $t('workshop.selectedWorkshop') }}</h4>
          <div v-if="selectedWorkshop" class="selected-workshop-details">
            <div class="selected-header">
              <h5>{{ selectedWorkshop.name }}</h5>
              <div class="selected-workload" :style="{ color: getColorForWorkload(selectedWorkshop.workload) }">
                {{ selectedWorkshop.workload }}%
              </div>
            </div>
            <div class="selected-stats">
              <div class="stat">
                <span class="label">{{ $t('workshop.regions') }}</span>
                <span class="value">{{ selectedWorkshop.sections.length }}</span>
              </div>
              <div class="stat">
                <span class="label">{{ $t('workshopdetail.war') }}</span>
                <span class="value">
                  {{ Math.round((selectedWorkshop.warehouse.currentStock / selectedWorkshop.warehouse.capacity) * 100) }}%
                </span>
              </div>
            </div>
            <button class="btn-view-details" @click="$emit('workshop-select', selectedWorkshop)">
              {{ $t('workshopdetail.learn') }}
            </button>
          </div>
          <div v-else class="no-selection">
            <p>{{ $t('workshopdetail.sel') }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Дополнительные мини-диаграммы -->
    <div class="mini-charts-grid">
      <div class="mini-chart-card">
        <h4>{{ $t('workshop.distr') }}</h4>
        <div class="mini-chart-container">
          <svg :height="100">
            <rect
              v-for="(section, index) in allSections"
              :key="section.id"
              :x="index * 15"
              :y="100 - (section.workload)"
              width="12"
              :height="section.workload"
              :fill="getColorForWorkload(section.workload)"
              @mouseenter="highlightSection(section)"
            />
          </svg>
          <div class="mini-chart-label">
            {{ allSections.length }} {{ $t('workshop.regions2') }}
          </div>
        </div>
      </div>
      
      <!-- <div class="mini-chart-card">
        <h4>Тенденции загрузки</h4>
        <div class="trend-chart">
          <div class="trend-indicator" :class="trendClass">
            {{ trendValue > 0 ? '↑' : '↓' }}
          </div>
          <div class="trend-value">{{ Math.abs(trendValue) }}%</div>
          <div class="trend-label">
            {{ trendValue > 0 ? 'Рост' : 'Снижение' }} за {{ timeRangeLabel }}
          </div>
        </div>
      </div> -->
      
      <!-- <div class="mini-chart-card">
        <h4>Плотность данных</h4>
        <div class="density-chart">
          <div class="density-bar" v-for="i in 10" :key="i">
            <div 
              class="density-fill"
              :style="{
                height: `${Math.random() * 100}%`,
                backgroundColor: `hsl(${200 + i * 10}, 70%, 50%)`
              }"
            ></div>
          </div>
        </div>
        <div class="density-info">
          Высокая плотность данных
        </div>
      </div> -->
    </div>

    <!-- Полноэкранный режим -->
    <div v-if="isFullscreen" class="fullscreen-overlay" @click="toggleFullscreen">
      <div class="fullscreen-content" @click.stop>
        <div class="fullscreen-header">
          <h2>{{ $t('workshop.workshopLoad') }}</h2>
          <button class="btn-close-fullscreen" @click="toggleFullscreen">✕</button>
        </div>
        <div class="fullscreen-chart">
          <!-- Здесь будет увеличенная версия диаграммы -->
          <div class="fullscreen-placeholder">
            <p>{{ $t('workshop.full') }}</p>
            <p>{{ $t('workshop.dep') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()


const props = defineProps({
  workshops: {
    type: Array,
    default: () => []
  },
  totalWorkload: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['workshop-select'])

// Состояния управления
const timeRange = ref('month')
const groupBy = ref('workshop')
const showTopN = ref(10)
const chartType = ref('bar')
const chartSearch = ref('')
const highlightedWorkshop = ref(null)
const selectedWorkshop = ref(null)
const isFullscreen = ref(false)
const scrollPosition = ref(0)

// Фильтры
const workloadRange = ref([0, 100])
const activeQuickFilter = ref(null)

// Размеры диаграммы
const chartContainer = ref(null)
const chartSvg = ref(null)
const chartWidth = ref(800)
const chartHeight = ref(400)
const margin = ref({ top: 40, right: 180, bottom: 60, left: 60 })

// Интерактивность
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  value: 0,
  sections: 0,
  width: 120,
  height: 80
})

// Вычисляемые свойства
const innerWidth = computed(() => chartWidth.value - margin.value.left - margin.value.right)
const innerHeight = computed(() => chartHeight.value - margin.value.top - margin.value.bottom)

const totalSections = computed(() => {
  return props.workshops.reduce((sum, workshop) => sum + workshop.sections.length, 0)
})

const allSections = computed(() => {
  return props.workshops.flatMap(workshop => 
    workshop.sections.map(section => ({
      ...section,
      workshopId: workshop.id,
      workshopName: workshop.name
    }))
  )
})

// Фильтрация и сортировка данных
const filteredWorkshops = computed(() => {
  let result = [...props.workshops]
  
  // Поиск
  if (chartSearch.value) {
    const query = chartSearch.value.toLowerCase()
    result = result.filter(workshop => 
      workshop.name.toLowerCase().includes(query) ||
      workshop.sections.some(section => 
        section.name.toLowerCase().includes(query)
      )
    )
  }
  
  // Фильтр по диапазону загрузки
  result = result.filter(workshop => 
    workshop.workload >= workloadRange.value[0] && 
    workshop.workload <= workloadRange.value[1]
  )
  
  // Сортировка по загрузке (по убыванию)
  return result.sort((a, b) => b.workload - a.workload)
})

// Видимые данные (с учетом ограничения Top-N и скролла)
const visibleData = computed(() => {
  let data = filteredWorkshops.value
  
  // Применяем Top-N если выбран
  if (showTopN.value > 0) {
    data = data.slice(0, showTopN.value)
  }
  
  // Применяем скроллинг
  const start = scrollPosition.value
  const end = start + maxVisibleItems.value
  return data.slice(start, end)
})

const maxVisibleItems = computed(() => {
  if (chartType.value === 'heatmap') return 50
  if (innerWidth.value < 400) return 5
  if (innerWidth.value < 600) return 8
  if (innerWidth.value < 800) return 12
  return 15
})

const scrollMax = computed(() => {
  return Math.max(0, filteredWorkshops.value.length - maxVisibleItems.value)
})

const showScrollbar = computed(() => {
  return filteredWorkshops.value.length > maxVisibleItems.value
})

// Работа с диаграммой
const barWidth = computed(() => {
  const itemCount = visibleData.value.length
  if (itemCount === 0) return 0
  return Math.max(10, Math.min(50, innerWidth.value / itemCount - 10))
})

const getBarX = (index) => {
  return margin.value.left + index * (3*barWidth.value)
}

const getBarY = (value) => {
  return margin.value.top + innerHeight.value - (value / 100) * innerHeight.value
}

const getBarColor = (workshop) => {
  if (highlightedWorkshop.value === workshop.id) {
    return '#333'
  }
  if (selectedWorkshop.value?.id === workshop.id) {
    return '#2196F3'
  }
  return getColorForWorkload(workshop.workload)
}

const getColorForWorkload = (workload) => {
  if (workload >= 90) return '#d32f2f'
  if (workload >= 80) return '#f57c00'
  if (workload >= 70) return '#fbc02d'
  if (workload >= 60) return '#afb42b'
  if (workload >= 50) return '#388e3c'
  if (workload >= 40) return '#0288d1'
  if (workload >= 30) return '#1976d2'
  if (workload >= 20) return '#303f9f'
  return '#5c6bc0'
}

// Статистика и метрики
const totalColor = computed(() => {
  return getColorForWorkload(props.totalWorkload)
})

const workloadDistribution = computed(() => {
  const ranges = [
    { label: '0-30%', min: 0, max: 30, color: '#5c6bc0' },
    { label: '30-60%', min: 30, max: 60, color: '#388e3c' },
    { label: '60-80%', min: 60, max: 80, color: '#fbc02d' },
    { label: '80-100%', min: 80, max: 100, color: '#d32f2f' }
  ]
  
  return ranges.map(range => {
    const count = props.workshops.filter(w => 
      w.workload >= range.min && w.workload < range.max
    ).length
    const percentage = props.workshops.length > 0 
      ? Math.round((count / props.workshops.length) * 100) 
      : 0
    
    return {
      ...range,
      count,
      percentage
    }
  })
})

const topWorkshops = computed(() => {
  return [...props.workshops]
    .sort((a, b) => b.workload - a.workload)
    .slice(0, 5)
})

const chartTitle = computed(() => {
  const typeLabels = {
    bar: 'Столбчатая диаграмма',
    line: 'Линейный график',
    heatmap: 'Тепловая карта',
    scatter: 'Точечная диаграмма'
  }
  
  const groupLabels = {
    workshop: 'цехов',
    section: 'участков',
    type: 'типов'
  }
  
  return `${typeLabels[chartType.value]} загрузки ${groupLabels[groupBy.value]}`
})

const quickFilters = computed(() => [
  { label: t('dashboard.filters.critical'), min: 90, color: '#d32f2f', count: props.workshops.filter(w => w.workload >= 90).length },
  { label: t('dashboard.filters.high'), min: 80, color: '#f57c00', count: props.workshops.filter(w => w.workload >= 80 && w.workload < 90).length },
  { label: t('dashboard.filters.average'), min: 60, max: 80, color: '#fbc02d', count: props.workshops.filter(w => w.workload >= 60 && w.workload < 80).length },
  { label: t('dashboard.filters.low'), min: 0, max: 60, color: '#388e3c', count: props.workshops.filter(w => w.workload < 60).length }
])

const trendValue = computed(() => {
  // Здесь должна быть логика расчета тренда из реальных данных
  // Для примепа возвращаем случайное значение
  return Math.round(Math.random() * 20 - 10)
})

const trendClass = computed(() => {
  return trendValue.value > 0 ? 'positive' : 'negative'
})

const timeRangeLabel = computed(() => {
  const labels = {
    day: 'день',
    week: 'неделю',
    month: 'месяц',
    quarter: 'квартал'
  }
  return labels[timeRange.value]
})

// Тепловая карта
const heatmapCells = computed(() => {
  if (chartType.value !== 'heatmap') return []
  
  const columns = 10
  const rows = Math.ceil(filteredWorkshops.value.length / columns)
  const cellSize = Math.min(40, innerWidth.value / columns)
  
  return filteredWorkshops.value.map((workshop, index) => {
    const col = index % columns
    const row = Math.floor(index / columns)
    
    return {
      key: workshop.id,
      x: margin.value.left + col * cellSize,
      y: margin.value.top + row * cellSize,
      value: workshop.workload,
      workshopId: workshop.id,
      workshopName: workshop.name,
      cellSize
    }
  })
})

const getHeatmapColor = (value) => {
  const intensity = Math.min(1, value / 100)
  const hue = 120 - (intensity * 120) // От зеленого к красному
  return `hsl(${hue}, 80%, 50%)`
}

// Линейная диаграмма
const linePoints = computed(() => {
  return visibleData.value.map((workshop, index) => ({
    x: margin.value.left + (index / (visibleData.value.length - 1)) * innerWidth.value,
    y: getBarY(workshop.workload),
    value: workshop.workload,
    name: workshop.name
  }))
})

const linePath = computed(() => {
  if (linePoints.value.length === 0) return ''
  
  const points = linePoints.value
  let path = `M ${points[0].x} ${points[0].y}`
  
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1]
    const curr = points[i]
    const cp1x = prev.x + (curr.x - prev.x) / 3
    const cp2x = prev.x + 2 * (curr.x - prev.x) / 3
    path += ` C ${cp1x} ${prev.y}, ${cp2x} ${curr.y}, ${curr.x} ${curr.y}`
  }
  
  return path
})

// Легенда
const legendItems = computed(() => {
  return workloadDistribution.value.map(dist => ({
    color: dist.color,
    label: `${dist.label} (${dist.count})`
  }))
})

// Методы
const selectWorkshop = (workshop) => {
  selectedWorkshop.value = workshop
  highlightedWorkshop.value = workshop.id
  emit('workshop-select', workshop)
}

const highlightWorkshop = (workshop) => {
  highlightedWorkshop.value = workshop.id
}

const highlightSection = (section) => {
  // Находим цех, к которому принадлежит участок
  const workshop = props.workshops.find(w => w.id === section.workshopId)
  if (workshop) {
    highlightWorkshop(workshop)
  }
}

const showTooltip = (workshop, event) => {
  const svgRect = chartSvg.value.getBoundingClientRect()
  const point = chartSvg.value.createSVGPoint()
  point.x = event.clientX - svgRect.left
  point.y = event.clientY - svgRect.top
  
  tooltip.value = {
    visible: true,
    x: point.x + 10,
    y: point.y - 40,
    title: workshop.name,
    value: workshop.workload,
    sections: workshop.sections.length,
    width: 120,
    height: 80
  }
}

const showHeatmapTooltip = (cell, event) => {
  const svgRect = chartSvg.value.getBoundingClientRect()
  const point = chartSvg.value.createSVGPoint()
  point.x = event.clientX - svgRect.left
  point.y = event.clientY - svgRect.top
  
  tooltip.value = {
    visible: true,
    x: point.x + 10,
    y: point.y - 40,
    title: cell.workshopName,
    value: cell.value,
    width: 120,
    height: 60
  }
}

const showLineTooltip = (point, event) => {
  const svgRect = chartSvg.value.getBoundingClientRect()
  const tooltipPoint = chartSvg.value.createSVGPoint()
  tooltipPoint.x = event.clientX - svgRect.left
  tooltipPoint.y = event.clientY - svgRect.top
  
  tooltip.value = {
    visible: true,
    x: tooltipPoint.x + 10,
    y: tooltipPoint.y - 40,
    title: point.name,
    value: point.value,
    width: 120,
    height: 60
  }
}

const handleMouseMove = (event) => {
  if (tooltip.value.visible) {
    const svgRect = chartSvg.value.getBoundingClientRect()
    const point = chartSvg.value.createSVGPoint()
    point.x = event.clientX - svgRect.left
    point.y = event.clientY - svgRect.top
    
    tooltip.value.x = point.x + 10
    tooltip.value.y = point.y - 40
  }
}

const handleMouseLeave = () => {
  tooltip.value.visible = false
}

const applyQuickFilter = (filter) => {
  activeQuickFilter.value = filter.label
  if (filter.max !== undefined) {
    workloadRange.value = [filter.min, filter.max]
  } else {
    workloadRange.value = [filter.min, 100]
  }
}

const updateWorkloadFilter = () => {
  activeQuickFilter.value = null
}

const resetFilters = () => {
  chartSearch.value = ''
  workloadRange.value = [0, 100]
  activeQuickFilter.value = null
  scrollPosition.value = 0
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const exportChart = () => {
  // Реализация экспорта диаграммы
  alert('Экспорт диаграммы в разработке')
}

const handleScroll = () => {
  // Обновление видимых данных уже происходит через computed
}

const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const updateChartSize = () => {
  if (chartContainer.value) {
    chartWidth.value = chartContainer.value.clientWidth
    chartHeight.value = Math.min(500, chartContainer.value.clientHeight)
  }
}

// Хуки жизненного цикла
onMounted(() => {
  updateChartSize()
  window.addEventListener('resize', updateChartSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateChartSize)
})

// Наблюдатели
watch(chartType, () => {
  scrollPosition.value = 0
})
</script>

<style scoped>
.charts-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

/* Панель управления */
.charts-control-panel {
  margin-bottom: 24px;
}

.charts-control-panel h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 24px;
}

.controls-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 16px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.control-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 14px;
  min-width: 140px;
  cursor: pointer;
}

.chart-type-toggle {
  display: flex;
  gap: 4px;
  background: #f8f9fa;
  padding: 4px;
  border-radius: 8px;
}

.type-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  border-radius: 6px;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.type-btn:hover {
  background: #e9ecef;
}

.type-btn.active {
  background: #4CAF50;
  color: white;
}

.search-filter {
  display: flex;
  gap: 12px;
  max-width: 400px;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.btn-reset {
  padding: 10px 20px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-reset:hover {
  background: #e9ecef;
}

/* Основной контейнер диаграмм */
.charts-main-container {
  display: grid;
  grid-template-columns: 250px 1fr 250px;
  gap: 20px;
  margin-bottom: 30px;
}

@media (max-width: 1200px) {
  .charts-main-container {
    grid-template-columns: 1fr;
  }
}

/* Левая колонка - метрики */
.metrics-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.metric-trend {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.metric-trend.positive {
  background: #E8F5E9;
  color: #2E7D32;
}

.metric-trend.negative {
  background: #FFEBEE;
  color: #D32F2F;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 12px;
}

.metric-progress {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.metric-subtext {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.distribution-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}

.dist-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
}

.dist-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.dist-value {
  font-size: 14px;
  font-weight: 600;
}

.top-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.top-item:hover {
  background: #e3f2fd;
  transform: translateX(4px);
}

.top-item.highlighted {
  background: #e3f2fd;
  border-left: 3px solid #2196F3;
}

.top-rank {
  font-size: 12px;
  font-weight: bold;
  color: #666;
  min-width: 24px;
}

.top-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-value {
  font-size: 14px;
  font-weight: 600;
}

/* Центральная область - основная диаграмма */
.main-chart-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #f8f9fa;
  border-color: #4CAF50;
}

.chart-container {
  position: relative;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  background: white;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.main-chart {
  width: 100%;
  height: 100%;
}

.bar-label {
  cursor: pointer;
  transition: fill 0.3s;
}

.bar-label:hover {
  fill: #2196F3;
  font-weight: bold;
}

.bar-value {
  pointer-events: none;
}

.heatmap rect {
  transition: all 0.3s;
  cursor: pointer;
}

.heatmap rect:hover {
  stroke-width: 2;
  stroke: #333;
}

.line-chart path {
  pointer-events: none;
}

.line-chart circle {
  cursor: pointer;
  transition: r 0.3s;
}

.line-chart circle:hover {
  r: 6;
}

.tooltip text {
  pointer-events: none;
}

.chart-scrollbar {
  margin-top: 20px;
  padding: 0 20px;
}

.scrollbar {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.scrollbar::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.scrollbar::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
  border: none;
}

.workload-legend {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.legend-gradient {
  display: flex;
  height: 20px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.gradient-segment {
  flex: 1;
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

/* Правая колонка - фильтры */
.filters-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.filter-section h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.filter-slider {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.range-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.slider-values {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  padding: 8px;
  background: white;
  border-radius: 6px;
}

.quick-filters {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-filter-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-filter-btn:hover {
  background: #f5f5f5;
  transform: translateX(4px);
}

.quick-filter-btn.active {
  background: #e3f2fd;
  border-color: #2196F3;
  color: #1976D2;
}

.filter-count {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.selected-workshop-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.selected-header h5 {
  margin: 0;
  font-size: 16px;
  color: #333;
  flex: 1;
}

.selected-workload {
  font-size: 18px;
  font-weight: bold;
}

.selected-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.selected-stats .stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.selected-stats .label {
  font-size: 12px;
  color: #666;
}

.selected-stats .value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.btn-view-details {
  padding: 10px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
}

.btn-view-details:hover {
  background: #45a049;
}

.no-selection {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.no-selection p {
  margin: 0;
}

/* Мини-диаграммы */
.mini-charts-grid {
  display: grid;
  gap: 20px;
  margin-top: 20px;
}

.mini-chart-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
}

.mini-chart-card h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.mini-chart-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-chart-label {
  font-size: 12px;
  color: #666;
  text-align: center;
}

.trend-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 0;
}

.trend-indicator {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border-radius: 50%;
}

.trend-indicator.positive {
  background: #E8F5E9;
  color: #2E7D32;
}

.trend-indicator.negative {
  background: #FFEBEE;
  color: #D32F2F;
}

.trend-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.trend-label {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.density-chart {
  display: flex;
  align-items: flex-end;
  height: 60px;
  gap: 2px;
  margin-bottom: 12px;
}

.density-bar {
  flex: 1;
  height: 100%;
  display: flex;
  align-items: flex-end;
}

.density-fill {
  width: 100%;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
}

.density-info {
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* Полноэкранный режим */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.fullscreen-content {
  background: white;
  border-radius: 12px;
  width: 90vw;
  height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.fullscreen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.fullscreen-header h2 {
  margin: 0;
  color: #333;
}

.btn-close-fullscreen {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.btn-close-fullscreen:hover {
  background: #f5f5f5;
}

.fullscreen-chart {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.fullscreen-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  text-align: center;
}

.fullscreen-placeholder p {
  margin: 8px 0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .charts-container {
    padding: 16px;
  }
  
  .controls-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .control-select {
    min-width: 100%;
  }
  
  .chart-type-toggle {
    width: 100%;
    justify-content: center;
  }
  
  .search-filter {
    flex-direction: column;
  }
  
  .mini-charts-grid {
    grid-template-columns: 1fr;
  }
  
  .fullscreen-content {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
  }
}
</style>