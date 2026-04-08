import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

export function useRouteGuard() {
  const router = useRouter()
  const isAuthenticated = ref(!!localStorage.getItem('token'))

  // Функция для проверки токена
  const checkToken = () => {
    const token = localStorage.getItem('token')
    isAuthenticated.value = !!token
    return !!token
  }

  // Слушаем изменения localStorage
  window.addEventListener('storage', (event) => {
    if (event.key === 'token') {
      checkToken()
    }
  })

  // Создаем навигационный гард
  const createRouteGuard = () => {
    router.beforeEach((to, from, next) => {
      checkToken() // Всегда проверяем актуальность токена

      if (to.meta.requiresAuth && !isAuthenticated.value) {
        next('/login')
      } else if (to.name === 'Login' && isAuthenticated.value) {
        next('/')
      } else {
        next()
      }
    })
  }

  return {
    isAuthenticated,
    checkToken,
    createRouteGuard
  }
}