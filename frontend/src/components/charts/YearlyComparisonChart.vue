<template>
  <div class="yearly-comparison-chart">
    <div class="controls">
      <!-- <div class="control-group">
        <label>Поле даты:</label>
        <select v-model="selectedDateField" @change="updateChart">
          <option value="">-- Выберите поле даты --</option>
          <option v-for="field in dateFields" :key="field" :value="field">
            {{ field }}
          </option>
        </select>
      </div>

      <div class="control-group">
        <label>Поле значений:</label>
        <select v-model="selectedValueField" @change="updateChart">
          <option value="">-- Выберите поле значений --</option>
          <option v-for="field in valueFields" :key="field" :value="field">
            {{ field }}
          </option>
        </select>
      </div> -->

      <div class="control-group">
        <label>{{ $t('faultAnalyze.years') }}</label>
        <div class="year-checkboxes">
          <label v-for="year in availableYears" :key="year" class="checkbox-label">
            <input 
              type="checkbox" 
              :value="year" 
              v-model="selectedYears"
              @change="updateChart"
            >
            {{ year }}
          </label>
        </div>
      </div>

      <!-- <div class="control-group">
        <label>Тип графика:</label>
        <select v-model="chartType" @change="updateChart">
          <option value="line">Линейный</option>
          <option value="bar">Столбчатый</option>
          <option value="area">Областной</option>
        </select>
      </div> -->
    </div>

    <div class="chart-container">
      <svg 
        :width="svgWidth" 
        :height="svgHeight" 
        class="chart-svg"
        @mousemove="handleMouseMove"
        @mouseleave="tooltipVisible = false"
      >
        <!-- Сетка -->
        <g v-for="(x, i) in gridLinesX" :key="'x' + i">
          <line 
            :x1="x" 
            :y1="padding" 
            :x2="x" 
            :y2="svgHeight - padding" 
            class="grid-line"
          />
          <text 
            :x="x" 
            :y="svgHeight - padding + 15" 
            class="axis-label"
          >
            {{ monthNames[i] }}
          </text>
        </g>

        <g v-for="(y, i) in gridLinesY" :key="'y' + i">
          <line 
            :x1="padding" 
            :y1="y" 
            :x2="svgWidth - padding" 
            :y2="y" 
            class="grid-line"
          />
          <text 
            :x="padding - 10" 
            :y="y + 4" 
            class="axis-label"
            text-anchor="end"
          >
            {{ formatNumber(yValues[i]) }}
          </text>
        </g>

        <!-- Оси -->
        <line 
          :x1="padding" 
          :y1="svgHeight - padding" 
          :x2="svgWidth - padding" 
          :y2="svgHeight - padding" 
          class="axis"
        />
        <line 
          :x1="padding" 
          :y1="padding" 
          :x2="padding" 
          :y2="svgHeight - padding" 
          class="axis"
        />

        <!-- Данные по годам -->
        <g v-for="(yearData, yearIndex) in chartData" :key="yearData.year">
          <!-- Линии для линейного графика -->
          <polyline 
            v-if="chartType === 'line' || chartType === 'area'"
            :points="yearData.points" 
            :class="`line-${yearIndex}`"
            fill="none"
          />

          <!-- Область для областного графика -->
          <polygon 
            v-if="chartType === 'area'"
            :points="yearData.areaPoints" 
            :class="`area-${yearIndex}`"
          />

          <!-- Столбцы для столбчатого графика -->
          <g v-if="chartType === 'bar'">
            <rect 
              v-for="(value, monthIndex) in yearData.values" 
              :key="monthIndex"
              :x="padding + (monthIndex * monthWidth) + (yearIndex * barWidth)"
              :y="getYPosition(value)" 
              :width="barWidth" 
              :height="svgHeight - padding - getYPosition(value)"
              :class="`bar-${yearIndex}`"
              rx="2"
            />
          </g>

          <!-- Точки данных -->
          <circle 
            v-for="(point, pointIndex) in yearData.pointsArray" 
            :key="'point' + pointIndex"
            :cx="point.x" 
            :cy="point.y" 
            r="3" 
            :class="`point-${yearIndex}`"
          />
        </g>

        <!-- Легенда -->
        <g class="legend">
          <rect 
            v-for="(yearData, index) in chartData" 
            :key="'legend' + index"
            :x="70" 
            :y="10 + index * 25" 
            width="15" 
            height="15" 
            :class="getLegendClass(index)"
            rx="3"
          />
          <text 
            v-for="(yearData, index) in chartData" 
            :key="'legendText' + index"
            :x="100" 
            :y="20 + index * 25" 
            class="legend-text"
          >
            {{ yearData.year }} (Σ: {{ formatNumber(yearData.total) }})
          </text>
        </g>

        <!-- Подсказка -->
        <g v-if="tooltipVisible && currentTooltip" class="tooltip">
          <rect 
            :x="tooltipX - 80" 
            :y="tooltipY - 50" 
            width="160" 
            height="60" 
            rx="5"
            class="tooltip-bg"
          />
          <text 
            :x="tooltipX" 
            :y="tooltipY - 30" 
            text-anchor="middle"
            class="tooltip-title"
          >
            {{ currentTooltip.month }} {{ currentTooltip.year }}
          </text>
          <text 
            :x="tooltipX" 
            :y="tooltipY - 10" 
            text-anchor="middle"
            class="tooltip-value"
          >
            {{ formatNumber(currentTooltip.value) }}
          </text>
          <text 
            :x="tooltipX" 
            :y="tooltipY + 10" 
            text-anchor="middle"
            class="tooltip-change"
            v-if="currentTooltip.change !== null"
          >
            {{ currentTooltip.change > 0 ? '+' : '' }}{{ currentTooltip.change.toFixed(1) }}% к пр. году
          </text>
        </g>
      </svg>
    </div>

    <!-- Статистика по годам -->
    <div v-if="yearlyStats.length > 0" class="statistics">
      <h3>Статистика по годам</h3>
      <div class="stats-grid">
        <div class="stat-card" v-for="stat in yearlyStats" :key="stat.year">
          <div class="stat-year">{{ stat.year }}</div>
          <div class="stat-total">{{ formatNumber(stat.total) }}</div>
          <div class="stat-details">
            <div>Среднее: {{ formatNumber(stat.average) }}</div>
            <div>Макс: {{ formatNumber(stat.max) }}</div>
            <div>Мин: {{ formatNumber(stat.min) }}</div>
            <div 
              class="stat-growth" 
              :class="{ positive: stat.growth > 0, negative: stat.growth < 0 }"
            >
              Рост: {{ stat.growth > 0 ? '+' : '' }}{{ stat.growth.toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'YearlyComparisonChart',
  props: {
    data: {
      type: Array,
      required: true,
      default: () => []
    },
    dateField: {
      type: String,
      default: 'Дата ремонта'
    },
    valueField: {
      type: String,
      default: ''
    },
    width: {
      type: Number,
      default: 1000
    },
    height: {
      type: Number,
      default: 600
    }
  },
  data() {
    return {
      selectedDateField: this.dateField,
      selectedValueField: this.valueField,
      dateFields: [],
      valueFields: [],
      selectedYears: [],
      availableYears: [],
      chartType: 'bar',
      
      // SVG данные
      chartData: [],
      gridLinesX: [],
      gridLinesY: [],
      yValues: [],
      monthWidth: 0,
      barWidth: 0,
      
      // Подсказка
      tooltipVisible: false,
      tooltipX: 0,
      tooltipY: 0,
      currentTooltip: null,
      
      // Статистика
      yearlyStats: [],
      error: '',
      
      // Константы
      svgWidth: this.width,
      svgHeight: this.height,
      padding: 60,
      monthNames: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    }
  },
  watch: {
    data: {
      handler(newData) {
        this.analyzeData(newData)
        this.updateChart()
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    analyzeData(data) {
      if (!data || data.length === 0) {
        this.dateFields = []
        this.valueFields = []
        return
      }

      const firstItem = data[0]        
      const fields = Object.keys(firstItem)        
      
      this.dateFields = fields.filter(field => 
        typeof firstItem[field] === 'string' || 
        firstItem[field] instanceof Date
      )
      
      this.valueFields = fields.filter(field => 
        typeof firstItem[field] === 'string'
      )

      if (!this.selectedDateField && this.dateFields.length > 0) {
        this.selectedDateField = this.dateFields[0]
      }
      if (!this.selectedValueField && this.valueFields.length > 0) {
        this.selectedValueField = this.valueFields[0]
      }

      // Определяем доступные годы
      this.extractAvailableYears(data)
    },

    extractAvailableYears(data) {
      // const years = new Set()
      // data.forEach(item => {
      //   const date = new Date(item[this.selectedDateField])
      //   if (!isNaN(date.getTime())) {
      //     years.add(date.getFullYear())
      //   }
      // })
      
      // this.availableYears = Array.from(years).sort((a, b) => b - a) // новые годы первыми
      //this.availableYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
      this.availableYears = [...new Set(data.map(item => item['Год']))].sort()
      // Автоматически выбираем последние 3 года
      if (this.availableYears.length > 0 && this.selectedYears.length === 0) {
        this.selectedYears = this.availableYears.slice(0, 3)
      }
    },

    updateChart() {
      if (!this.selectedDateField || !this.selectedValueField || !this.data.length || this.selectedYears.length === 0) {
        this.error = 'Выберите поля даты, значений и хотя бы один год'
        return
      }

      try {
        const processedData = this.processYearlyData()
        this.calculateGrid(processedData)
        this.calculateChartData(processedData)
        this.calculateStatistics(processedData)
        this.error = ''

      } catch (err) {
        this.error = `Ошибка построения графика: ${err.message}`
      }
    },      
    processYearlyData() {
      const yearlyData = {}
      
      // Инициализируем структуру для каждого выбранного года
      this.selectedYears.forEach(year => {
        yearlyData[year] = Array(12).fill(0).map(() => ({
          values: [],
          count: 0
        }))
      })

      // Заполняем данными
      this.data.forEach(item => {
        const date = new Date(item[this.selectedDateField] + "T00:00:00")
        const year = date.getFullYear()
        const month = date.getMonth() // 0-11
        const value = item[this.selectedValueField]

        if (yearlyData[year]) {
          yearlyData[year][month].values.push(value)
          yearlyData[year][month].count++
        }          
      })

      // Вычисляем средние значения по месяцам
      const result = {}
      this.selectedYears.forEach(year => {
        result[year] = yearlyData[year].map(monthData => {
          if (monthData.count > 0) {
           // return monthData.values.reduce((sum, val) => sum + val, 0) / monthData.count
           return monthData.count
          }
          return 0
        })
      })

      return result
    },

    calculateGrid(yearlyData) {
      const chartWidth = this.svgWidth - this.padding * 2
      const chartHeight = this.svgHeight - this.padding * 2
      
      // Находим минимальное и максимальное значение среди всех данных
      let minValue = Infinity
      let maxValue = -Infinity
      
      Object.values(yearlyData).forEach(yearData => {
        yearData.forEach(value => {
          if (value < minValue) minValue = value
          if (value > maxValue) maxValue = value
        })
      })

      // Добавляем немного места сверху
      maxValue = maxValue * 1.1
      minValue = Math.min(0, minValue * 0.9)
      
      const valueRange = maxValue - minValue

      // Вертикальные линии (месяцы)
      this.gridLinesX = []
      this.monthWidth = chartWidth / 12
      this.barWidth = this.monthWidth / (this.selectedYears.length + 1)
      
      for (let i = 0; i <= 12; i++) {
        const x = this.padding + (chartWidth * i) / 12
        this.gridLinesX.push(x)
      }

      // Горизонтальные линии (значения)
      this.gridLinesY = []
      this.yValues = []
      const gridLinesCount = 5
      
      for (let i = 0; i <= gridLinesCount; i++) {
        const value = minValue + (valueRange * i) / gridLinesCount
        const y = this.svgHeight - this.padding - (chartHeight * i) / gridLinesCount
        this.gridLinesY.push(y)
        this.yValues.push(value)
      }

      this.minValue = minValue
      this.valueRange = valueRange
    },

    calculateChartData(yearlyData) {
      const chartWidth = this.svgWidth - this.padding * 2
      const chartHeight = this.svgHeight - this.padding * 2
      
      this.chartData = this.selectedYears.map((year, yearIndex) => {
        const yearData = yearlyData[year]
        const pointsArray = []
        const points = []
        const areaPoints = []

        // Вычисляем общую сумму за год
        const total = yearData.reduce((sum, value) => sum + value, 0)

        yearData.forEach((value, monthIndex) => {
          const x = this.padding + (chartWidth * (monthIndex + 0.5)) / 12
          const y = this.svgHeight - this.padding - ((value - this.minValue) / this.valueRange) * chartHeight
          
          pointsArray.push({ x, y, value, month: monthIndex, year })
          points.push(`${x},${y}`)

          // Для областного графика добавляем точку на ось X
          if (this.chartType === 'area') {
            const baseY = this.svgHeight - this.padding
            areaPoints.push(`${x},${baseY}`)
          }
        })

        // Для областного графика соединяем точки в обратном порядке
        if (this.chartType === 'area') {
          areaPoints.unshift(`${this.padding},${this.svgHeight - this.padding}`)
          areaPoints.push(...points.slice().reverse())
          areaPoints.push(`${this.svgWidth - this.padding},${this.svgHeight - this.padding}`)
        }

        return {
          year,
          values: yearData,
          points: points.join(' '),
          pointsArray,
          areaPoints: areaPoints.join(' '),
          total
        }
      })
    },

    calculateStatistics(yearlyData) {
      this.yearlyStats = this.selectedYears.map((year, index) => {
        const values = yearlyData[year]
        const validValues = values.filter(v => v > 0)
        const total = values.reduce((sum, val) => sum + val, 0)
        const average = validValues.length > 0 ? total / validValues.length : 0
        const max = Math.max(...values)
        const min = Math.min(...values.filter(v => v > 0))

        // Рост относительно предыдущего года
        let growth = 0
        if (index > 0) {
          const prevYear = this.selectedYears[index - 1]
          const prevTotal = yearlyData[prevYear].reduce((sum, val) => sum + val, 0)
          growth = prevTotal > 0 ? ((total - prevTotal) / prevTotal) * 100 : 0
        }

        return {
          year,
          total,
          average,
          max,
          min,
          growth
        }
      })
    },

    getYPosition(value) {
      const chartHeight = this.svgHeight - this.padding * 2
      return this.svgHeight - this.padding - ((value - this.minValue) / this.valueRange) * chartHeight
    },

    getLegendClass(index) {
      return `legend-${index}`
    },

    handleMouseMove(event) {
      const svgElement = event.currentTarget
      const point = svgElement.createSVGPoint()
      point.x = event.clientX
      point.y = event.clientY
      const svgPoint = point.matrixTransform(svgElement.getScreenCTM().inverse())
      
      this.tooltipX = svgPoint.x
      this.tooltipY = svgPoint.y
      
      // Поиск ближайшей точки
      const closestPoint = this.findClosestPoint(svgPoint.x, svgPoint.y)
      if (closestPoint) {
        this.currentTooltip = {
          month: this.monthNames[closestPoint.month],
          year: closestPoint.year,
          value: closestPoint.value,
          change: this.calculateYearOverYearChange(closestPoint.month, closestPoint.year, closestPoint.value)
        }
        this.tooltipVisible = true
      } else {
        this.tooltipVisible = false
      }
    },

    findClosestPoint(x, y) {
      let closest = null
      let minDistance = Infinity
      
      this.chartData.forEach(yearData => {
        yearData.pointsArray.forEach(point => {
          const distance = Math.sqrt(Math.pow(point.x - x, 2) + Math.pow(point.y - y, 2))
          if (distance < minDistance && distance < 25) {
            minDistance = distance
            closest = point
          }
        })
      })
      
      return closest
    },

    calculateYearOverYearChange(month, year, value) {
      const yearIndex = this.selectedYears.indexOf(year)
      if (yearIndex <= 0) return null

      const prevYear = this.selectedYears[yearIndex - 1]
      const prevYearData = this.chartData.find(d => d.year === prevYear)
      if (!prevYearData) return null

      const prevValue = prevYearData.values[month]
      if (!prevValue || prevValue === 0) return null

      return ((value - prevValue) / prevValue) * 100
    },

    formatNumber(num) {
      return new Intl.NumberFormat('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: num < 1000 ? 1 : 0
      }).format(num)
    }
  }
}
</script>

<style scoped>
.yearly-comparison-chart {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
}

.control-group select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

.year-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-height: 120px;
  overflow-y: auto;
  padding: 5px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: normal;
  cursor: pointer;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.checkbox-label input {
  margin: 0;
}

.chart-container {
  margin-bottom: 30px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-svg {
  display: block;
}

/* Стили для сетки и осей */
.grid-line {
  stroke: #e0e0e0;
  stroke-width: 1;
}

.axis {
  stroke: #2c3e50;
  stroke-width: 2;
}

.axis-label {
  font-size: 11px;
  fill: #666;
  font-family: Arial, sans-serif;
}

/* Цвета для линий (до 6 лет) */
.line-0 { stroke: #3366cc; stroke-width: 3; }
.line-1 { stroke: #dc3912; stroke-width: 3; }
.line-2 { stroke: #ff9900; stroke-width: 3; }
.line-3 { stroke: #68b46d; stroke-width: 3; }
.line-4 { stroke: #990099; stroke-width: 3; }
.line-5 { stroke: #0099c6; stroke-width: 3; }
.line-6 { stroke: #a2e4f8; stroke-width: 3; }
.line-7 { stroke: #ca8bcc; stroke-width: 3; }

/* Цвета для областей */
.area-0 { fill: rgba(51, 102, 204, 0.2); stroke: none; }
.area-1 { fill: rgba(220, 57, 18, 0.2); stroke: none; }
.area-2 { fill: rgba(255, 153, 0, 0.2); stroke: none; }
.area-3 { fill: rgba(16, 150, 24, 0.2); stroke: none; }
.area-4 { fill: rgba(153, 0, 153, 0.2); stroke: none; }
.area-5 { fill: rgba(0, 153, 198, 0.2); stroke: none; }
.area-5 { fill: rgba(35, 194, 56, 0.2); stroke: none; }
.area-5 { fill: rgba(65, 75, 78, 0.2); stroke: none; }

/* Цвета для столбцов */
.bar-0 { fill: #3366cc; opacity: 0.8; }
.bar-1 { fill: #dc3912; opacity: 0.8; }
.bar-2 { fill: #ff9900; opacity: 0.8; }
.bar-3 { fill: #68b46d; opacity: 0.8; }
.bar-4 { fill: #990099; opacity: 0.8; }
.bar-5 { fill: #0099c6; opacity: 0.8; }
.bar-6 { fill: #a2e4f8; opacity: 0.8; }
.bar-7 { fill: #ca8bcc; opacity: 0.8; }

/* Цвета для точек */
.point-0 { fill: #3366cc; stroke: white; stroke-width: 2; }
.point-1 { fill: #dc3912; stroke: white; stroke-width: 2; }
.point-2 { fill: #ff9900; stroke: white; stroke-width: 2; }
.point-3 { fill: #68b46d; stroke: white; stroke-width: 2; }
.point-4 { fill: #990099; stroke: white; stroke-width: 2; }
.point-5 { fill: #0099c6; stroke: white; stroke-width: 2; }
.point-6 { fill: #a2e4f8; stroke: white; stroke-width: 2; }
.point-7 { fill: #ca8bcc; stroke: white; stroke-width: 2; }

/* Цвета для легенды */
.legend-0 { fill: #3366cc; }
.legend-1 { fill: #dc3912; }
.legend-2 { fill: #ff9900; }
.legend-3 { fill: #68b46d; }
.legend-4 { fill: #990099; }
.legend-5 { fill: #0099c6; }
.legend-6 { fill: #a2e4f8; }
.legend-7 { fill: #ca8bcc; }

.legend {
  font-family: Arial, sans-serif;
}

.legend-text {
  fill: #2c3e50;
  font-size: 12px;
  font-weight: 500;
}

/* Подсказка */
.tooltip-bg {
  fill: rgba(0, 0, 0, 0.85);
}

.tooltip-title {
  fill: white;
  font-size: 13px;
  font-weight: 600;
  font-family: Arial, sans-serif;
}

.tooltip-value {
  fill: white;
  font-size: 14px;
  font-weight: bold;
  font-family: Arial, sans-serif;
}

.tooltip-change {
  fill: #ffeb3b;
  font-size: 11px;
  font-family: Arial, sans-serif;
}

/* Статистика */
.statistics {
  margin-top: 30px;
}

.statistics h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-card {
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-year {
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.stat-total {
  font-size: 24px;
  font-weight: 700;
  color: #3366cc;
  margin-bottom: 10px;
}

.stat-details {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.stat-growth {
  margin-top: 8px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.stat-growth.positive {
  background: #e8f5e8;
  color: #2e7d32;
}

.stat-growth.negative {
  background: #ffebee;
  color: #c62828;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 10px;
  border: 1px solid #f5c6cb;
  text-align: center;
}

@media (max-width: 768px) {
  .controls {
    grid-template-columns: 1fr;
  }
  
  .year-checkboxes {
    max-height: 80px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-svg {
    width: 100%;
    height: auto;
  }
}
</style>