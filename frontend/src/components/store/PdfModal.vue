<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  pdfUrl: String,
  isEditMode: Boolean // Добавляем проп для переключения режима (просмотр/добавление)
});

const emit = defineEmits(['update:modelValue', 'update-pdf']);

const newUrl = ref('');
const isError = ref(false);

// Синхронизируем поле ввода с текущим URL при открытии
watch(() => props.modelValue, (val) => {
  if (val) newUrl.value = props.pdfUrl || '';
  isError.value = false;
});

const close = () => {
  emit('update:modelValue', false);
};

const saveDocument = () => {
  if (!newUrl.value.trim()) return;

  // Имитация загрузки на бэкенд
  /* 
  const formData = new FormData();
  formData.append('pdf', newUrl.value);
  axios.post('/api/upload', formData)... 
  */
  
  console.log('Документ прикреплен локально:', newUrl.value);
  emit('update-pdf', newUrl.value); // Передаем новую ссылку родителю
  close();
};

const markAsError = () => { isError.value = true; };
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal-content order-modal pdf-modal-inner">
        
        <div class="modal-header">
          <h3>{{ isEditMode ? 'Прикрепить документ' : 'Просмотр документа' }}</h3>
          <button class="close-x" @click="close">&times;</button>
        </div>

        <!-- РЕЖИМ ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ -->
        <div v-if="isEditMode" class="upload-container">
          <div class="input-group">
            <label>Ссылка на PDF документ или путь к файлу:</label>
            <input 
              v-model="newUrl" 
              type="text" 
              placeholder="/doc/store/filename.pdf"
              class="styled-input"
            />
          </div>
          <!-- <p class="hint">Бэкенд не подключен: изменение применится только в текущей сессии.</p> -->
          <div class="modal-footer">
            <button class="btn btn-cancel" @click="close">Отмена</button>
            <button class="btn btn-save" @click="saveDocument">Сохранить ссылку</button>
          </div>
        </div>

        <!-- РЕЖИМ ПРОСМОТРА (твой старый код) -->
        <template v-else>
          <div v-if="isError" class="pdf-error-container">
              <h3>Документ не найден</h3>
              <button class="btn-cancel" @click="close">Закрыть</button>
          </div>
          <div v-else class="pdf-viewer-container">
            <iframe :src="pdfUrl + '#view=FitH'" frameborder="0"></iframe>
            <button class="btn-error-manual" @click="markAsError">Ошибка загрузки</button>
          </div>
        </template>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Стили из предыдущего шага остаются, добавляем новые */
.pdf-error-container {
    padding: 40px;
    text-align: center;
    color: #b91c1c;
    background: #fef2f2;
    border: 2px dashed #f87171;
    border-radius: 12px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.btn-error-manual {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background: #f97316;
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-size: 12px;
}

/* Базовые стили для наложения и фона окна */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; padding: 24px; border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

/* Стили заголовка и кнопки закрытия */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 15px;
}
.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}
.close-x {
  background: none; border: none; cursor: pointer;
  font-size: 36px; color: #475569;
  position: absolute; right: 0; top: 50%; transform: translateY(-50%);
  padding: 0 10px;
}
.close-x:hover { color: #1e293b; }

/* Увеличенный размер окна для просмотра PDF */
.pdf-modal-inner {
  width: 90vw;
  max-width: 1200px;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Контейнер и iframe */
.pdf-viewer-container {
  flex-grow: 1;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background-color: #f8fafc;
}
.pdf-viewer-container iframe {
  width: 100%;
  height: 100%;
}

.upload-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.styled-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 16px;
}
.hint { font-size: 12px; color: #64748b; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: auto;
}
.btn-save { background: #059669; color: white; padding: 10px 20px; border-radius: 8px; cursor: pointer; border: none; }
.btn-cancel { background: #e2e8f0; color: #475569; padding: 10px 20px; border-radius: 8px; cursor: pointer; border: none; }

</style>
