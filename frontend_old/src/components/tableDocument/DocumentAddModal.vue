<script setup>
import { ref } from 'vue';

const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue', 'add']);

const form = ref({ 
  type: '', 
  title: '', 
  date: '', 
  note: '', 
  pdfUrl: '' 
});

const save = () => {
  // Добавляем текущую дату, если пользователь не ввел
  if (!form.value.date) {
    form.value.date = new Date().toISOString().split('T')[0];
  }
  emit('add', { ...form.value });
  close();
};

const close = () => {
  emit('update:modelValue', false);
  // Сброс формы при закрытии
  form.value = { type: '', title: '', date: '', note: '', pdfUrl: '' };
};
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal-content add-doc-modal">
        
        <div class="modal-header">
          <h3>Новый документ</h3>
          <button class="close-x" @click="close">&times;</button>
        </div>

        <div class="form-grid">
            <input v-model="form.type" placeholder="Тип (Инструкция, Договор...)" class="styled-input" />
            <input v-model="form.title" placeholder="Название документа" class="styled-input" />
            
            <div class="input-with-icon">
                <input v-model="form.date" type="date" class="styled-input" placeholder="дд.мм.гггг" />
            </div>

            <textarea v-model="form.note" placeholder="Примечание" class="styled-input" rows="3"></textarea>

            <input v-model="form.pdfUrl" placeholder="Ссылка на PDF-документ (необязательно)" class="styled-input" />
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="close">Отмена</button>
          <button class="btn btn-save" @click="save">Добавить</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Базовые стили для наложения и фона окна (переиспользуются из PdfModal) */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(4px);
  display: flex; 
  justify-content: center; /* Центрирует по горизонтали */
  align-items: center;     /* Центрирует по вертикали */
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; padding: 24px; border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 90vw;
  max-width: 600px; /* Увеличил ширину для удобства */
}
/* Стили заголовка и кнопки закрытия */
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.modal-header h3 { margin: 0; font-size: 24px; color: #1e293b; }
.close-x {
  background: none; border: none; cursor: pointer; font-size: 36px; color: #475569;
}
.close-x:hover { color: #1e293b; }

/* Стилизация формы (сетка) */
.form-grid {
    display: grid;
    /* Устанавливаем одну колонку, занимающую всю ширину (100%) */
    grid-template-columns: 1fr; 
    gap: 15px;
    /* Ограничиваем ширину контейнера формы и центрируем его */
    max-width: 500px; 
    margin: 0 auto;
}


.styled-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  font-size: 16px;
  box-sizing: border-box;
}

/* Контейнер для кнопки и инпутов */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

.btn { padding: 10px 20px; border-radius: 8px; cursor: pointer; border: none; font-weight: 600; }
.btn-save { background: #5bc06398; color: black; }
.btn-save:hover { background: #5bc063; }
.btn-cancel { background: #e2e8f0; color: #475569; }

/* Эффект иконки календаря в поле даты */
.input-with-icon {
  position: relative;
}
.input-with-icon .icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none; /* Чтобы можно было кликнуть на сам инпут */
  font-size: 18px;
}

</style>
