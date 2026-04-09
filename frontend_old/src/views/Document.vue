<script setup>
import { computed, ref } from 'vue';
// AgGridVue и PdfModal (DocumentAddModal нужно импортировать отдельно, если вы его создали)
import { AgGridVue } from 'ag-grid-vue3';
import PdfModal from '../components/store/PdfModal.vue'; 
import DocumentAddModal from '../components/tableDocument/DocumentAddModal.vue'; // Если создали отдельный файл
import { useI18n } from 'vue-i18n'

// --- Переменные состояния ---
const gridApi = ref(null);
const selectedPdfUrl = ref(null); 
const isPdfModalOpen = ref(false);
const isEditPdfMode = ref(false);
const isRowSelected = ref(false);
const isAddModalOpen = ref(false); // Для модалки добавления
const { t } = useI18n()

// --- Данные для таблицы (Замените своими данными) ---
const rowData = ref([
  { id: 1, type: 'Инструкция', title: 'Инструкция ремонту блока ШИБФ.460626.558 Д27', date: '2024-01-15', note: '', pdfUrl: '/doc/1/1.pdf' },
  { id: 2, type: 'Документ', title: 'Соответствие ГОСТ 12.2.007.0-75', date: '2024-02-20', note: 'Актуально', pdfUrl: '/doc/1/2.pdf' },
  { id: 3, type: 'Документ', title: 'Акт приёма-передачи оборудования', date: '2024-03-10', note: '', pdfUrl: '/doc/1/3.pdf' },
  { id: 4, type: 'Документ', title: 'Эксплуатация блока управления', date: '2024-04-05', note: '', pdfUrl: '/doc/1/4.pdf' },
  { id: 5, type: 'Акт приёма', title: 'Акт приёма выполненных работ', date: '2024-05-18', note: 'Завершено', pdfUrl: '/doc/1/5.pdf' },
  { id: 6, type: 'Акт приёма', title: 'Акт приёма блока питания', date: '2024-06-25', note: '', pdfUrl: '/doc/1/6.pdf' },
  { id: 7, type: 'Акт приёма', title: 'Акт приёма после ремонта', date: '2024-07-12', note: '', pdfUrl: '/doc/1/1.pdf' },
  { id: 8, type: 'Акт приёма', title: 'Соответствие техническим условиям', date: '2024-08-30', note: '', pdfUrl: '/doc/1/2.pdf' },
  { id: 9, type: 'Документ', title: 'Акт приёма-сдачи работ', date: '2024-09-01', note: 'Срочно', pdfUrl: '/doc/1/3.pdf' },
  { id: 10, type: 'Инструкция', title: 'Эксплуатация тестового стенда', date: '2024-10-14', note: '', pdfUrl: '/doc/1/4.pdf' },
  { id: 11, type: 'Инструкция', title: 'Соответствие ISO 9001', date: '2024-11-21', note: '', pdfUrl: '/doc/1/5.pdf' },
  { id: 12, type: 'Договор', title: 'Договор на техническое обслуживание', date: '2024-12-08', note: '', pdfUrl: '/doc/1/6.pdf' },
  { id: 13, type: 'Договор', title: 'Договор на поставку комплектующих', date: '2025-01-22', note: 'Актуально', pdfUrl: '/doc/1/1.pdf' },
  { id: 14, type: 'Договор', title: 'Соответствие требованиям безопасности', date: '2025-02-17', note: '', pdfUrl: '/doc/1/2.pdf' },
  { id: 15, type: 'Документ', title: 'Акт приёма в эксплуатацию', date: '2025-03-03', note: '', pdfUrl: '/doc/1/3.pdf' },
  { id: 16, type: 'Инструкция', title: 'Эксплуатация измерительного оборудования', date: '2025-04-19', note: '', pdfUrl: '/doc/1/4.pdf' },
  { id: 17, type: 'Документ', title: 'Соответствие стандартам качества', date: '2025-05-26', note: '', pdfUrl: '/doc/1/5.pdf' },
  { id: 18, type: 'Документ', title: 'Акт приёма после поверки', date: '2025-06-11', note: 'Выполнено', pdfUrl: '/doc/1/6.pdf' },
]);

