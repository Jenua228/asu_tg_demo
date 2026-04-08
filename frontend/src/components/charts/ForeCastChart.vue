<template>
  <div class="forecast-chart-module">
     <div class="controls">
    <!--  <div class="control-group">
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
      </div>

      <div class="control-group">
        <label>Прогноз на:</label>
        <input 
          v-model="forecastPeriods" 
          type="number" 
          min="1" 
          max="10" 
          @change="updateChart"
          class="forecast-input"
        >
        <span>период(ов)</span>
      </div>

      <div class="control-group">
        <label>Приближения:</label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showLinear" @change="updateChart"> Линейное
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showQuadratic" @change="updateChart"> Квадратичное
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showExponential" @change="updateChart"> Экспоненциальное
        </label>
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
            {{ getLabelForX(i) }}
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

        <!-- Фактические данные -->
        <polyline 
          v-if="actualPoints.length > 0"
          :points="actualPoints" 
          class="line-actual"
          fill="none"
        />
        <circle 
          v-for="(point, index) in actualPointsArray" 
          :key="'actual' + index"
          :cx="point.x" 
          :cy="point.y" 
          r="3" 
          class="point-actual"
        />

        <!-- Линейное приближение -->
        <polyline 
          v-if="showLinear && linearPoints.length > 0"
          :points="linearPoints" 
          class="line-linear"
          fill="none"
        />

        <!-- Квадратичное приближение -->
        <polyline 
          v-if="showQuadratic && quadraticPoints.length > 0"
          :points="quadraticPoints" 
          class="line-quadratic"
          fill="none"
        />

        <!-- Экспоненциальное приближение -->
        <polyline 
          v-if="showExponential && exponentialPoints.length > 0"
          :points="exponentialPoints" 
          class="line-exponential"
          fill="none"
        />

        <!-- Легенда -->
        <g class="legend">
          <rect x="60" y="10" width="12" height="12" class="legend-actual"/>
          <text x="80" y="20" class="legend-text">{{ $t('foreCast.Fact') }}</text>
          
          <rect v-if="showLinear" x="60" y="35" width="12" height="2" class="legend-linear"/>
          <text v-if="showLinear" x="80" y="40" class="legend-text">{{ $t('foreCast.Linear') }}</text>
          
          <rect v-if="showQuadratic" x="60" y="55" width="12" height="2" class="legend-quadratic"/>
          <text v-if="showQuadratic" x="80" y="60" class="legend-text">{{ $t('foreCast.Quart') }}</text>
          
          <rect v-if="showExponential" x="60" y="75" width="12" height="2" class="legend-exponential"/>
          <text v-if="showExponential" x="80" y="80" class="legend-text">{{ $t('foreCast.Exp') }}</text>
        </g>

        <!-- Подсказка -->
        <g v-if="tooltipVisible && currentTooltip" class="tooltip">
          <rect 
            :x="tooltipX - 60" 
            :y="tooltipY - 40" 
            width="120" 
            height="30" 
            rx="3"
            class="tooltip-bg"
          />
          <text 
            :x="tooltipX" 
            :y="tooltipY - 20" 
            text-anchor="middle"
            class="tooltip-text"
          >
            {{ currentTooltip }}
          </text>
        </g>
      </svg>
    </div>

    <div v-if="predictions" class="predictions">
      <h3>{{ $t('faultAnalyze.next') }}</h3>
      <div class="prediction-list">
        <div class="prediction-item" v-if="showLinear">
          <span class="prediction-type">{{ $t('faultAnalyze.linear') }}</span>
          <span class="prediction-value">{{ formatNumber(predictions.linear) }}</span>
        </div>
        <div class="prediction-item" v-if="showQuadratic">
          <span class="prediction-type">{{ $t('faultAnalyze.quart') }}</span>
          <span class="prediction-value">{{ formatNumber(predictions.quadratic) }}</span>
        </div>
        <div class="prediction-item" v-if="showExponential">
          <span class="prediction-type">{{ $t('faultAnalyze.exp') }}</span>
          <span class="prediction-value">{{ formatNumber(predictions.exponential) }}</span>
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
  name: 'ForecastChartModule',
  props: {
    data: {
      type: Array,
      required: true,
      default: () => []
    },
    dateField: {
      type: String,
      default: ''
    },
    valueField: {
      type: String,
      default: ''
    },
    width: {
      type: Number,
      default: 970
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
      showLinear: true,
      showQuadratic: true,
      showExponential: true,
      forecastPeriods: 1,
      
      // SVG данные
      actualPoints: '',
      actualPointsArray: [],
      linearPoints: '',
      quadraticPoints: '',
      exponentialPoints: '',
      gridLinesX: [],
      gridLinesY: [],
      yValues: [],
      
      // Подсказка
      tooltipVisible: false,
      tooltipX: 0,
      tooltipY: 0,
      currentTooltip: '',
      
      predictions: null,
      error: '',
      
      // Константы
      svgWidth: this.width,
      svgHeight: this.height,
      padding: 50
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
        typeof firstItem[field] === 'number'
      )

      if (!this.selectedDateField && this.dateFields.length > 0) {
        this.selectedDateField = this.dateFields[0]
      }
      if (!this.selectedValueField && this.valueFields.length > 0) {
        this.selectedValueField = this.valueFields[0]
      }
    },

    updateChart() {
      if (!this.selectedDateField || !this.selectedValueField || !this.data.length) {
        this.error = 'Выберите поля даты и значений'
        return
      }

      try {
        const { labels, values } = this.extractData()
        this.calculateGrid(values)
        this.calculatePoints(labels, values)
        this.predictions = this.calculatePredictions(values)
        this.error = ''

      } catch (err) {
        this.error = `Ошибка построения графика: ${err.message}`
      }
    },

    extractData() {
      const sortedData = [...this.data].sort((a, b) => {
        const aVal = a[this.selectedDateField]
        const bVal = b[this.selectedDateField]
        return new Date(aVal) - new Date(bVal)
      })

      const labels = sortedData.map(item => {
        const date = item[this.selectedDateField]
        return typeof date === 'string' ? date : date.toISOString().split('T')[0]
      })

      const values = sortedData.map(item => {
        const value = item[this.selectedValueField]
        return typeof value === 'number' ? value : 0
      })

      return { labels, values }
    },

    calculateGrid(values) {
      const chartWidth = this.svgWidth - this.padding * 2
      const chartHeight = this.svgHeight - this.padding * 2
      
      const allValues = [...values]
      if (this.showLinear) allValues.push(...this.calculateLinearForecast(values))
      if (this.showQuadratic) allValues.push(...this.calculateQuadraticForecast(values))
      if (this.showExponential) allValues.push(...this.calculateExponentialForecast(values))
      
      const minValue = Math.min(...allValues)
      const maxValue = Math.max(...allValues)
      const valueRange = maxValue - minValue
      
      // Горизонтальные линии (значения Y)
      this.gridLinesY = []
      this.yValues = []
      const gridLinesCount = 6
      
      for (let i = 0; i <= gridLinesCount; i++) {
        const value = minValue + (valueRange * i) / gridLinesCount
        const y = this.svgHeight - this.padding - (chartHeight * i) / gridLinesCount
        this.gridLinesY.push(y)
        this.yValues.push(value)
      }
      
      // Вертикальные линии (временные периоды)
      this.gridLinesX = []
      const totalPoints = values.length + this.forecastPeriods
      
      for (let i = 0; i < totalPoints; i++) {
        const x = this.padding + (chartWidth * i) / (totalPoints - 1)
        this.gridLinesX.push(x)
      }
    },

    calculatePoints(labels, values) {
      const chartWidth = this.svgWidth - this.padding * 2
      const chartHeight = this.svgHeight - this.padding * 2
      
      const allValues = [...values]
      if (this.showLinear) allValues.push(...this.calculateLinearForecast(values))
      if (this.showQuadratic) allValues.push(...this.calculateQuadraticForecast(values))
      if (this.showExponential) allValues.push(...this.calculateExponentialForecast(values))
      
      const minValue = Math.min(...allValues)
      const maxValue = Math.max(...allValues)
      const valueRange = maxValue - minValue || 1
      
      // Фактические данные
      this.actualPointsArray = values.map((value, index) => {
        const x = this.padding + (chartWidth * index) / (values.length - 1)
        const y = this.svgHeight - this.padding - ((value - minValue) / valueRange) * chartHeight
        return { x, y, value, label: labels[index] }
      })
      
      this.actualPoints = this.actualPointsArray.map(point => `${point.x},${point.y}`).join(' ')
      
      // Линейное приближение
      if (this.showLinear) {
        const linearData = this.calculateLinearData(values)
        const linearForecast = this.calculateLinearForecast(values)
        const allLinear = [...linearData, ...linearForecast]
        
        this.linearPoints = allLinear.map((value, index) => {
          const x = this.padding + (chartWidth * index) / (allLinear.length - 1)
          const y = this.svgHeight - this.padding - ((value - minValue) / valueRange) * chartHeight
          return `${x},${y}`
        }).join(' ')
      }
      
      // Квадратичное приближение
      if (this.showQuadratic) {
        const quadraticData = this.calculateQuadraticData(values)
        const quadraticForecast = this.calculateQuadraticForecast(values)
        const allQuadratic = [...quadraticData, ...quadraticForecast]
        
        this.quadraticPoints = allQuadratic.map((value, index) => {
          const x = this.padding + (chartWidth * index) / (allQuadratic.length - 1)
          const y = this.svgHeight - this.padding - ((value - minValue) / valueRange) * chartHeight
          return `${x},${y}`
        }).join(' ')
      }
      
      // Экспоненциальное приближение
      if (this.showExponential) {
        const exponentialData = this.calculateExponentialData(values)
        const exponentialForecast = this.calculateExponentialForecast(values)
        const allExponential = [...exponentialData, ...exponentialForecast]
        
        this.exponentialPoints = allExponential.map((value, index) => {
          const x = this.padding + (chartWidth * index) / (allExponential.length - 1)
          const y = this.svgHeight - this.padding - ((value - minValue) / valueRange) * chartHeight
          return `${x},${y}`
        }).join(' ')
      }
    },

    // Методы регрессии (остаются такими же)
    linearRegression(x, y) {
      const n = x.length
      const sumX = x.reduce((a, b) => a + b, 0)
      const sumY = y.reduce((a, b) => a + b, 0)
      const sumXY = x.reduce((a, b, i) => a + b * y[i], 0)
      const sumXX = x.reduce((a, b) => a + b * b, 0)

      const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
      const intercept = (sumY - slope * sumX) / n

      return { slope, intercept }
    },

    quadraticRegression(x, y) {
      const n = x.length
      const x2 = x.map(xi => xi * xi)
      const x3 = x.map(xi => xi * xi * xi)
      const x4 = x.map(xi => xi * xi * xi * xi)

      const sumX = x.reduce((a, b) => a + b, 0)
      const sumX2 = x2.reduce((a, b) => a + b, 0)
      const sumX3 = x3.reduce((a, b) => a + b, 0)
      const sumX4 = x4.reduce((a, b) => a + b, 0)
      const sumY = y.reduce((a, b) => a + b, 0)
      const sumXY = x.reduce((a, b, i) => a + b * y[i], 0)
      const sumX2Y = x2.reduce((a, b, i) => a + b * y[i], 0)

      const Sxx = sumX2 - sumX * sumX / n
      const Sxy = sumXY - sumX * sumY / n
      const Sxx2 = sumX3 - sumX * sumX2 / n
      const Sx2x2 = sumX4 - sumX2 * sumX2 / n
      const Sx2y = sumX2Y - sumX2 * sumY / n

      const denominator = Sxx * Sx2x2 - Sxx2 * Sxx2
      const a = (Sx2y * Sxx - Sxy * Sxx2) / denominator
      const b = (Sxy * Sx2x2 - Sx2y * Sxx2) / denominator
      const c = (sumY - b * sumX - a * sumX2) / n

      return { a, b, c }
    },

    exponentialRegression(x, y) {
      const logY = y.map(val => val > 0 ? Math.log(val) : 0)
      const linear = this.linearRegression(x, logY)
      
      return {
        a: Math.exp(linear.intercept),
        b: Math.exp(linear.slope)
      }
    },

    calculateLinearData(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.linearRegression(x, values)
      return Array.from({ length: n }, (_, i) => regression.slope * i + regression.intercept)
    },

    calculateQuadraticData(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.quadraticRegression(x, values)
      return Array.from({ length: n }, (_, i) => regression.a * i * i + regression.b * i + regression.c)
    },

    calculateExponentialData(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.exponentialRegression(x, values)
      return Array.from({ length: n }, (_, i) => regression.a * Math.pow(regression.b, i))
    },

    calculateLinearForecast(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.linearRegression(x, values)
      return Array.from({ length: this.forecastPeriods }, (_, i) => 
        regression.slope * (n + i) + regression.intercept
      )
    },

    calculateQuadraticForecast(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.quadraticRegression(x, values)
      return Array.from({ length: this.forecastPeriods }, (_, i) => 
        regression.a * Math.pow(n + i, 2) + regression.b * (n + i) + regression.c
      )
    },

    calculateExponentialForecast(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      const regression = this.exponentialRegression(x, values)
      return Array.from({ length: this.forecastPeriods }, (_, i) => 
        regression.a * Math.pow(regression.b, n + i)
      )
    },

    calculatePredictions(values) {
      const n = values.length
      const x = Array.from({ length: n }, (_, i) => i)
      
      const predictions = {}
      
      if (this.showLinear) {
        const linear = this.linearRegression(x, values)
        predictions.linear = linear.slope * n + linear.intercept
      }
      
      if (this.showQuadratic) {
        const quadratic = this.quadraticRegression(x, values)
        predictions.quadratic = quadratic.a * n * n + quadratic.b * n + quadratic.c
      }
      
      if (this.showExponential) {
        const exponential = this.exponentialRegression(x, values)
        predictions.exponential = exponential.a * Math.pow(exponential.b, n)
      }

      return predictions
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
        this.currentTooltip = `${closestPoint.label}: ${this.formatNumber(closestPoint.value)}`
        this.tooltipVisible = true
      } else {
        this.tooltipVisible = false
      }
    },

    findClosestPoint(x, y) {
      let closest = null
      let minDistance = Infinity
      
      for (const point of this.actualPointsArray) {
        const distance = Math.sqrt(Math.pow(point.x - x, 2) + Math.pow(point.y - y, 2))
        if (distance < minDistance && distance < 20) { // 20px радиус
          minDistance = distance
          closest = point
        }
      }
      
      return closest
    },

    getLabelForX(index) {
      if (index < this.data.length) {
        const date = this.data[index][this.selectedDateField]
        return typeof date === 'string' ? date.split('-')[2] : new Date(date).getDate()
      } else {
        return `+${index - this.data.length + 1}`
      }
    },

    formatNumber(num) {
      return new Intl.NumberFormat('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num)
    }
  }
}
</script>

