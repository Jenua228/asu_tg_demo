<script setup>
import { ref, computed } from 'vue'
import { token, logout } from './components/auth.js'
import { useI18n } from 'vue-i18n'
import { setLanguage } from './i18n'

import ReportsView from './views/ReportsView.vue'
import GanttView from './views/GanttView.vue'
import DetailedGanttView from './views/DetailedGanttView.vue'
import BlockView from './views/Block.vue'
import Store from './views/Store.vue'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Dashboard2 from './views/Dashboard2.vue'
import Fault from './views/FaultAnalyze.vue'
import Document from './views/Document.vue'


const currentView = ref('Dashboard')
const selectedReportForDetail = ref(null)
const isSidebarCollapsed = ref(false)
const { t, locale } = useI18n()

// Поддерживаемые языки
const languages = [
  { code: 'ru', name: 'Русский', flag: 'RU' },
  { code: 'en', name: 'English', flag: 'EN' }
]

const currentLanguage = ref(locale.value)
const changeLanguage = (lang) => {
  setLanguage(lang)
  locale.value = lang
  currentLanguage.value = lang
}

// Обработчик перехода к детализации
const navigateToDetail = (reportRow) => {
  selectedReportForDetail.value = reportRow
  currentView.value = 'detailed-gantt'
}

// Возврат из детализации
const backFromDetail = () => {
  selectedReportForDetail.value = null
  currentView.value = 'reports'
}

// Переключение состояния меню
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const menuItems = computed(() => [
  { id: 'Dashboard', label: t('menu.dashboard'), icon: '📊' },
  { id: 'Dashboard2', label: t('menu.dashboard2'), icon: '📊' },
  { id: 'reports', label: t('menu.reports'), icon: '📋' },
  { id: 'gantt', label: t('menu.gantt'), icon: '📅' },
  { id: 'block', label: t('menu.block'), icon: '🔲' },
  { id: 'faultanalyze', label: t('menu.faultAnalyze'), icon: '🔧' },
  { id: 'Document', label: t('menu.documents'), icon: '📦' },
  { id: 'Store', label: t('menu.store'), icon: '📦' }
])

// Вычисляемое свойство для ширины сайдбара
const sidebarWidth = computed(() => {
  return isSidebarCollapsed.value ? '80px' : '220px'
})
</script>