// --- Настройки AG Grid ---

const defaultColDef = {
  flex: 1,
  minWidth: 100,
  sortable: true,
  filter: true,
  editable: true,
  wrapText: true,
  autoHeight: false,
};

const columnDefs = computed(() => [
  { headerName: t('documents.columns.id'), field: "id", width: 70 },
  { headerName: t('documents.columns.type'), field: "type" },
  { headerName: t('documents.columns.title'), field: "title" },
  { 
    headerName: t('documents.columns.document'), // Переименовали "Док." в "Документ"
    field: "pdfUrl", 
    width: 120,
    cellClass: ['grid-cell-centered', 'link-style'], // Добавляем класс стиля ссылки
    cellRenderer: params => params.value ? '📄' : '—',
    tooltipValueGetter: (params) => params.value ? `Файл: ${params.value}` : 'Файл отсутствует'
  },
  { headerName: t('documents.columns.date'), field: "date" },
  { headerName: t('documents.columns.note'), field: "note" },
  {
    headerName: t('documents.columns.actions'),
    width: 100,
    lockPosition: 'right', // Закрепляем справа
    cellClass: 'grid-cell-centered',
    cellRenderer: (params) => {
      const button = document.createElement('button');
      button.innerText = t('documents.delete');
      button.classList.add('btn', 'btn-delete-row'); // Используем стили кнопок
      
      // При клике вызываем нашу функцию удаления, передавая ID строки
      button.addEventListener('click', () => {
        if (confirm(`Вы уверены, что хотите удалить документ "${params.data.title}"?`)) {
          deleteDocument(params.data.id);
        }
      });
      
      return button;
    }
  },
]);

const localeRu = computed(()  => ({
  // Фильтры
  contains: t('agGrid.contains'),
  notContains: t('agGrid.notContains'),
  equals: t('agGrid.equals'),
  notEqual: t('agGrid.notEqual'),
  startsWith: t('agGrid.startsWith'),
  endsWith: t('agGrid.endsWith'),
  blank: t('agGrid.blank'),
  notBlank: t('agGrid.notBlank'),
  
  // Числовые фильтры
  lessThan: t('agGrid.lessThan'),
  greaterThan: t('agGrid.greaterThan'),
  lessThanOrEqual: t('agGrid.lessThanOrEqual'),
  greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
  inRange: t('agGrid.inRange'),
  
  // Условия
  andCondition: t('agGrid.andCondition'),
  orCondition: t('agGrid.orCondition'),
  
  // Панель фильтров
  filterOoo: t('agGrid.filterOoo'),
  applyFilter: t('agGrid.applyFilter'),
  resetFilter: t('agGrid.resetFilter'),
  clearFilter: t('agGrid.clearFilter'),
  
  // Пагинация
  page: t('agGrid.page'),
  more: t('agGrid.more'),
  of: t('agGrid.of'),
  to: t('agGrid.to'),
  nextPage: t('agGrid.nextPage'),
  previousPage: t('agGrid.previousPage'),
  firstPage: t('agGrid.firstPage'),
  lastPage: t('agGrid.lastPage'),
  pageSize: t('agGrid.pageSize'),
  pageSizeSelectorLabel: t('agGrid.pageSizeSelectorLabel'),
  
  // Выделение
  selectAll: t('agGrid.selectAll'),
  selectAllSearchResults: t('agGrid.selectAllSearchResults'),
  searchOoo: t('agGrid.searchOoo'),
  noMatches: t('agGrid.noMatches'),
  
  // Прочее
  noRowsToShow: t('agGrid.noRowsToShow'),
  loading: t('agGrid.loading'),
  pinColumn: t('agGrid.pinColumn'),
  autosizeThiscolumn: t('agGrid.autosizeThiscolumn'),
  autosizeAllColumns: t('agGrid.autosizeAllColumns'),
  resetColumns: t('agGrid.resetColumns'),
  copy: t('agGrid.copy'),
  copyWithHeaders: t('agGrid.copyWithHeaders'),
  paste: t('agGrid.paste'),
  export: t('agGrid.export'),
  csvExport: t('agGrid.csvExport'),
  excelExport: t('agGrid.excelExport'),
}))

