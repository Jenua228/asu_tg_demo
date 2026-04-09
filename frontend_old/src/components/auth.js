import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

// Создаем реактивную переменную токена
const token = ref(localStorage.getItem('token') || false)
const router = useRouter()

// Слушаем изменения localStorage для токена
window.addEventListener('storage', (event) => {
    if (event.key === 'token') {
        token.value = event.newValue ? true : false
    }
})

function logger(login, password) {
    if (login === 'admin' && password === 'admin') {
        const tokenValue = Date.now().toString() // Генерируем уникальный токен
        localStorage.setItem('token', tokenValue)
        token.value = true
        return true
    } else {
        alert('Неверные учетные данные')
        return false
    }
}

function resetPassword(email) {
    // В реальном приложении здесь был бы запрос к API
    console.log('Запрос на сброс пароля для:', email)
    return true
}

function logout() {
    localStorage.removeItem('token')
    token.value = false
    if (router) {
        router.push('/login')
    }
}

// Синхронизация токена между вкладками
watch(token, (newValue) => {
    if (!newValue) {
        localStorage.removeItem('token')
        if (router) {
            router.push('/login')
        }
    }
})

export { token, logger, logout, resetPassword }