<template>
  <div v-if="token" class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :style="{ width: sidebarWidth }">
      <div class="sidebar-header">
        <img 
          src="/logo.png" 
          alt="АСУ ТГ" 
          style="max-width: 100%; height: auto;"
        >
        <h5 v-if="isSidebarCollapsed">{{ $t('menu.asu') }}</h5>
        <h1 v-else>{{ $t('menu.asu') }}</h1>
      </div>
      
      <!-- Улучшенная кнопка переключения -->
      <button class="toggle-btn" @click="toggleSidebar" :title="isSidebarCollapsed ? 'Развернуть меню' : 'Свернуть меню'">
        <div class="toggle-icon">
          <div class="toggle-line" :class="{ 'collapsed': isSidebarCollapsed }"></div>
          <div class="toggle-line" :class="{ 'collapsed': isSidebarCollapsed }"></div>
          <div class="toggle-line" :class="{ 'collapsed': isSidebarCollapsed }"></div>
        </div>
      </button>
      
      <nav class="sidebar-nav">
        <button 
          v-for="item in menuItems"
          :key="item.id"
          class="nav-btn"
          :class="{ 
            active: currentView === item.id,
            'collapsed': isSidebarCollapsed 
          }"
          @click="currentView = item.id"
          :title="isSidebarCollapsed ? item.label : ''"
        >
          <!-- Минималистичные черно-белые иконки -->
          <div class="nav-icon-wrapper">
            <svg v-if="item.id === 'Dashboard'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="14" y="3" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="3" y="14" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="14" y="14" width="7" height="7" rx="1" stroke-width="2"/>
            </svg>
            <svg v-if="item.id === 'Dashboard2'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="14" y="3" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="3" y="14" width="7" height="7" rx="1" stroke-width="2"/>
              <rect x="14" y="14" width="7" height="7" rx="1" stroke-width="2"/>
            </svg>
            
            <svg v-else-if="item.id === 'reports'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2v6h6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 13H8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 17H8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 9H8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            
            <svg v-else-if="item.id === 'gantt'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="2"/>
              <path d="M3 10h18" stroke-width="2" stroke-linecap="round"/>
              <path d="M8 14h4" stroke-width="2" stroke-linecap="round"/>
              <path d="M13 14h5" stroke-width="2" stroke-linecap="round"/>
              <path d="M3 16h4" stroke-width="2" stroke-linecap="round"/>
            </svg>
            
            <svg v-else-if="item.id === 'block'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2"/>
              <path d="M9 3v18" stroke-width="2" stroke-linecap="round"/>
              <path d="M15 3v18" stroke-width="2" stroke-linecap="round"/>
              <path d="M3 9h18" stroke-width="2" stroke-linecap="round"/>
              <path d="M3 15h18" stroke-width="2" stroke-linecap="round"/>
            </svg>
            
            <svg v-else-if="item.id === 'faultanalyze'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9.5 9h5M9.5 12h5" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 15v3" stroke-width="2" stroke-linecap="round"/>
            </svg>
            
            <svg v-else-if="item.id === 'Document'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <path d="M14 2v6h6"></path>
              <path d="M16 13H8"></path>
              <path d="M16 17H8"></path>
              <path d="M10 9H8"></path>
            </svg>
            <svg v-else-if="item.id === 'Store'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M20 7h-4V5c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 12v4" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 8v1" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          
          <span v-if="!isSidebarCollapsed" class="nav-text">
            {{ item.label }}
          </span>
        </button>
      </nav>
      

      <!-- Language Selector -->
      <div class="language-selector" :class="{ 'collapsed': isSidebarCollapsed }">
        <button 
          v-for="lang in languages" 
          :key="lang.code"
          class="lang-btn"
          :class="{ active: currentLanguage === lang.code }"
          @click="changeLanguage(lang.code)"
          :title="lang.name"
        >
          {{ lang.flag }}
          <!-- :class="['lang-btn', { active: currentLanguage === lang.code }]" -->
        </button>
      </div>
      
      <button 
        class="btn-ext"
        :class="{ 'collapsed': isSidebarCollapsed }"
        @click="logout"
        :title="isSidebarCollapsed ? 'Выйти' : ''"
      >
        <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="m16 17 5-5-5-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M21 12H9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span v-if="!isSidebarCollapsed" class="logout-text">{{ $t('menu.logout') }}</span>
      </button>
    </aside>
    
    <!-- Main content -->
    <main 
      class="main-content" 
      :style="{ marginLeft: sidebarWidth }"
    >
      <!-- Reports View (AG Grid Table) -->
      <ReportsView 
        v-if="currentView === 'reports'" 
        @navigate-to-detail="navigateToDetail"
      />
      
      <!-- Gantt View -->
      <GanttView v-else-if="currentView === 'gantt'" />

      <!-- Detailed Gantt View (новая страница) -->
      <DetailedGanttView 
        v-else-if="currentView === 'detailed-gantt' && selectedReportForDetail"
        :report-id="selectedReportForDetail.id"
        @back="backFromDetail"
      />
      
      <!-- Анализ -->
      <Fault v-else-if="currentView === 'faultanalyze'" />

      <BlockView v-else-if="currentView === 'block'" />

      <Document v-else-if="currentView === 'Document'" />

      <Store v-else-if="currentView === 'Store'" />

      <Dashboard v-else-if="currentView === 'Dashboard'" />
      <Dashboard2 v-else-if="currentView === 'Dashboard2'" />
    </main>
  </div>
  <Login v-else />
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  transition: all 0.3s ease;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
  color: #212529;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-x: hidden;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.08);
  border-right: 1px solid #dee2e6;
}

.sidebar-header {
  padding: 24px 10px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  border-bottom: 1px solid #e9ecef;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  /* min-height: 120px; */
  background: #ffffff;
}

.sidebar-header h2 {
  font-size: 16px;
  margin: 0;
  transition: all 0.3s ease;
  color: #343a40;
  font-weight: 600;
}

.logo {
  max-width: 120px;
  max-height: 50px;
  object-fit: contain;
  filter: grayscale(100%) contrast(120%);
}

.collapsed-logo {
  font-size: 18px;
  font-weight: 700;
  color: #343a40;
  padding: 15px 0;
  letter-spacing: 1px;
}

/* Улучшенная кнопка переключения */
.toggle-btn {
  position: absolute;
  top: 50vh;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #ffffff;
  border: 2px solid #dee2e6;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #495057;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1001;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toggle-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toggle-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 12px;
  height: 12px;
  position: relative;
}

.toggle-line {
  width: 100%;
  height: 2px;
  background: #495057;
  margin: 1px 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 1px;
}