// --- Функции-обработчики ---

const onGridReady = (params) => {
  gridApi.value = params.api;
};

const getRowId = (params) => params.data.id; 

const onSelectionChanged = (event) => {
  const selectedNodes = event.api.getSelectedNodes();
  isRowSelected.value = selectedNodes.length > 0;

  if (isRowSelected.value) {
    const data = selectedNodes[0].data;
    if (data.pdfUrl && data.pdfUrl.trim().length > 0) {
      selectedPdfUrl.value = data.pdfUrl;
    } else {
      selectedPdfUrl.value = null;
    }
  } else {
    selectedPdfUrl.value = null;
  }
};

const handleAttachPdf = (newUrl) => {
  const selectedNodes = gridApi.value.getSelectedNodes();
  
  if (selectedNodes.length > 0) {
    const selectedNode = selectedNodes[0]; // Берем первый (единственный) выбранный узел
    
    // Создаем НОВЫЙ объект данных на основе существующего, меняем только URL
    const updatedData = { ...selectedNode.data, pdfUrl: newUrl };
    
    // 1. Обновляем данные в реактивном массиве Vue (это для реактивности вне AG Grid)
    // Убедитесь, что rowData — это ref([...])
    const index = rowData.value.findIndex(i => i.id === updatedData.id);
    if (index !== -1) {
      rowData.value.splice(index, 1, updatedData);
    }
    
    // 2. Уведомляем AG Grid об обновлении, передавая НОВЫЙ объект данных.
    // Благодаря функции getRowId (которая использует ID), AG Grid понимает, что это UPDATE, а не ADD.
    gridApi.value.applyTransaction({ update: [updatedData] });

    // Обновляем выбранный URL для кнопки "Просмотр"
    selectedPdfUrl.value = newUrl;
    isEditPdfMode.value = false; // Закрываем модалку в режиме просмотра
  }
};

const openAttachModal = () => {
  isEditPdfMode.value = true;
  isPdfModalOpen.value = true;
};

// Функция добавления нового документа (если используете DocumentAddModal)

const handleAddNewDocument = (newDoc) => {
  const id = rowData.value.length > 0 ? Math.max(...rowData.value.map(d => d.id)) + 1 : 1;
  const docWithId = { ...newDoc, id };
  rowData.value = [...rowData.value, docWithId];
  gridApi.value?.applyTransaction({ add: [docWithId] });
};


const deleteDocument = (id) => {
  // Находим удаляемый объект по ID
  const itemToDelete = rowData.value.find(item => item.id === id);

  if (itemToDelete) {
    // 1. Обновляем реактивный массив Vue
    rowData.value = rowData.value.filter(item => item.id !== id);
    
    // 2. Уведомляем AG Grid об удалении через applyTransaction
    gridApi.value?.applyTransaction({ remove: [itemToDelete] });
  }
};

const onCellDoubleClicked = (params) => {
  // Проверяем, что клик был по колонке "pdfUrl" И что у этой строки есть ссылка
  if (params.colDef.field === 'pdfUrl' && params.value) {
    selectedPdfUrl.value = params.value;
    isEditPdfMode.value = false; // Убеждаемся, что открываем в режиме просмотра, а не редактирования
    isPdfModalOpen.value = true;
  }
};
</script>

