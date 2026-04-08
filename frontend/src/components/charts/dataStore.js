import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import jsonD from './db.json' assert { type:'json'}

export const useDataStore = defineStore('data', () => {
  const jsonData = reactive(jsonD)
  const isLoading = ref(false)
  const error = ref(null)
  const count = ref(0)

  function increment() {
    count.value++
  }

  async function loadData() {
    try {
      isLoading.value = true
      const responce = await fetch('./db.json')
      if (!responce.ok) throw new Error('Oshibka zagruzki')
      const jsonD = await responce.json()
      jsonData.value = jsonD['db']
    }
    catch (err) {
      error.value = err.message
    }
    finally {
      isLoading.value = false
    }
  }
  loadData()

  return {
    jsonData,
    isLoading,
    error,
    loadData,
    count, 
    increment
  }
})
