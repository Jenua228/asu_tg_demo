<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { logger, resetPassword } from '../components/auth'

const router = useRouter()
const login = ref('')
const password = ref('')
const isLoading = ref(false)
const showResetForm = ref(false)
const language = ref('ru') // 'ru' или 'en'

const resetData = reactive({
  firstName: '',
  lastName: '',
  email: ''
})

const translations = {
  ru: {
    logo: 'Автоматизированная система управления технической готовности (АСУ ТГ)',
    title: 'Авторизация',
    loginLabel: 'Логин',
    loginPlaceholder: 'Введите логин',
    passwordLabel: 'Пароль',
    passwordPlaceholder: 'Введите пароль',
    loginButton: 'Войти в систему',
    forgotPassword: 'Забыли пароль?',
    hint: 'Для демонстрации используйте:',
    loginHint: 'Логин',
    passwordHint: 'Пароль',
    resetTitle: 'Восстановление пароля',
    firstName: 'Имя',
    firstNamePlaceholder: 'Введите ваше имя',
    lastName: 'Фамилия',
    lastNamePlaceholder: 'Введите вашу фамилию',
    email: 'Email',
    emailPlaceholder: 'Введите ваш email',
    resetButton: 'Восстановить пароль',
    resetHint: 'На указанный email будет отправлена инструкция по восстановлению пароля.',
    back: 'Назад',
    footer: '© 2024 Все права защищены'
  },
  en: {
    logo: 'Automated control system for technical readiness (ACS TR)',
    title: 'Authorization',
    loginLabel: 'Login',
    loginPlaceholder: 'Enter your login',
    passwordLabel: 'Password',
    passwordPlaceholder: 'Enter your password',
    loginButton: 'Sign In',
    forgotPassword: 'Forgot password?',
    hint: 'For demo use:',
    loginHint: 'Login',
    passwordHint: 'Password',
    resetTitle: 'Password Recovery',
    firstName: 'First Name',
    firstNamePlaceholder: 'Enter your first name',
    lastName: 'Last Name',
    lastNamePlaceholder: 'Enter your last name',
    email: 'Email',
    emailPlaceholder: 'Enter your email',
    resetButton: 'Recover Password',
    resetHint: 'Recovery instructions will be sent to the specified email.',
    back: 'Back',
    footer: '© 2024 All rights reserved'
  }
}

const toggleLanguage = () => {
  language.value = language.value === 'ru' ? 'en' : 'ru'
}

const handleLogin = async () => {
  if (!login.value.trim() || !password.value.trim()) {
    alert(language.value === 'ru' 
      ? 'Пожалуйста, заполните все поля' 
      : 'Please fill in all fields')
    return
  }
  
  isLoading.value = true
  const success = logger(login.value, password.value)
  isLoading.value = false
  
  if (success) {
    router.push('/')
  }
}