<template>
  <div class="manager-dashboard">
    <div class="header">
      <h2>{{ $t('documents.title') }}</h2>
      <div class="header-actions">
        <button class="btn btn-add" @click="isAddModalOpen = true">{{ $t('documents.addDocument') }}</button>
        
        <button class="btn btn-pdf" :class="{ 'btn-pdf-active': selectedPdfUrl }" :disabled="!selectedPdfUrl" @click="isPdfModalOpen = true">
          {{ $t('documents.viewDocument') }}
        </button>
        
        <button class="btn btn-ofer" :class="{ 'btn-pdf-active': isRowSelected }" :disabled="!isRowSelected" @click="openAttachModal">
          {{ $t('documents.attachChange') }}
        </button>
      </div>
    </div>

    <div class="ag-grid-wrapper">
      <ag-grid-vue
        class="ag-theme-alpine"
        :rowData="rowData"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :suppressCellFocus="true"
        :rowHeight="65"
        :stopEditingWhenCellsLoseFocus= "true"
        rowSelection="single"
        @selection-changed="onSelectionChanged"
        @grid-ready="onGridReady"
        @cell-double-clicked="onCellDoubleClicked"
        :getRowId="getRowId"
        style="height: 78vh; width: 100%;"
        :pagination="true"
        :paginationPageSize="15"
        :tooltipShowDelay="100" 
        :paginationPageSizeSelector="[5, 10, 25, 50]"
        :localeText="localeRu"
      />
    </div>

    <PdfModal 
      v-model="isPdfModalOpen" 
      :pdfUrl="selectedPdfUrl"
      :isEditMode="isEditPdfMode"
      @update-pdf="handleAttachPdf"
      @update:modelValue="(val) => { if(!val) isEditPdfMode = false }" 
    />

    <DocumentAddModal v-model="isAddModalOpen" @add="handleAddNewDocument" />
  </div>
</template>


<style scoped>
.manager-dashboard {
  padding: 20px;
}



.header {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Разносит заголовок и группу кнопок по краям */
  padding: 0 40px;                /* Горизонтальные отступы внутри хедера */
  height: 100px;
  border-radius: 30px;
  background-color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 28px;
  color: #1e293b;
}

/* Контейнер для кнопок */
.header-actions {
  display: flex;
  gap: 20px; /* Расстояние между кнопками */
}

/* Закругление краев и мягкая тень для обертки */
.ag-grid-wrapper {
  border-radius: 30px;
  overflow-y: auto;
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); */
  border: 1px solid #acacac;
}


/* Стилизация заголовков: делаем их жирнее и чуть меньше */
.ag-header-cell-label {
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.5px;
}

/* Центрирование данных в ячейках */
:deep(.grid-cell-centered) {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
}

:deep(.ag-right-aligned-cell) {
  text-align: center !important;
  justify-content: center !important;
}

.ag-tooltip-custom {
  /* display: flex; */
  width: 200px;
  height: 300px;
  height: auto;
  margin-bottom: 8px;
  border-radius: 2px;
}

.btn {
  padding: 12px 24px;
  font-size: 15px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

/* Button styles */
.btn-add {
  border: 1px solid #00000079;
  background-color: #5bc06398
}
.btn-add:hover {
  background-color: #5bc063
}

.btn-edit {
  border: 1px solid #00000079;
  background-color: #d86a0388
}
.btn-edit:hover {
  background-color: #d86a03de
}

.btn-ofer {
  border: 1px solid #00000079;
  background-color: #005fcc98
}
.btn-ofer:hover {
  background-color: #0063d4cb
}

.btn-cap {
  display: flex;
  margin-bottom: 20px;
  gap: 70px;
}

.header .btn {
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
}

/* Стили для кнопки "Показать документ" */
.btn-pdf {
  background-color: #94a3b8; /* Серый по умолчанию */
  transition: all 0.3s ease;
  cursor: not-allowed;
  padding: 10px 20px; /* Приводим в соответствие с другими кнопками */
  border-radius: 8px;
  font-weight: 600;
}

.btn-pdf-active {
  background-color: #f1dd01 ; /* Ярко-красный (горит) */
  cursor: pointer;
  border: 1px solid #00000079;

}

.btn-delete-row {
  background-color: #ef4444; /* Красный цвет */
  color: white;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  border: none;
}

.btn-delete-row:hover {
    background-color: #dc2626;
}
</style>