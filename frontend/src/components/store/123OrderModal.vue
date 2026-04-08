<script setup>
import { ref } from 'vue'

const isSuccess = ref(false)

const props = defineProps({
  modelValue: Boolean,
  inventory: Array // Список товаров из основной таблицы
})

const emit = defineEmits(['update:modelValue', 'submit'])

const order = ref({
  selectedProduct: '',
  count: 1,
  comment: ''
})

const close = () => {
  emit('update:modelValue', false)
  order.value = { selectedProduct: '', count: 1, comment: '' }
}

const submitOrder = () => {
  if (!order.value.selectedProduct) return alert('Выберите товар')
  
  // Имитируем отправку в логи/бэкенд
  console.log("📝 ЛОГ ЗАКАЗА:", {
    timestamp: new Date().toISOString(),
    article: order.value.selectedProduct,
    quantity: order.value.count,
    comment: order.value.comment
  })

  // Эмитим событие для обновления таблицы
  emit('submit', { ...order.value })

  // Показываем сообщение об успехе
  isSuccess.value = true

  // Закрываем окно через 1.5 секунды
  setTimeout(() => {
    close()
    isSuccess.value = false // Сбрасываем статус для следующего открытия
  }, 1000)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal-content order-modal">
        <div v-if="isSuccess" class="success-overlay">
          <div class="success-message">
            <span class="check-icon">✅</span>
            <p>Ваш заказ успешно оформлен</p>
          </div>
        </div>

        <div v-else>
            <h3>Оформление заказа</h3>
            <div class="form-grid">
            <div class="input-group">
                <label>Выберите товар (Артикул + Название)</label>
                <select v-model="order.selectedProduct" class="custom-select">
                <option value="" disabled>-- Выберите из списка --</option>
                <option v-for="item in inventory" :key="item.Article" :value="item.Article">
                    [{{ item.Article }}] {{ item.num_rus }}
                </option>
                </select>
            </div>

            <div class="input-group">
                <label>Количество для заказа</label>
                <input v-model.number="order.count" type="number" min="1">
            </div>

            <div class="input-group">
                <label>Комментарий к заказу</label>
                <textarea v-model="order.comment" placeholder="Укажите детали заказа..."></textarea>
            </div>
            </div>

            <div class="modal-actions">
            <button @click="close" class="btn-cancel">Отмена</button>
            <button @click="submitOrder" class="btn-order">Оформить заказ</button>
            </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Используем те же стили, что в первой модалке, добавляя специфичные */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; padding: 24px; border-radius: 20px; width: 450px;
}
.custom-select {
  padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; background: white;
}
.btn-order {
  background: #005fcc; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;
}

.success-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  animation: fadeIn 0.3s ease;
}

.success-message {
  text-align: center;
}

.check-icon {
  font-size: 50px;
  display: block;
  margin-bottom: 10px;
}

.success-message p {
  font-size: 18px;
  font-weight: 600;
  color: #059669;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

.input-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 15px; }
.input-group label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; }
input, textarea, select { width: 100%; box-sizing: border-box; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; }
.btn-cancel { background: #f1f5f9; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
</style>
