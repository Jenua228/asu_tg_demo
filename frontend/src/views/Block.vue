<template>
  <div id="app">
    <!-- <header class="app-header">
      <h1>🛠 Блок-схема получения и ремонта изделия</h1>
      <p class="subtitle">Создайте и отредактируйте процесс ремонта изделий</p>
    </header> -->
    <main class="app-main">
      <Flowchart />
      <div class="zoom-hint">
        {{ $t('zoom.hint') }}
      </div>
          <!-- Zoom indicator -->
      <div class="zoom-indicator" v-if="zoomLevel !== 1.0">
        {{ Math.round(zoomLevel * 100) }}%
      </div>
    </main>

    <!-- <footer class="app-footer">
      <div class="footer-content">
        <div class="instructions">
          <h4>Инструкция:</h4>
          <ul>
            <li><strong>Перетаскивание:</strong> Зажмите и перетащите узел</li>
            <li><strong>Выбор:</strong> Клик по узлу или соединению</li>
            <li><strong>Удаление:</strong> Выделите элемент и нажмите "Удалить" или Delete</li>
            <li><strong>Соединение:</strong> Выберите 2 узла и нажмите "Соединить"</li>
            <li><strong>Редактирование:</strong> Выделите элемент и используйте панель справа</li>
          </ul>
        </div>
        <div class="shortcuts">
          <h4>Горячие клавиши:</h4>
          <ul>
            <li><kbd>Delete</kbd> - Удалить выбранный элемент</li>
            <li><kbd>Ctrl</kbd> + <kbd>Клик</kbd> - Множественный выбор</li>
            <li><kbd>Ctrl</kbd> + <kbd>S</kbd> - Сохранить</li>
            <li><kbd>Ctrl</kbd> + <kbd>L</kbd> - Загрузить</li>
          </ul>
        </div>
      </div>
      <div class="copyright">
        © 2025 Система управления ремонтом изделий
      </div>
    </footer> -->
    
  </div>
</template>

<script setup>
import Flowchart from '../components/Flowchart.vue'
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

.app-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.app-main {
  flex: 1;
  /* padding: 20px; */
}

.app-footer {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px 30px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-bottom: 20px;
}

.instructions h4,
.shortcuts h4 {
  color: #4fc3f7;
  margin-bottom: 10px;
  font-size: 16px;
}

.instructions ul,
.shortcuts ul {
  list-style: none;
  padding-left: 0;
}

.instructions li,
.shortcuts li {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.shortcuts kbd {
  background: #333;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.copyright {
  text-align: center;
  font-size: 14px;
  color: #aaa;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}


.zoom-indicator {
position: absolute;
bottom: 16px;
right: 16px;
background: var(--bg-elevated);
border: 1px solid var(--border-subtle);
color: var(--accent-primary);
padding: 6px 12px;
border-radius: var(--radius-md);
font-size: 12px;
font-weight: 600;
z-index: 1000;
box-shadow: var(--shadow-md);
}

.zoom-hint {
position: absolute;
bottom: 16px;
right: 80px;
background: var(--bg-elevated);
border: 1px solid var(--border-subtle);
color: var(--text-muted);
padding: 6px 12px;
border-radius: var(--radius-md);
font-size: 10px;
z-index: 1000;
box-shadow: var(--shadow-sm);
opacity: 0.7;
}
</style>