<style scoped>
.forecast-chart-module {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.control-group select,
.forecast-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.forecast-input {
  width: 60px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input {
  margin: 0;
}

.chart-container {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.chart-svg {
  display: block;
  background: white;
}

.grid-line {
  stroke: #e0e0e0;
  stroke-width: 1;
}

.axis {
  stroke: #333;
  stroke-width: 2;
}

.axis-label {
  font-size: 12px;
  fill: #666;
  font-family: Arial, sans-serif;
}

.line-actual {
  stroke: #3366cc;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.line-linear {
  stroke: #dc3912;
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  stroke-linecap: round;
}

.line-quadratic {
  stroke: #ff9900;
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  stroke-linecap: round;
}

.line-exponential {
  stroke: #109618;
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  stroke-linecap: round;
}

.point-actual {
  fill: #3366cc;
  stroke: white;
  stroke-width: 1;
}

.legend {
  font-family: Arial, sans-serif;
  font-size: 12px;
}

.legend-actual {
  fill: #3366cc;
}

.legend-linear {
  fill: #dc3912;
}

.legend-quadratic {
  fill: #ff9900;
}

.legend-exponential {
  fill: #109618;
}

.legend-text {
  fill: #333;
  font-size: 12px;
}

.tooltip-bg {
  fill: rgba(0, 0, 0, 0.8);
}

.tooltip-text {
  fill: white;
  font-size: 12px;
  font-family: Arial, sans-serif;
}

.predictions {
  padding: 15px;
  background: #e8f5e8;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
}

.predictions h3 {
  margin: 0 0 10px 0;
  color: #2e7d32;
  font-size: 16px;
}

.prediction-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.prediction-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.prediction-type {
  font-weight: 600;
  color: #555;
}

.prediction-value {
  font-weight: 700;
  color: #2e7d32;
  font-size: 16px;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .controls {
    grid-template-columns: 1fr;
  }
  
  .prediction-list {
    flex-direction: column;
    gap: 10px;
  }
  
  .chart-svg {
    width: 100%;
    height: auto;
  }
}
</style>