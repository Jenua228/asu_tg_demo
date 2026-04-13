import { createApp } from 'vue'
import App from './App.vue'
import i18n from './i18n'
import './styles/main.css'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { createPinia } from 'pinia'
import { ToastPlugin } from './composables/useToast'


const app = createApp(App)

app.use(createPinia())
app.use(i18n)
app.use(ToastPlugin)

app.mount('#app')