.toggle-line:nth-child(1) {
  transform-origin: left center;
}

.toggle-line:nth-child(2) {
  width: 80%;
}

.toggle-line:nth-child(3) {
  transform-origin: left center;
}

.toggle-line.collapsed:nth-child(1) {
  transform: rotate(45deg) translate(1px, -1px);
}

.toggle-line.collapsed:nth-child(2) {
  opacity: 0;
  transform: translateX(-5px);
}

.toggle-line.collapsed:nth-child(3) {
  transform: rotate(-45deg) translate(1px, 1px);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 20px 10px;
  gap: 4px;
  flex: 1;
}

.nav-btn {
  background: transparent;
  border: none;
  color: #495057;
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 14px;
  white-space: normal;
  overflow: visible;
  line-height: 1.4;
  min-height: 52px;
  border: 1px solid transparent;
}

.nav-btn:hover {
  background: #f1f3f5;
  color: #212529;
  border-color: #e9ecef;
  transform: translateX(2px);
}

.nav-btn.active {
  background: #ffffff;
  color: #212529;
  font-weight: 600;
  border-color: #dee2e6;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.nav-btn.active .nav-icon {
  stroke: #000000;
}

.nav-btn.collapsed {
  justify-content: center;
  padding: 14px;
  min-height: 52px;
  border-radius: 10px;
}

.nav-btn.collapsed:hover {
  transform: scale(1.05);
}

.nav-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  stroke: #6c757d;
  stroke-width: 1.8;
  transition: all 0.3s ease;
}

.nav-btn:hover .nav-icon {
  stroke: #495057;
}

.nav-btn.active .nav-icon {
  stroke: #212529;
  stroke-width: 2;
}

.nav-text {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.3px;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  width: 100%;
  font-size: 12px;
  line-height: 1.3;
}

.nav-btn:not(.collapsed) .nav-text {
  display: inline-block;
  max-width: 150px;
}

.nav-btn.collapsed .nav-text {
  opacity: 0;
  width: 0;
  display: none;
}

.main-content {
  flex: 1;
  background: #f8f9fa;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
}

.language-selector {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0px 16px;
  border-top: 1px solid #e9ecef;
  margin-top: auto;
}

.language-selector.collapsed {
  flex-direction: column;
  padding: 8px;
}

.lang-btn {
  padding: 8px 16px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  background: #ffffff;
  color: #495057;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.2s ease;
}

.lang-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.lang-btn.active {
  background: #343a40;
  color: #ffffff;
  border-color: #343a40;
}

.btn-ext {
  margin-top: auto;
  padding: 16px 20px;
  height: 56px;
  border: none;
  border-radius: 10px;
  background: #ffffff;
  color: #495057;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 14px;
  justify-content: center;
  white-space: nowrap;
  overflow: hidden;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  border-top: 1px solid #e9ecef;
  /* margin: 10px; */
  border: 1px solid #e9ecef;
}

.btn-ext:hover {
  background: #f8f9fa;
  color: #212529;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.btn-ext.collapsed {
  padding: 16px;
  justify-content: center;
  margin: 10px;
}

.logout-text {
  transition: all 0.3s ease;
  opacity: 1;
}

.btn-ext.collapsed .logout-text {
  opacity: 0;
  width: 0;
  display: none;
}

.logout-icon {
  width: 18px;
  height: 18px;
  stroke: #6c757d;
  stroke-width: 1.8;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.btn-ext:hover .logout-icon {
  stroke: #212529;
}

/* Анимация для перехода текста */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.nav-btn:not(.collapsed) .nav-text {
  animation: fadeIn 0.3s ease;
}

/* Медиазапрос для адаптивности */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
  
  .toggle-btn {
    position: fixed;
    top: 20px;
    left: 20px;
    right: auto;
    z-index: 1002;
    background: #ffffff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .nav-btn:not(.collapsed) .nav-text {
    max-width: 140px;
    font-size: 11px;
  }
}

/* Дополнительные стили для улучшения читаемости */
@media (max-width: 480px) {
  .sidebar:not(.collapsed) {
    width: 200px !important;
  }
  
  .nav-btn:not(.collapsed) {
    padding: 12px 14px;
    font-size: 11px;
  }
  
  .nav-btn:not(.collapsed) .nav-text {
    max-width: 120px;
  }
}

/* Плавный скролл для основного контента */
.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: #f1f3f5;
}

.main-content::-webkit-scrollbar-thumb {
  background: #ced4da;
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #adb5bd;
}
</style>