const handleResetPassword = () => {
  if (!resetData.email.trim()) {
    alert(language.value === 'ru' 
      ? 'Пожалуйста, укажите email' 
      : 'Please provide an email')
    return
  }
  
  const success = resetPassword(resetData.email)
  if (success) {
    alert(language.value === 'ru'
      ? 'Инструкция отправлена на email'
      : 'Instructions have been sent to your email')
    showResetForm.value = false
    resetData.firstName = ''
    resetData.lastName = ''
    resetData.email = ''
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">

      <header class="login-header">
        <img src="/logo_full.png" alt="Flag" class="logo_login" />
        <img src="/Flag.svg" alt="Flag" class="flag" />
        <h1 style=" color: #191970;">{{ translations[language].logo }}</h1>
        <h3>{{ translations[language].title }}</h3>
      </header>
      
      <!-- Форма авторизации -->
      <div v-if="!showResetForm" class="login-form">
        <div class="input-group">
          <label for="login">{{ translations[language].loginLabel }}</label>
          <input 
            id="login"
            v-model="login" 
            type="text" 
            :placeholder="translations[language].loginPlaceholder"
            @keyup.enter="handleLogin"
            class="login-input"
          />
        </div>
        
        <div class="input-group">
          <label for="password">{{ translations[language].passwordLabel }}</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            :placeholder="translations[language].passwordPlaceholder"
            @keyup.enter="handleLogin"
            class="login-input"
          />
        </div>
        
        <button 
          @click="handleLogin" 
          class="login-button"
          :disabled="!login || !password"
        >
          {{ translations[language].loginButton }}
        </button>
        
        <!-- Кнопка "Забыл пароль" -->
        <div class="forgot-password">
          <button 
            @click="showResetForm = true"
            class="forgot-btn"
          >
            {{ translations[language].forgotPassword }}
          </button>
        </div>
        
        <!-- <div class="login-hint">
          <p>{{ translations[language].hint }}</p>
          <p>{{ translations[language].loginHint }}: <strong>admin</strong></p>
          <p>{{ translations[language].passwordHint }}: <strong>admin</strong></p>
        </div> -->
      </div>
      
      <!-- Форма восстановления пароля -->
      <div v-else class="reset-form">
        <div class="form-header">
          <button @click="showResetForm = false" class="back-button">
            ← {{ translations[language].back }}
          </button>
          <h2>{{ translations[language].resetTitle }}</h2>
        </div>
        
        <div class="input-group">
          <label for="firstName">{{ translations[language].firstName }}</label>
          <input 
            id="firstName"
            v-model="resetData.firstName" 
            type="text" 
            :placeholder="translations[language].firstNamePlaceholder"
            class="login-input"
          />
        </div>
        
        <div class="input-group">
          <label for="lastName">{{ translations[language].lastName }}</label>
          <input 
            id="lastName"
            v-model="resetData.lastName" 
            type="text" 
            :placeholder="translations[language].lastNamePlaceholder"
            class="login-input"
          />
        </div>
        
        <div class="input-group">
          <label for="email">{{ translations[language].email }}</label>
          <input 
            id="email"
            v-model="resetData.email" 
            type="email" 
            :placeholder="translations[language].emailPlaceholder"
            class="login-input"
          />
        </div>
        
        <button 
          @click="handleResetPassword" 
          class="login-button reset-button"
          :disabled="!resetData.email"
        >
          {{ translations[language].resetButton }}
        </button>
        
        <div class="reset-hint">
          <p>{{ translations[language].resetHint }}</p>
        </div>
      </div>
            <!-- Кнопка переключения языка -->
            <div class="language-switcher">
        <button 
          @click="toggleLanguage"
          class="lang-btn"
          :class="{ active: language === 'ru' }"
        >
          RU
        </button>
        <button 
          @click="toggleLanguage"
          class="lang-btn"
          :class="{ active: language === 'en' }"
        >
          EN
        </button>
      </div>
      <!-- <div class="login-footer">
        <p>{{ translations[language].footer }}</p>
      </div> -->
    </div>
  </div>
</template>



<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-container {
  position: relative;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  /* height:3000px; */
  /* width: 1020px; */
  max-width: 500px;
  transition: transform 0.3s ease;
}

.login-container:hover {
  transform: translateY(-5px);
}

.language-switcher {
  position: relative;
  /* top: 540px;
  right: 210px; */
  width: 100px;
  display: flex;
  gap: 8px;
  background: #f8fafd;
  border-radius: 10px;
  padding: 5px;
  border: 1px solid #e8ebf0;
}

.lang-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #5d6979;
}

.lang-btn:hover {
  background: #e8ebf0;
  color: #2c3e50;
}

.lang-btn.active {
  background: #4a90e2;
  color: white;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo_login {
  width: 300px;
  height: auto;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.flag {
  width: 120px;
  height: auto;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.login-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.login-form,
.reset-form {
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 25px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  color: #5d6979;
  font-weight: 500;
  font-size: 14px;
}

.login-input {
  width: 420px;
  padding: 15px;
  border: 2px solid #e8ebf0;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f9fafc;
  color: #2c3e50;
}

.login-input:focus {
  outline: none;
  border-color: #4a90e2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.login-button {
  width: 420px;
  padding: 16px;
  background: linear-gradient(135deg, #4a90e2 0%, #357ae8 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
}

.login-button:hover {
  background: linear-gradient(135deg, #357ae8 0%, #2a6cd4 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
}

.login-button:disabled {
  background: #c8d6e5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.forgot-password {
  text-align: center;
  margin: 20px 0;
}

.forgot-btn {
  background: none;
  border: none;
  color: #4a90e2;
  font-size: 14px;
  cursor: pointer;
  padding: 8px;
  transition: color 0.3s ease;
}

.forgot-btn:hover {
  color: #2a6cd4;
  text-decoration: underline;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.back-button {
  background: none;
  border: none;
  color: #4a90e2;
  font-size: 16px;
  cursor: pointer;
  padding: 8px;
  transition: color 0.3s ease;
  white-space: nowrap;
}

.back-button:hover {
  color: #2a6cd4;
}

.form-header h2 {
  color: #2c3e50;
  margin: 0;
  font-size: 24px;
}

.reset-button {
  margin-top: 20px;
}

.login-hint,
.reset-hint {
  margin-top: 30px;
  padding: 20px;
  background: #f8fafd;
  border-radius: 10px;
  border-left: 4px solid #4a90e2;
  color: #5d6979;
  font-size: 14px;
}

.login-hint p,
.reset-hint p {
  margin: 5px 0;
}

.login-hint strong {
  color: #2c3e50;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e8ebf0;
  color: #a8b2c3;
  font-size: 14px;
}

/* Анимации */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-container {
  animation: fadeIn 0.6s ease-out;
}

/* Адаптивность */
@media (max-width: 480px) {
  .login-container {
    padding: 25px;
    margin: 0 15px;
  }
  
  .logo {
    width: 100px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
  
  .language-switcher {
    top: 15px;
    right: 15px;
  }
}
</style>