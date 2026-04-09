<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean // Управляет видимостью (v-model)
})

const emit = defineEmits(['update:modelValue', 'add'])

const initialState = {
  Number: '',
  Article: '',
  num_rus: '',
  num_eng: '',
  count: 0,
  min_sctock: 0,
  name_storage: '',
  comment: ''
}

const newItem = ref({ ...initialState })

const close = () => {
  emit('update:modelValue', false)
  newItem.value = { ...initialState } // Сброс формы
}

const save = () => {
  emit('add', { ...newItem.value })
  close()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Добавление имущества</h3>
          <button class="close-x" @click="close">&times;</button>
        </div>

        <div class="form-grid">
          <div class="input-group">
            <label>Идентификация</label>
            <div class="row">
              <input v-model="newItem.Number" placeholder="№ п/п" class="flex-1">
              <input v-model="newItem.Article" placeholder="Артикул" class="flex-2">
            </div>
          </div>

          <div class="input-group">
            <label>Номенклатура</label>
            <input v-model="newItem.num_rus" placeholder="Название (RU)">
            <input v-model="newItem.num_eng" placeholder="Name (EN)">
          </div>

          <div class="input-group highlight">
            <div class="row">
              <div class="col">
                <label>Текущее кол-во</label>
                <input v-model.number="newItem.count" type="number">
              </div>
              <div class="col">
                <label>Мин. запас</label>
                <input v-model.number="newItem.min_sctock" type="number">
              </div>
            </div>
            <p v-if="newItem.count < newItem.min_sctock" class="warning-text">
              ⚠️ Будет подсвечено красным (ниже лимита)
            </p>
          </div>

          <div class="input-group">
            <label>Склад и примечание</label>
            <input v-model="newItem.name_storage" placeholder="Склад">
            <textarea v-model="newItem.comment" placeholder="Комментарий..."></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="close" class="btn-cancel">Отмена</button>
          <button @click="save" class="btn-save">Добавить в базу</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; padding: 24px; border-radius: 20px; width: 480px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-x { background: none; border: none; font-size: 24px; cursor: pointer; color: #94a3b8; }
.form-grid { display: flex; flex-direction: column; gap: 16px; }
.input-group { display: flex; flex-direction: column; gap: 6px; }
.input-group label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; }
.row { display: flex; gap: 12px; }
.col { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.highlight { background: #f1f5f9; padding: 12px; border-radius: 12px; }
.warning-text { color: #e11d48; font-size: 11px; margin-top: 5px; font-weight: 500; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.flex-1 { flex: 1; } .flex-2 { flex: 2; }
input, textarea { padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; width: 100%; box-sizing: border-box; }
.btn-save { background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.btn-cancel { background: #f1f5f9; color: #475569; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
</style>
