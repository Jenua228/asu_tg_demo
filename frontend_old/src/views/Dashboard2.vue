<template>
  <div class="dashboard">
    <!-- Заголовок и фильтры -->
    <div class="dashboard-header">
      <h1>{{ $t('dashboard2.title') }}</h1>
      <!-- <div class="filters">
        <div class="filter-group">
          <label for="statusFilter">Статус:</label>
          <select id="statusFilter" v-model="filters.status" @change="applyFilters">
            <option value="">Все</option>
            <option value="предстоящая">Предстоящая</option>
            <option value="выполнено">Выполнено</option>
            <option value="просрочено">Просрочено</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="tcrFilter">ТЦР:</label>
          <select id="tcrFilter" v-model="filters.tcr" @change="applyFilters">
            <option value="">Все</option>
            <option v-for="workshop in workshops" :key="workshop.id" :value="workshop.shortName">
              {{ workshop.shortName }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="categoryFilter">Категория:</label>
          <select id="categoryFilter" v-model="filters.category" @change="applyFilters">
            <option value="">Все</option>
            <option value="1">Категория 1</option>
            <option value="2">Категория 2</option>
          </select>
        </div>
        
        <button @click="resetFilters" class="reset-btn">Сбросить фильтры</button>
      </div>
    </div> -->

    <!-- Статистика -->
    <div class="stats-cards">
      <div class="stat-card total">
        <h3>{{ $t('dashboard2.totalRepairs') }}</h3>
        <p class="stat-number">{{ filteredReports.length }}</p>
      </div>
      
      <div class="stat-card upcoming">
        <h3>{{ $t('dashboard2.upcoming') }}</h3>
        <p class="stat-number">{{ stats.upcoming }}</p>
      </div>
      
      <div class="stat-card completed">
        <h3>{{ $t('dashboard2.completed') }}</h3>
        <p class="stat-number">{{ stats.completed }}</p>
      </div>
      
      <div class="stat-card overdue">
        <h3>{{ $t('dashboard2.overdue') }}</h3>
        <p class="stat-number">{{ stats.overdue }}</p>
      </div>
    
      <div class="stat-card working">
        <h3>{{ $t('dashboard2.inProgress') }}</h3>
        <p class="stat-number">{{ stats.working }}</p>
      </div>
    </div>


<!-- KPI секция (основные показатели) -->
<div class="kpi-section">
<div class="kpi-header">
  <h2>{{ $t('dashboard2.kpi.title') }}</h2>
  <button @click="showAllKpiModal = true" class="view-all-kpi-btn">
    {{ $t('dashboard2.kpi.viewAllTasks') }}
  </button>
</div>

<div class="kpi-cards">
  <!-- KPI 1: Коэффициент выполнения плана (общий) -->
  <div class="kpi-card" :class="getKpiClass(kpi.planExecutionRate)">
    <div class="kpi-icon">📊</div>
    <div class="kpi-content">
      <h3>{{ $t('dashboard2.kpi.planExecutionRate') }}</h3>
      <p class="kpi-value">{{ kpi.planExecutionRate.toFixed(1) }}%</p>
      <p class="kpi-description">{{ $t('dashboard2.kpi.planExecutionDesc') }}</p>
      <div class="kpi-formula">
        <span class="formula-label">{{ $t('dashboard2.kpi.formula') }}:</span>
        <span class="formula-text">{{ $t('dashboard2.kpi.planExecutionFormula') }}</span>
      </div>
    </div>
    <div class="kpi-indicator" :class="getPlanExecutionIndicator(kpi.planExecutionRate)">
      <span v-if="kpi.planExecutionRate <= 100">✓</span>
      <span v-else>⚠</span>
    </div>
  </div>
  
  <!-- KPI 2: Средняя доля трудозатрат (общая по всем ТЦР) -->
  <div class="kpi-card">
    <div class="kpi-icon">⚡</div>
    <div class="kpi-content">
      <h3>{{ $t('dashboard2.kpi.averageLaborShare') }}</h3>
      <p class="kpi-value">{{ kpi.averageLaborPerTask.toFixed(1) }} ч</p>
      <p class="kpi-description">{{ $t('dashboard2.kpi.averageLaborDesc') }}</p>
      <div class="kpi-formula">
        <span class="formula-label">{{ $t('dashboard2.kpi.formula') }}:</span>
        <span class="formula-text">{{ $t('dashboard2.kpi.averageLaborFormula') }}</span>
      </div>
    </div>
  </div>
  
  <!-- KPI 3: Коэффициент производительности -->
  <div class="kpi-card" :class="getProductivityClass(kpi.productivityIndex)">
    <div class="kpi-icon">🎯</div>
    <div class="kpi-content">
      <h3>{{ $t('dashboard2.kpi.productivityIndex') }}</h3>
      <p class="kpi-value">{{ kpi.productivityIndex.toFixed(1) }}%</p>
      <p class="kpi-description">{{ $t('dashboard2.kpi.productivityDesc') }}</p>
      <div class="kpi-formula">
        <span class="formula-label">{{ $t('dashboard2.kpi.formula') }}:</span>
        <span class="formula-text">{{ $t('dashboard2.kpi.productivityFormula') }}</span>
      </div>
    </div>
    <div class="kpi-progress-ring">
      <svg width="60" height="60" viewBox="0 0 60 60">
        <circle cx="30" cy="30" r="25" fill="none" stroke="#e0e0e0" stroke-width="5"/>
        <circle cx="30" cy="30" r="25" fill="none" stroke="currentColor" stroke-width="5"
          :stroke-dasharray="`${kpi.productivityIndex * 1.57} 157`"
          stroke-linecap="round"
          transform="rotate(-90 30 30)"/>
      </svg>
    </div>
  </div>
</div>
</div>

<!-- Модальное окно KPI всех задач -->
<div v-if="showAllKpiModal" class="kpi-modal-overlay" @click.self="showAllKpiModal = false">
<div class="kpi-modal">
  <div class="kpi-modal-header">
    <h2>{{ $t('dashboard2.kpi.allTasksKpi') }}</h2>
    <button @click="showAllKpiModal = false" class="close-btn">×</button>
  </div>
  <div class="kpi-modal-body">
    <table class="kpi-table">
      <thead>
        <tr>
          <th>{{ $t('dashboard2.kpi.tableColumns.taskName') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.tcr') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.plannedHours') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.spentHours') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.planExecution') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.laborShare') }}</th>
          <th>{{ $t('dashboard2.kpi.tableColumns.status') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in allTasksKpi" :key="task.id" :class="getTaskKpiRowClass(task)">
          <td class="task-name-cell">{{ task.name }}</td>
          <td>{{ task.tcr }}</td>
          <td>{{ task.plannedHours }} ч</td>
          <td>{{ task.spentHours }} ч</td>
          <td :class="getPlanExecutionCellClass(task.planExecution)">
            {{ task.planExecution.toFixed(1) }}%
          </td>
          <td>{{ task.laborShare.toFixed(1) }}%</td>
          <td>
            <span class="status-badge" :class="getStatusClass(task.status)">
              {{ task.status }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</div>

    <!-- Сводка по ТЦР -->
    <!-- <div class="tcr-summary">
      <h2>Сводка по техническим центрам ремонта</h2>
      <div class="summary-cards">
        <div class="summary-card busy">
          <div class="summary-icon">⚡</div>
          <div class="summary-info">
            <h3>Высокая загрузка</h3>
            <p class="summary-count">{{ workshopStats.highLoad }} ТЦР</p>
            <p class="summary-percent">{{ workshopStats.highLoadPercent }}%</p>
          </div>
        </div>
        
        <div class="summary-card medium">
          <div class="summary-icon">🔄</div>
          <div class="summary-info">
            <h3>Средняя загрузка</h3>
            <p class="summary-count">{{ workshopStats.mediumLoad }} ТЦР</p>
            <p class="summary-percent">{{ workshopStats.mediumLoadPercent }}%</p>
          </div>
        </div>
        
        <div class="summary-card free">
          <div class="summary-icon">✅</div>
          <div class="summary-info">
            <h3>Низкая загрузка</h3>
            <p class="summary-count">{{ workshopStats.lowLoad }} ТЦР</p>
            <p class="summary-percent">{{ workshopStats.lowLoadPercent }}%</p>
          </div>
        </div>
      </div>
    </div> -->

    <!-- Диаграмма загрузки ТЦР -->
    <div class="charts-section">
      <div class="chart-card">
        <h3>{{ $t('dashboard2.tcrLoad') }}</h3>
        <div class="bar-chart">
          <div v-for="workshop in workshops" :key="workshop.id" class="bar-chart-item">
            <div class="bar-label">{{ $t('dashboard2.columns.tcr') }}{{ workshop.shortName.slice(3) }}</div>
            <div class="bar-container">
              <div 
                class="bar" 
                :style="{ width: workshop.workload + '%' }"
                :class="getWorkloadClass(workshop.workload)"
                :title="`${workshop.name}: ${workshop.workload}%`"
              >
                <span class="bar-value">{{ workshop.workload }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-card">
        <h3>{{ $t('dashboard2.tcrDistribution') }}</h3>
        <div class="pie-chart-container">
          <div class="pie-chart">
            <svg width="200" height="200" viewBox="0 0 200 200">
              <!-- Сектор высокой загрузки -->
              <circle 
                cx="100" cy="100" r="80" 
                fill="transparent" 
                :stroke="getWorkloadColor(80)" 
                stroke-width="40"
                pathLength="100"
                :stroke-dasharray="`${workshopStats.highLoadPercent} ${100 - workshopStats.highLoadPercent}`"
                :stroke-dashoffset="0"
              />
              <!-- Сектор средней загрузки -->
              <circle 
                cx="100" cy="100" r="80" 
                fill="transparent" 
                :stroke="getWorkloadColor(50)" 
                stroke-width="40"
                pathLength="100"
                :stroke-dasharray="`${workshopStats.mediumLoadPercent} ${100 - workshopStats.mediumLoadPercent}`"
                :stroke-dashoffset="`${0 - workshopStats.highLoadPercent}`"
              />
              <!-- Сектор низкой загрузки -->
              <circle 
                cx="100" cy="100" r="80" 
                fill="transparent" 
                :stroke="getWorkloadColor(20)" 
                stroke-width="40"
                pathLength="100"
                :stroke-dasharray="`${workshopStats.lowLoadPercent} ${100 - workshopStats.lowLoadPercent}`"
                :stroke-dashoffset="0 - (workshopStats.highLoadPercent) - (workshopStats.mediumLoadPercent)"
              />
            </svg>
          </div>
          <div class="pie-legend">
            <div class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: getWorkloadColor(80) }"></span>
              <span>{{ $t('dashboard2.highLoad') }}</span>
              <span class="legend-count">{{ workshopStats.highLoad }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: getWorkloadColor(50) }"></span>
              <span>{{ $t('dashboard2.mediumLoad') }}</span>
              <span class="legend-count">{{ workshopStats.mediumLoad }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: getWorkloadColor(20) }"></span>
              <span>{{ $t('dashboard2.lowLoad') }}</span>
              <span class="legend-count">{{ workshopStats.lowLoad }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
</div>
    <!-- Загрузка ТЦР с участками -->
    <div class="workshops-section">
      <h2>{{ $t('dashboard2.detailedLoad') }}</h2>
      <div class="workshops-container">
        <div class="workshop-card" v-for="workshop in workshops" :key="workshop.id">
          <div class="workshop-header" @click="toggleWorkshopDetails(workshop.id)">
            <div class="workshop-title">
              <h3>{{ $t('dashboard2.columns.tcr') }}{{ workshop.shortName.slice(3) }}</h3>
              <span class="workshop-name">{{ workshop.name }}</span>
            </div>
            <div class="workshop-stats">
              <div class="workload-indicator">
                <div class="workload-bar">
                  <div 
                    class="workload-fill" 
                    :style="{ width: workshop.workload + '%' }"
                    :class="getWorkloadClass(workshop.workload)"
                  ></div>
                </div>
                <span class="workload-value">{{ workshop.workload }}%</span>
              </div>
              <span class="toggle-icon">{{ expandedWorkshop === workshop.id ? '−' : '+' }}</span>
            </div>
          </div>
          
          <div v-if="expandedWorkshop === workshop.id" class="workshop-details">
            <div class="workshop-summary">
              <div class="summary-item">
                <span class="label">{{ $t('dashboard2.totalSections') }}</span>
                <span class="value">{{ workshop.sections.length }}</span>
              </div>
              <div class="summary-item">
                <span class="label">{{ $t('dashboard2.averageLoad') }}</span>
                <span class="value">{{ calculateAverageLoad(workshop) }}%</span>
              </div>
              <div class="summary-item">
                <span class="label">{{ $t('dashboard2.storageAreas') }}</span>
                <span class="value">{{ countStorageSections(workshop) }}</span>
              </div>
            </div>
            
            <div class="sections-grid">
              <div v-for="section in workshop.sections" :key="section.id" class="section-card">
                <div class="section-header">
                  <span class="section-name">{{ section.name }}</span>
                  <span class="section-load" :class="getLoadClass(section.workload)">
                    {{ section.workload }}%
                  </span>
                </div>
                <div class="section-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: section.workload + '%' }"
                      :class="getLoadClass(section.workload)"
                    ></div>
                  </div>
                </div>
                <div class="section-info">
                  <div class="info-item">
                    <span class="info-label">{{ $t('dashboard2.capacity') }}</span>
                    <span class="info-value">{{ section.capacity }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ $t('dashboard2.current') }}</span>
                    <span class="info-value">{{ section.currentLoad }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ $t('dashboard2.available') }}</span>
                    <span class="info-value">{{ section.capacity - section.currentLoad }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Таблица данных -->
      <div class="table-section">
        <div class="section-header">
          <h2>{{ $t('dashboard2.repairList') }}</h2>
          <div class="table-info">
            {{ $t('dashboard2.showing') }} {{ filteredReports.length }} {{ $t('dashboard2.of') }} {{ reports.length }}
          </div>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th @click="sortBy('nameRETIndex')" class="sortable">
                  <div class="th-content">
                    <span>{{ $t('dashboard2.columns.name') }}</span>
                    <span v-if="sortField === 'nameRETIndex'" class="sort-arrow">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th @click="sortBy('factoryNumber')" class="sortable">
                  <div class="th-content">
                    <span>{{ $t('dashboard2.columns.factoryNumber') }}</span>
                    <span v-if="sortField === 'factoryNumber'" class="sort-arrow">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th @click="sortBy('status')" class="sortable">
                  <div class="th-content">
                    <span>{{ $t('dashboard2.columns.status') }}</span>
                    <span v-if="sortField === 'status'" class="sort-arrow">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th @click="sortBy('beginRepairDate')" class="sortable">
                  <div class="th-content">
                    <span>{{ $t('dashboard2.columns.startDate') }}</span>
                    <span v-if="sortField === 'beginRepairDate'" class="sort-arrow">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th @click="sortBy('dueDate')" class="sortable">
                  <div class="th-content">
                    <span>{{ $t('dashboard2.columns.dueDate') }}</span>
                    <span v-if="sortField === 'dueDate'" class="sort-arrow">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th>{{ $t('dashboard2.columns.tcr') }}</th>
                <th>{{ $t('dashboard2.columns.laborCost') }}</th>
                <!-- <th>Действия</th> -->
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in sortedReports" :key="report.id" 
                  :style="{ backgroundColor: report.color + '20' }"
                  @click="selectReport(report)">
                <td>
                  <div class="item-name">
                    <div class="color-indicator" :style="{ backgroundColor: report.color }"></div>
                    <div class="item-text">
                      <div class="item-title">{{ report.nameRETIndex }}</div>
                      <div class="item-subtitle">{{ report.division }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="factory-number">{{ report.factoryNumber }}</div>
                </td>
                <td>
                  <span class="status-badge" :class="getStatusClass(report.status)">
                    {{ report.status }}
                  </span>
                </td>
                <td>
                  <div class="date-cell">
                    {{ formatDate(report.beginRepairDate) }}
                  </div>
                </td>
                <td>
                  <div class="date-cell" :class="{ 'overdue': isDateOverdue(report.dueDate) }">
                    {{ formatDate(report.dueDate) }}
                    <span v-if="isDateOverdue(report.dueDate)" class="overdue-icon">⚠️</span>
                  </div>
                </td>
                <td>
                  <span>
                    {{ report.tcr }}
                  </span>
                  <!-- <span class="tcr-badge" :style="{ 
                    backgroundColor: getTCRColor(report.tcr),
                    color: getTCRTextColor(report.tcr)
                  }">
                    {{ report.tcr }}
                  </span> -->
                </td>
                <td>
                  <div class="labor-cost">
                    {{ report.laborCost }} ч
                  </div>
                </td>
                <!-- <td>
                  <div class="action-buttons">
                    <button @click.stop="editReport(report)" class="action-btn edit" title="Редактировать">
                      <span class="action-icon">✏️</span>
                    </button>
                    <button @click.stop="deleteReport(report.id)" class="action-btn delete" title="Удалить">
                      <span class="action-icon">🗑️</span>
                    </button>
                  </div>
                </td> -->
              </tr>
            </tbody>
          </table>
          <div v-if="filteredReports.length === 0" class="empty-table">
            <div class="empty-icon">📋</div>
            <p>{{ $t('dashboard2.noDataFilters') }}</p>
            <button @click="resetFilters" class="reset-filters-btn">{{ $t('dashboard2.resetFilters') }}</button>
          </div>
        </div>
      </div>

      <!-- Диаграмма Ганта -->
      <!-- <div class="gantt-section">
        <div class="section-header">
          <h2>Календарь ремонтов</h2>
          <div class="date-range">
            {{ formatDateRange(timelineDates[0], timelineDates[timelineDates.length - 1]) }}
          </div>
        </div>
        <div class="gantt-container">
          <div class="gantt-timeline">
            <div class="timeline-header">
              <div class="task-name-header">Задача</div>
              <div class="timeline-dates">
                <div v-for="date in timelineDates" :key="date" class="timeline-date">
                  {{ formatTimelineDate(date) }}
                </div>
              </div>
            </div>
            
            <div class="gantt-tasks">
              <div v-for="task in ganttTasks" :key="task.id" class="gantt-task">
                <div class="task-label" :title="task.title">{{ task.title }}</div>
                <div class="task-bar-container">
                  <div 
                    class="task-bar"
                    :style="{
                      left: calculateTaskPosition(task.start_date) + '%',
                      width: calculateTaskWidth(task.start_date, task.end_date) + '%',
                      backgroundColor: task.color
                    }"
                    :title="`${formatDate(task.start_date)} - ${formatDate(task.end_date)}`"
                  >
                    <span class="task-status">{{ getStatusShort(task.status) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
 -->
      <!-- Детальная информация -->
      <div v-if="selectedReport" class="detail-section">
        <div class="detail-header">
          <h2>{{ $t('dashboard2.detail.title') }}</h2>
          <button @click="selectedReport = null" class="close-btn" title="Закрыть">×</button>
        </div>
        <div class="detail-card">
          <div class="detail-main">
            <div class="detail-title">
              <h3>{{ selectedReport.nameRETIndex }}</h3>
              <div class="detail-status">
                <span class="status-badge" :class="getStatusClass(selectedReport.status)">
                  {{ selectedReport.status }}
                </span>
                <!-- backgroundColor: getTCRColor(selectedReport.tcr), -->
                <span class="tcr-badge" :style="{ 
                  
                  color: getTCRTextColor(selectedReport.tcr)
                }">
                  {{ selectedReport.tcr }}
                </span>
              </div>
            </div>
            
            <div class="detail-timeline">
              <div class="timeline-item">
                <span class="timeline-label">{{ $t('dashboard2.detail.receiving') }}:</span>
                <span class="timeline-value">{{ formatDate(selectedReport.receivingDate) }}</span>
              </div>
              <div class="timeline-item">
                <span class="timeline-label">{{ $t('dashboard2.detail.repairStart') }}:</span>
                <span class="timeline-value">{{ formatDate(selectedReport.beginRepairDate) }}</span>
              </div>
              <div class="timeline-item">
                <span class="timeline-label">{{ $t('dashboard2.detail.repairEnd') }}:</span>
                <span class="timeline-value">{{ formatDate(selectedReport.endRepairDate) }}</span>
              </div>
              <div class="timeline-item">
                <span class="timeline-label">{{ $t('dashboard2.detail.dueDate') }}:</span>
                <span class="timeline-value" :class="{ 'overdue': isDateOverdue(selectedReport.dueDate) }">
                  {{ formatDate(selectedReport.dueDate) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="detail-grid">
            <div class="detail-group">
              <h4>{{ $t('dashboard2.detail.mainData') }}</h4>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.factoryNumber') }}:</strong> {{ selectedReport.factoryNumber }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.makeDate') }}:</strong> {{ formatDate(selectedReport.makeDate) }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.division') }}:</strong> {{ selectedReport.division }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.category') }}:</strong> {{ selectedReport.category }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.repairType') }}:</strong> {{ selectedReport.repairType }}
              </div>
            </div>
            
            <div class="detail-group">
              <h4>{{ $t('dashboard2.detail.technicalParams') }}</h4>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.laborCost') }}:</strong> {{ selectedReport.laborCost }} {{ $t('dashboard2.detail.hours') }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.hoursFromStart') }}:</strong> {{ selectedReport.hoursFromStart }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.hoursFromLastRepair') }}:</strong> {{ selectedReport.hoursFromLastRepair || 'нет' }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.militaryRepairs') }}:</strong> {{ selectedReport.militaryRepairs }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.capitalRepairs') }}:</strong> {{ selectedReport.capitalRepairs }}
              </div>
            </div>
            
            <div class="detail-group">
              <h4>{{ $t('dashboard2.detail.responsiblePersons') }}</h4>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.responsibleRepair') }}:</strong> {{ selectedReport.responsibleRepair }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.responsibleTransfer') }}:</strong> {{ selectedReport.responsibleTransfer }}
              </div>
            </div>
            
            <div class="detail-group full-width">
              <h4>{{ $t('dashboard2.detail.additionalInfo') }}</h4>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.failureDate') }}:</strong> {{ formatDate(selectedReport.failureDate) || 'нет' }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.usedZIP') }}:</strong> {{ selectedReport.usedZIP || 'нет' }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.workType') }}:</strong> {{ selectedReport.workType || 'нет' }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.destination') }}:</strong> {{ selectedReport.destination }}
              </div>
              <div class="detail-item">
                <strong>{{ $t('dashboard2.detail.comments') }}:</strong> {{ selectedReport.comments || 'нет' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

// Реактивные данные
const reports = ref([])
const ganttData = ref({ tasks: [], connections: [] })
const filters = ref({
  status: '',
  tcr: '',
  category: ''
})
const sortField = ref('beginRepairDate')
const sortDirection = ref('asc')
const selectedReport = ref(null)
const expandedWorkshop = ref(null)
const { t } = useI18n()
// Модальное окно KPI всех задач
const showAllKpiModal = ref(false)

// Данные о ТЦР (цехах ремонта)
const workshops = ref([
  {
    id: 1,
    shortName: 'ТЦР-1',
    name: 'Стационарный КРДО «РЕДИКОМ»',
    workload: 0,
    sections: [
      { id: 101, name: 'Участок ремонта цифровых сменных элементов РЭА', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 102, name: 'Участок ремонта цифроаналоговых, аналоговых и высокочастотных сменных элементов РЭА', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 103, name: 'Участок ремонта источников вторичного питания РЭА', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 104, name: 'Участок ремонта СВЧ аппаратуры', workload: 0, capacity: 1, currentLoad: 0 }
    ],
  },
  {
    id: 2,
    shortName: 'ТЦР-2',
    name: 'ТЦР ремонта гидравлических систем ЗРК «Бук-М2Э»',
    workload: 0,
    sections: [
      { id: 201, name: 'Участок дефектации, разборки, сборки и настройки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 202, name: 'Участок сборки, испытаний гидравлических частей и цилиндров', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 203, name: 'Участок ремонта, изготовления трубопроводов и проверки на герметичность', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 204, name: 'Слесарный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 205, name: 'Участок испытания привода вращения', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 206, name: 'Участок ремонта, настройки гидроцилиндров и гидравлических замков', workload: 0, capacity: 1, currentLoad: 0 }
    ],
  },
  {
    id: 3,
    shortName: 'ТЦР-3',
    name: 'ТЦР ремонта СЧ изделий 9И56, 9И56-8, 9И112М2, 9И113М2, 9И114М2',
    workload: 0,
    sections: [
      { id: 301, name: 'Подготовка Участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 302, name: 'Участок дефектации', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 303, name: 'Участок разборки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 304, name: 'Участок входного контроля подшипниковой заготовки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 305, name: 'Слесарный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 306, name: 'Участок механической обработки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 307, name: 'Участок балансировки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 308, name: 'Участок съёма металла при балансировке', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 309, name: 'Участок доводки и притирки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 310, name: 'Участок сварки и пайки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 311, name: 'Участок ремонта топливорегулирующей аппаратуры (ТРА)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 312, name: 'Участок общей сборки', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 313, name: 'Участок контроля', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 314, name: 'Участок контроля электроблоков и ремонта кабелей', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 315, name: 'Участок специальных испытаний после доводки', workload: 40, capacity: 100, currentLoad: 40 },
      { id: 316, name: 'Участок выдачи из ремонта', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 317, name: 'Диспетчерская', workload: 0, capacity: 1, currentLoad: 0 }
    ],
  },
  {
    id: 4,
    shortName: 'ТЦР-4',
    name: 'ТЦР дизельных двигателей',
    workload: 0,
    sections: [
      { id: 401, name: 'Пост приема в ремонт', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 402, name: 'Пост дефектации двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 403, name: 'Пост разборки двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 404, name: 'Пост ремонта навесного оборудования', workload: 0, capacity: 1, currentLoad: 500 },
      { id: 405, name: 'Пост ремонта электрооборудования', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 406, name: 'Пост ремонта топливной аппаратуры', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 407, name: 'Пост устранения дефектов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 408, name: 'Участок подкрашивания ДВС', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 409, name: 'Участок ремонта шатуно1поршневой группы', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 410, name: 'Участок ремонта клапанов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 411, name: 'Участок ремонта ГБЦ и рубашки охлаждения', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 412, name: 'Участок ремонта картера и БЦ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 413, name: 'Участок ремонта валов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 414, name: 'Пост сборки двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 415, name: 'Пост комплектации', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 416, name: 'Участок сдачи блоков и узлов ОТК', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 417, name: 'Инструментальная', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 418, name: 'Диспетчерская', workload: 0, capacity: 1, currentLoad: 0 },
    ],
  },
  {
    id: 5,
    shortName: 'ТЦР-5',
    name: 'ТЦР ремонта модуля разведки и управления 9С932-1 и ЗСУ-23-4М4 «Шилка-М4»',
    workload: 0,
    sections: [   
      { id: 501, name: 'Участок диагностики изделия', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 502, name: 'Площадка для размещения подвижного оборудования', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 503, name: 'Участок ремонта изделия', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 504, name: 'Слесарно-сборочный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 505, name: 'Электромонтажный участок #1', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 506, name: 'Электромонтажный участок #2', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 507, name: 'Слесарный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 508, name: 'Инженерный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 509, name: 'Участок настроечно-регулировочных работ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 510, name: 'Участок ремонта мачт и кондиционеров', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 511, name: 'Участок проверки, сборки, ремонта и настройки блоков', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 512, name: 'Командный пункт', workload: 0, capacity: 1, currentLoad: 0 },    
    ],
  },
  {
    id: 6,
    shortName: 'ТЦР-6',
    name: 'ТЦР ремонта шасси ЗРК «Тор-М1», ЗРК «Тор-М2Э», ЗРК «Бук-М2Э», ЗРК «Антей-2500», МРУ-Б',
    workload: 0,
    sections: [
      { id: 601, name: 'Участок дефектации, разборки-сборки и испытаний ГМ, Мт-Лбу (5 зон и площадок)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 602, name: 'Участок дефектации, разборки-сборки и испытаний СГШ(4 зоны и площадки)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 603, name: 'Участок обслуживания АКБ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 604, name: 'Участок ремонта узлов СГШ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 605, name: 'Участок заправки баллов ППО', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 606, name: 'Слесарно-сборочный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 607, name: 'Участок ремонта узлов шасси МТ-Лбу', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 608, name: 'Участок испытания электрооборудования, проверки жгутов, ремонта блока управления ГМТ, щитка двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 609, name: 'Участок испытаний топливных баков и радиаторов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 610, name: 'Участок испытаний (боксы 1-3)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 611, name: 'Сварочный участок', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 612, name: 'Участок сдачи готовой продукции', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 613, name: 'Кладовая приспособлений инструмента, участок хранения ЗИП', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 614, name: 'Зоны хранения крупногабаритного ЗИП (2 зоны)', workload: 0, capacity: 2, currentLoad: 0 },
    ],
  },
  {
    id: 7,
    shortName: 'ТЦР-7',
    name: 'ТЦР ремонта шасси  ЗРК «Тор-М1», ЗРК «Тор-М2Э», ЗРК «Бук-М2Э», ЗРК «Антей-2500», МРУ-Б',
    workload: 0,
    sections: [
      { id: 701, name: 'Пост приема в ремонт', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 702, name: 'Пост дефектации двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 703, name: 'Пост разборки двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 704, name: 'Пост ремонта навесного оборудования', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 705, name: 'Пост ремонта электрооборудования', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 706, name: 'Пост ремонта топливной аппаратуры', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 707, name: 'Пост устранения дефектов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 708, name: 'Участок подкрашивания ДВС', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 709, name: 'Участок ремонта шатуно-поршневой группы', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 710, name: 'Участок ремонта клапанов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 711, name: 'Участок ремонта ГБЦ и рубашки охлаждения', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 712, name: 'Участок ремонта картера и БЦ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 713, name: 'Участок ремонта валов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 714, name: 'Пост сборки двигателя', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 715, name: 'Пост комплектации', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 716, name: 'Участок сдачи блоков и узлов ОТК', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 717, name: 'Инструментальная', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 718, name: 'Диспетчерская', workload: 0, capacity: 1, currentLoad: 0 },
    ],
  },
  {
    id: 8,
    shortName: 'ТЦР-8',
    name: 'ТЦР ремонта ЗРК «Тор-М2Э»',
    workload: 0,
    sections: [
      { id: 801, name: 'Участок сборки-разборки изделий', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 802, name: 'Участок диагностики и ремонта антенного поста', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 803, name: 'Участок диагностики и ремонта электронных и электромеханических блоков', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 804, name: 'Участок диагностики и ремонта цифровых, высокочастотных и аналоговых панелей', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 805, name: 'Электромонтажный участок для ремонта блоков и жгутов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 806, name: 'Химическая лаборатория', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 807, name: 'Камера окраски (агрегатное помещение)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 808, name: 'Камера дождевания (агрегатное помещение)', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 809, name: 'Отделение подкраски корпусов, блоков, панелей', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 810, name: 'Склад ЛВЖ', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 811, name: 'Склад химических материалов', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 812, name: 'Кладовая инструментов и приспособлений', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 813, name: 'Кладовая средств измерений', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 814, name: 'Склад узлов, блоков, комплектующих изделий', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 815, name: 'Кладовая материалов и малогабаритного ЗИП', workload: 0, capacity: 1, currentLoad: 0 },
      { id: 816, name: 'Административные помещения (4 помещения)', workload: 0, capacity: 1, currentLoad: 0 },
    ],
  },
  {
    id: 9,
    shortName: 'ТЦР-9',
    name: 'ТЦР ремонта изделий 9М82МДЭ, 9М83МЭ, 9М317',
    workload: 0,
    sections: [
      { id: 901, name: 'Участок дефектации, разборки, сборки и контроля изделий', workload: 30, capacity: 100, currentLoad: 50 },
      { id: 902, name: 'Участок мелкой сборки (в том числе снаряжения/расснаряжения изделий)', workload: 20, capacity: 100, currentLoad: 50 },
      { id: 903, name: 'Участок упаковки изделий и составных частей', workload: 40, capacity: 100, currentLoad: 50 },
      { id: 904, name: 'Участок выполнения ремонтных работ', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 905, name: 'Участок проверки бортовой аппаратуры до и после ремонта', workload: 70, capacity: 100, currentLoad: 50 },
      { id: 906, name: 'Участок испытания на герметичность', workload: 60, capacity: 100, currentLoad: 50 },
      { id: 907, name: 'Участок входного контроля, дефектации и проверки', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 908, name: 'Участок технической документации', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 909, name: 'Склад инструмента и приспособлений', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 910, name: 'Участок хранения оснастки, инструмента и приспособлений', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 911, name: 'Склад (участок) хранения изделий до и после ремонта', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 912, name: 'Склад готовых изделий (запасных частей)', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 913, name: 'Склад ЗИП-Р', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 914, name: 'Склад ЛКП и ЛВЖ', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 915, name: 'Склад хранения забракованных комплектующих, пироэлементов, из состава ЗУР', workload: 50, capacity: 100, currentLoad: 50 },
      { id: 916, name: 'Командный пункт', workload: 50, capacity: 100, currentLoad: 50 },
    ],
  },
])

// Вычисляемые свойства
const filteredReports = computed(() => {
  return reports.value.filter(report => {
    if (filters.value.status && report.status !== filters.value.status) return false
    if (filters.value.tcr && report.tcr !== filters.value.tcr) return false
    if (filters.value.category && report.category !== filters.value.category) return false
    return true
  })
})

const sortedReports = computed(() => {
  return [...filteredReports.value].sort((a, b) => {
    let aValue = a[sortField.value]
    let bValue = b[sortField.value]
    
    if (sortField.value.includes('Date')) {
      aValue = parseDate(aValue)
      bValue = parseDate(bValue)
    }
    
    if (sortDirection.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
})

const stats = computed(() => {
  return {
    total: reports.value.length,
    upcoming: reports.value.filter(r => r.status === 'предстоящая').length,
    working: reports.value.filter(r => r.status === 'в работе').length,
    completed: reports.value.filter(r => r.status === 'выполнено').length,
    overdue: reports.value.filter(r => r.status === 'просрочено').length
  }
})

// KPI метрики (общие)
const kpi = computed(() => {
const reportsData = reports.value

// KPI 1: Коэффициент выполнения плана (общий)
let totalPlanned = 0
let totalSpent = 0

reportsData.forEach(report => {
  const planned = parseFloat(report.plannedHours) || parseFloat(report.planned_hours) || 0
  const spent = parseFloat(report.spentHours) || parseFloat(report.spent_hours) || 0
  if (planned > 0) {
    totalPlanned += planned
    totalSpent += spent
  }
})

const planExecutionRate = totalPlanned > 0 
  ? (totalSpent / totalPlanned) * 100 
  : 0

// KPI 2: Средние трудозатраты на задачу
let totalLabor = 0
reportsData.forEach(report => {
  totalLabor += parseFloat(report.laborCost) || parseFloat(report.labor_cost) || 0
})
const averageLaborPerTask = reportsData.length > 0 
  ? totalLabor / reportsData.length 
  : 0

// KPI 3: Коэффициент производительности
const totalTasks = reportsData.length
const completedTasks = reportsData.filter(r => 
  r.status === 'выполнено' || r.status === 'completed'
).length

const productivityIndex = totalTasks > 0 
  ? (completedTasks / totalTasks) * 100 
  : 0

return {
  planExecutionRate,
  averageLaborPerTask,
  productivityIndex,
  totalPlanned,
  totalSpent,
  totalLabor,
  completedTasks,
  totalTasks
}
})

// KPI для каждой задачи (для таблицы в модальном окне)
const allTasksKpi = computed(() => {
const reportsData = reports.value

// Сначала посчитаем общие трудозатраты по каждому ТЦР
const tcrTotalLabor = {}
reportsData.forEach(report => {
  const tcr = report.tcr || 'Не указан'
  const labor = parseFloat(report.laborCost) || parseFloat(report.labor_cost) || 0
  tcrTotalLabor[tcr] = (tcrTotalLabor[tcr] || 0) + labor
})

return reportsData.map(report => {
  const planned = parseFloat(report.plannedHours) || parseFloat(report.planned_hours) || 0
  const spent = parseFloat(report.spentHours) || parseFloat(report.spent_hours) || 0
  const labor = parseFloat(report.laborCost) || parseFloat(report.labor_cost) || 0
  const tcr = report.tcr || 'Не указан'
  
  // Коэффициент выполнения плана для этой задачи
  const planExecution = planned > 0 ? (spent / planned) * 100 : 0
  
  // Доля трудозатрат от всего ТЦР
  const laborShare = tcrTotalLabor[tcr] > 0 ? (labor / tcrTotalLabor[tcr]) * 100 : 0
  
  return {
    id: report.id,
    name: report.nameRETIndex || report.name_ret_index || 'Без названия',
    tcr: tcr,
    plannedHours: planned,
    spentHours: spent,
    planExecution: planExecution,
    laborShare: laborShare,
    status: report.status || 'Не указан'
  }
})
})


// Функции для стилизации KPI
const getKpiClass = (value) => {
if (value <= 90) return 'kpi-excellent'
if (value <= 100) return 'kpi-good'
if (value <= 110) return 'kpi-warning'
return 'kpi-danger'
}

const getPlanExecutionIndicator = (value) => {
if (value <= 100) return 'indicator-success'
return 'indicator-warning'
}

const getProductivityClass = (value) => {
if (value >= 80) return 'kpi-excellent'
if (value >= 60) return 'kpi-good'
if (value >= 40) return 'kpi-warning'
return 'kpi-danger'
}

// Класс для строки в таблице KPI
const getTaskKpiRowClass = (task) => {
if (task.planExecution > 120) return 'kpi-row-danger'
if (task.planExecution > 100) return 'kpi-row-warning'
return ''
}

// Класс для ячейки коэффициента выполнения плана
const getPlanExecutionCellClass = (value) => {
if (value > 120) return 'cell-danger'
if (value > 100) return 'cell-warning'
if (value <= 100) return 'cell-success'
return ''
}

const workshopStats = computed(() => {
  const highLoad = workshops.value.filter(w => w.workload >= 70).length
  const mediumLoad = workshops.value.filter(w => w.workload >= 40 && w.workload < 70).length
  const lowLoad = workshops.value.filter(w => w.workload < 40).length
  const total = workshops.value.length
  
  return {
    highLoad,
    mediumLoad,
    lowLoad,
    highLoadPercent: Math.round((highLoad / total) * 100),
    mediumLoadPercent: Math.round((mediumLoad / total) * 100),
    lowLoadPercent: Math.round((lowLoad / total) * 100)
  }
})

const ganttTasks = computed(() => {
  return ganttData.value.tasks || []
})

const timelineDates = computed(() => {
  if (!ganttTasks.value.length) return []
  
  const dates = []
  const today = new Date('2026-01-10')
  const endDate = new Date('2026-02-01')
  
  for (let d = new Date(today); d <= endDate; d.setDate(d.getDate() + 1)) {
    dates.push(new Date(d))
  }
  
  return dates
})

// Методы
const parseDate = (dateStr) => {
  if (!dateStr || dateStr === 'нет') return new Date(0)
  const [day, month, year] = dateStr.split('.')
  return new Date(year, month - 1, day)
}

const formatDate = (dateStr) => {
  if (!dateStr || dateStr === 'нет') return '—'
  return dateStr
}

const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return ''
  const startStr = startDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
  const endStr = endDate.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
  return `${startStr} - ${endStr}`
}

const formatTimelineDate = (date) => {
  return date.getDate().toString().padStart(2, '0')
}

const isDateOverdue = (dateStr) => {
  const date = parseDate(dateStr)
  const today = new Date('2026-01-31')
  return date < today
}

const getStatusClass = (status) => {
  return {
    'предстоящая': 'status-upcoming',
    'выполнено': 'status-completed',
    'просрочено': 'status-overdue'
  }[status] || ''
}

const getStatusShort = (status) => {
  const map = {
    'предстоящая': 'предст.',
    'выполнено': 'выполн.',
    'просрочено': 'проср.'
  }
  return map[status] || status
}

const getWorkloadClass = (workload) => {
  if (workload >= 80) return 'high'
  if (workload >= 60) return 'medium'
  if (workload >= 40) return 'normal'
  if (workload >= 20) return 'low'
  return 'very-low'
}

const getWorkloadColor = (workload) => {
  if (workload >= 70) return '#EF476F' // Высокая
  if (workload >= 40) return '#FFA166' // Средняя
  return '#06D6A0' // Низкая
}

const getLoadClass = (load) => {
  if (load >= 80) return 'load-high'
  if (load >= 60) return 'load-medium'
  if (load >= 40) return 'load-normal'
  if (load >= 20) return 'load-low'
  return 'load-very-low'
}

const getTCRColor = (tcr) => {
  const tcrMap = {
    'ТЦР-1': '#4A90D9',
    'ТЦР-2': '#50C878',
    'ТЦР-3': '#FF6B6B',
    'ТЦР-4': '#FFD166',
    'ТЦР-5': '#06D6A0',
    'ТЦР-6': '#118AB2',
    'ТЦР-7': '#EF476F',
    'ТЦР-8': '#073B4C',
    'ТЦР-9': '#7209B7'
  }
  return tcrMap[tcr] || '#6C757D'
}

const getTCRTextColor = (tcr) => {
  const color = getTCRColor(tcr)
  const r = parseInt(color.slice(1, 3), 16)
  const g = parseInt(color.slice(3, 5), 16)
  const b = parseInt(color.slice(5, 7), 16)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  return brightness > 125 ? '#000' : '#FFF'
}

const calculateAverageLoad = (workshop) => {
  if (!workshop.sections.length) return 0
  const sum = workshop.sections.reduce((acc, section) => acc + section.workload, 0)
  return Math.round(sum / workshop.sections.length)
}

const countStorageSections = (workshop) => {
  const storageKeywords = ['склад', 'кладовая', 'хранение', 'запас']
  return workshop.sections.filter(section => 
    storageKeywords.some(keyword => 
      section.name.toLowerCase().includes(keyword)
    )
  ).length
}

const sortBy = (field) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const applyFilters = () => {
  // Фильтры применяются автоматически через computed свойство
}

const resetFilters = () => {
  filters.value = {
    status: '',
    tcr: '',
    category: ''
  }
}

const toggleWorkshopDetails = (workshopId) => {
  expandedWorkshop.value = expandedWorkshop.value === workshopId ? null : workshopId
}

const selectReport = (report) => {
  selectedReport.value = report
}

const editReport = (report) => {
  selectedReport.value = report
  console.log('Редактирование:', report)
}

const deleteReport = async (id) => {
  if (confirm('Вы уверены, что хотите удалить эту запись?')) {
    try {
      await axios.delete(`http://localhost:8000/api/reports/${id}`)
      await fetchData()
    } catch (error) {
      console.error('Ошибка удаления:', error)
    }
  }
}

const calculateTaskPosition = (startDateStr) => {
  const startDate = parseDate(startDateStr)
  const timelineStart = timelineDates.value[0]
  const timelineEnd = timelineDates.value[timelineDates.value.length - 1]
  
  const totalDays = (timelineEnd - timelineStart) / (1000 * 60 * 60 * 24)
  const daysFromStart = (startDate - timelineStart) / (1000 * 60 * 60 * 24)
  
  return Math.max(0, (daysFromStart / totalDays) * 100)
}

const calculateTaskWidth = (startDateStr, endDateStr) => {
  const startDate = parseDate(startDateStr)
  const endDate = parseDate(endDateStr)
  const days = (endDate - startDate) / (1000 * 60 * 60 * 24) + 1
  
  return Math.min(100, Math.max(5, days * 5))
}

// Получение данных
const fetchData = async () => {
  try {
    const [reportsResponse, ganttResponse] = await Promise.all([
      // axios.get('http://192.168.1.68:8000/api/reports'),
      // axios.get('http://192.168.1.68:8000/api/gantt')
      axios.get('http://localhost:8000/api/reports'),
      axios.get('http://localhost:8000/api/gantt')
    ])
    
    reports.value = reportsResponse.data
    ganttData.value = ganttResponse.data
    
    // Обновляем загрузку ТЦР на основе данных о ремонтах
    updateWorkshopWorkload()
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  }
}

const updateWorkshopWorkload = () => {
  // Сбрасываем загрузку
  workshops.value.forEach(workshop => {
    workshop.workload = 0
  })
  
  // Пересчитываем загрузку на основе текущих ремонтов
  reports.value.forEach(report => {
    if (report.status === 'предстоящая' || report.status === 'просрочено' || report.status === 'в работе') {
      const workshop = workshops.value.find(w => w.shortName === report.tcr)
      if (workshop) {
        const laborCost = parseInt(report.laborCost) || 0
        workshop.workload = Math.min(100, workshop.workload + laborCost)
      }
    }
  })
  
  // Ограничиваем значения от 0 до 100
  workshops.value.forEach(workshop => {
    workshop.workload = Math.min(100, Math.max(0, workshop.workload))
  })
}

// Хуки жизненного цикла
onMounted(async () => {
  await fetchData()
  
  // Автообновление
  const interval = setInterval(fetchData, 30000)
  
  onUnmounted(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.dashboard-header {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.dashboard-header h1 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 24px;
}

.filters {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 12px;
  color: #666;
  font-weight: bold;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  min-width: 150px;
  background: white;
  cursor: pointer;
}

.reset-btn {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
  align-self: flex-end;
  font-size: 14px;
}

.reset-btn:hover {
  background: #c82333;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card.total { border-top: 4px solid #4A90D9; }
.stat-card.upcoming { border-top: 4px solid #FFA500; }
.stat-card.completed { border-top: 4px solid #28a745; }
.stat-card.overdue { border-top: 4px solid #dc3545; }
.stat-card.working { border-top: 4px solid #35dc8e; }

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.tcr-summary {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.tcr-summary h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: transform 0.3s;
}

.summary-card:hover {
  transform: translateY(-3px);
}

.summary-card.busy { border-left: 4px solid #EF476F; }
.summary-card.medium { border-left: 4px solid #FFD166; }
.summary-card.free { border-left: 4px solid #06D6A0; }

.summary-icon {
  font-size: 40px;
  margin-right: 20px;
}

.summary-info h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 16px;
}

.summary-count {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 2px 0;
  color: #495057;
}

.summary-percent {
  font-size: 14px;
  color: #6c757d;
  margin: 0;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bar-chart-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.bar-label {
  width: 80px;
  font-size: 14px;
  font-weight: bold;
  color: #495057;
  text-align: right;
}

.bar-container {
  flex: 1;
  height: 30px;
  background: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.bar {
  height: 100%;
  min-width: 20px;
  transition: width 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
}

.bar.high { background: #EF476F; }
.bar.medium { background: #FFD166; }
.bar.normal { background: #06D6A0; }
.bar.low { background: #118AB2; }
.bar.very-low { background: #6C757D; }

.bar-value {
  color: white;
  font-size: 12px;
  font-weight: bold;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
}

.pie-chart-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
}

.pie-chart {
  flex-shrink: 0;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.legend-count {
  margin-left: auto;
  font-weight: bold;
  color: #495057;
}

.workshops-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.workshops-section h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.workshops-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.workshop-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  background: white;
}

.workshop-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.workshop-header {
  padding: 15px;
  background: #f8f9fa;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.3s;
}

.workshop-header:hover {
  background: #e9ecef;
}

.workshop-title h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.workshop-name {
  font-size: 12px;
  color: #6c757d;
  display: block;
  margin-top: 4px;
}

.workshop-stats {
  display: flex;
  align-items: center;
  gap: 15px;
}

.workload-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 100px;
}

.workload-bar {
  width: 60px;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.workload-fill {
  height: 100%;
  transition: width 0.3s;
}

.workload-fill.high { background: #EF476F; }
.workload-fill.medium { background: #FFD166; }
.workload-fill.normal { background: #06D6A0; }
.workload-fill.low { background: #118AB2; }
.workload-fill.very-low { background: #6C757D; }

.workload-value {
  font-weight: bold;
  font-size: 14px;
  min-width: 40px;
  color: #495057;
}

.toggle-icon {
  font-size: 20px;
  font-weight: bold;
  color: #6c757d;
  width: 20px;
  text-align: center;
}

.workshop-details {
  padding: 15px;
  background: white;
  border-top: 1px solid #e9ecef;
}

.workshop-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.summary-item .label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.summary-item .value {
  font-weight: bold;
  font-size: 18px;
  color: #2c3e50;
}

.sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 5px;
}

.section-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  border-left: 4px solid #4A90D9;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.section-name {
  font-size: 13px;
  color: #495057;
  flex: 1;
  margin-right: 10px;
}

.section-load {
  font-weight: bold;
  font-size: 14px;
  min-width: 40px;
  text-align: right;
}

.section-load.load-high { color: #EF476F; }
.section-load.load-medium { color: #FFD166; }
.section-load.load-normal { color: #06D6A0; }
.section-load.load-low { color: #118AB2; }
.section-load.load-very-low { color: #6C757D; }

.section-progress {
  margin-bottom: 10px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s;
}

.progress-fill.load-high { background: #EF476F; }
.progress-fill.load-medium { background: #FFD166; }
.progress-fill.load-normal { background: #06D6A0; }
.progress-fill.load-low { background: #118AB2; }
.progress-fill.load-very-low { background: #6C757D; }

.section-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  font-size: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  color: #6c757d;
  margin-bottom: 2px;
}

.info-value {
  font-weight: bold;
  color: #495057;
}

.dashboard-content {
  display: grid;
  gap: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.table-info {
  font-size: 14px;
  color: #6c757d;
}

.date-range {
  font-size: 14px;
  color: #6c757d;
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 4px;
}

.table-section,
.gantt-section,
.detail-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.reports-table th,
.reports-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.reports-table th {
  background: #f8f9fa;
  font-weight: bold;
  color: #495057;
  position: sticky;
  top: 0;
}

.reports-table th.sortable {
  cursor: pointer;
  transition: background 0.2s;
}

.reports-table th.sortable:hover {
  background: #e9ecef;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-arrow {
  font-size: 12px;
  color: #4A90D9;
}

.reports-table tr {
  cursor: pointer;
  transition: background 0.2s;
}

.reports-table tr:hover {
  background: #f8f9fa !important;
}

.item-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.item-text {
  min-width: 0;
}

.item-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-subtitle {
  font-size: 12px;
  color: #6c757d;
}

.factory-number {
  font-family: 'Courier New', monospace;
  color: #495057;
}

.date-cell {
  font-family: 'Courier New', monospace;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 4px;
}

.date-cell.overdue {
  color: #dc3545;
  font-weight: bold;
}

.overdue-icon {
  font-size: 14px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
  white-space: nowrap;
}

.status-upcoming {
  background: #e3f2fd;
  color: #1976d2;
}

.status-completed {
  background: #e8f5e9;
  color: #388e3c;
}

.status-overdue {
  background: #ffebee;
  color: #d32f2f;
}

.tcr-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  display: inline-block;
  white-space: nowrap;
}

.labor-cost {
  font-family: 'Courier New', monospace;
  color: #495057;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.edit {
  background: #ffc107;
  color: #000;
}

.action-btn.delete {
  background: #dc3545;
  color: white;
}

.action-btn:hover {
  opacity: 0.9;
  transform: scale(1.05);
}

.action-icon {
  font-size: 16px;
}

.empty-table {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-table p {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.reset-filters-btn {
  padding: 8px 20px;
  background: #4A90D9;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.reset-filters-btn:hover {
  background: #3a80c9;
}

.gantt-container {
  overflow-x: auto;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.gantt-timeline {
  min-width: 800px;
}

.timeline-header {
  display: flex;
  border-bottom: 2px solid #eee;
  padding: 10px;
  background: #f8f9fa;
}

.task-name-header {
  width: 200px;
  font-weight: bold;
  color: #495057;
  flex-shrink: 0;
  padding-right: 20px;
}

.timeline-dates {
  flex: 1;
  display: flex;
  gap: 1px;
  overflow-x: auto;
}

.timeline-date {
  flex: 1;
  min-width: 25px;
  text-align: center;
  font-size: 12px;
  color: #6c757d;
  padding: 4px 0;
  background: white;
}

.gantt-tasks {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px;
  background: white;
}

.gantt-task {
  display: flex;
  align-items: center;
  height: 40px;
}

.task-label {
  width: 200px;
  padding-right: 20px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
  color: #495057;
}

.task-bar-container {
  flex: 1;
  position: relative;
  height: 30px;
  background: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.task-bar {
  position: absolute;
  height: 100%;
  border-radius: 4px;
  min-width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
  overflow: hidden;
  transition: all 0.3s;
}

.task-status {
  padding: 2px 6px;
  background: rgba(0,0,0,0.3);
  border-radius: 3px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #dc3545;
}

.detail-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.detail-main {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e9ecef;
}

.detail-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.detail-title h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  flex: 1;
  margin-right: 20px;
}

.detail-status {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.detail-timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f8f9fa;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-label {
  font-size: 14px;
  color: #6c757d;
}

.timeline-value {
  font-weight: 500;
  color: #495057;
  font-family: 'Courier New', monospace;
}

.timeline-value.overdue {
  color: #dc3545;
  font-weight: bold;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.detail-group {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.detail-group.full-width {
  grid-column: 1 / -1;
}

.detail-group h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f8f9fa;
}

.detail-item {
  padding: 8px 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item strong {
  color: #495057;
  margin-right: 5px;
  display: inline-block;
  min-width: 200px;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .pie-chart-container {
    flex-direction: column;
    gap: 20px;
  }
}

@media (max-width: 992px) {
  .workshops-container {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  
  .sections-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group select {
    min-width: unset;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    min-width: unset;
  }
  
  .bar-chart-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .bar-label {
    width: auto;
    text-align: left;
  }
  
  .workshop-summary {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-title {
    flex-direction: column;
    gap: 10px;
  }
  
  .detail-status {
    width: 100%;
  }
  
  .detail-item strong {
    min-width: 150px;
  }
}

@media (max-width: 576px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .workshops-container {
    grid-template-columns: 1fr;
  }
  
  .workshop-stats {
    flex-direction: column;
    gap: 10px;
    align-items: flex-end;
  }
  
  .reports-table {
    font-size: 14px;
  }
  
  .reports-table th,
  .reports-table td {
    padding: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-btn {
    padding: 4px 8px;
  }
  
  .timeline-dates {
    min-width: 600px;
  }
}

/* ========== KPI Section ========== */
.kpi-section {
margin: 20px 0;
}

.kpi-section h2 {
margin-bottom: 15px;
font-size: 1.3rem;
color: #333;
}

.kpi-cards {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
gap: 20px;
}

.kpi-card {
background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
border-radius: 12px;
padding: 20px;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
display: flex;
align-items: flex-start;
gap: 15px;
border-left: 4px solid #4A90D9;
transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
transform: translateY(-2px);
box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.kpi-card.kpi-excellent {
border-left-color: #28a745;
}

.kpi-card.kpi-good {
border-left-color: #4A90D9;
}

.kpi-card.kpi-warning {
border-left-color: #ffc107;
}

.kpi-card.kpi-danger {
border-left-color: #dc3545;
}

.kpi-icon {
font-size: 2rem;
min-width: 50px;
text-align: center;
}

.kpi-content {
flex: 1;
}

.kpi-content h3 {
margin: 0 0 8px 0;
font-size: 0.95rem;
color: #555;
font-weight: 600;
}

.kpi-value {
font-size: 2rem;
font-weight: 700;
color: #333;
margin: 0 0 5px 0;
}

.kpi-description {
font-size: 0.85rem;
color: #777;
margin: 0 0 10px 0;
}

.kpi-formula {
background: #f0f4f8;
padding: 8px 12px;
border-radius: 6px;
font-size: 0.8rem;
}

.formula-label {
color: #666;
font-weight: 500;
}

.formula-text {
color: #4A90D9;
font-family: monospace;
margin-left: 5px;
}

.kpi-indicator {
width: 40px;
height: 40px;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
font-size: 1.2rem;
}

.kpi-indicator.indicator-success {
background: #d4edda;
color: #28a745;
}

.kpi-indicator.indicator-warning {
background: #fff3cd;
color: #856404;
}

.kpi-progress-ring {
color: #4A90D9;
}

.kpi-card.kpi-excellent .kpi-progress-ring {
color: #28a745;
}

.kpi-card.kpi-warning .kpi-progress-ring {
color: #ffc107;
}

.kpi-card.kpi-danger .kpi-progress-ring {
color: #dc3545;
}

/* ========== KPI Header with Button ========== */
.kpi-header {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 15px;
}

.view-all-kpi-btn {
padding: 8px 16px;
background: #4A90D9;
color: white;
border: none;
border-radius: 6px;
cursor: pointer;
font-size: 0.9rem;
transition: background 0.2s;
}

.view-all-kpi-btn:hover {
background: #357abd;
}

/* ========== KPI Modal ========== */
.kpi-modal-overlay {
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background: rgba(0, 0, 0, 0.5);
display: flex;
justify-content: center;
align-items: center;
z-index: 1000;
}

.kpi-modal {
background: white;
border-radius: 12px;
width: 90%;
max-width: 1200px;
max-height: 80vh;
display: flex;
flex-direction: column;
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.kpi-modal-header {
display: flex;
justify-content: space-between;
align-items: center;
padding: 20px;
border-bottom: 1px solid #e0e0e0;
}

.kpi-modal-header h2 {
margin: 0;
font-size: 1.3rem;
}

.kpi-modal-body {
padding: 20px;
overflow-y: auto;
}

.kpi-table {
width: 100%;
border-collapse: collapse;
}

.kpi-table th,
.kpi-table td {
padding: 12px;
text-align: left;
border-bottom: 1px solid #e0e0e0;
}

.kpi-table th {
background: #f8f9fa;
font-weight: 600;
color: #333;
position: sticky;
top: 0;
}

.kpi-table tbody tr:hover {
background: #f5f5f5;
}

.task-name-cell {
max-width: 250px;
overflow: hidden;
text-overflow: ellipsis;
white-space: nowrap;
}

.kpi-row-warning {
background: #fff8e6 !important;
}

.kpi-row-danger {
background: #ffe6e6 !important;
}

.cell-success {
color: #28a745;
font-weight: 600;
}

.cell-warning {
color: #ffc107;
font-weight: 600;
}

.cell-danger {
color: #dc3545;
font-weight: 600;
}

/* Адаптивность */
@media (max-width: 768px) {
.kpi-cards {
  grid-template-columns: 1fr;
}

.kpi-value {
  font-size: 1.5rem;
}
}
</style>