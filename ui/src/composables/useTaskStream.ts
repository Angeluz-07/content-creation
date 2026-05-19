import { ref } from 'vue'

import api from '@/api/client'


export function useTaskStream() {
  const eventSource = ref<EventSource | null>(null)
  const isConnected = ref(false)

  const connect = (url: string, onUpdateCallback: () => void) => {
    // Evitamos duplicar conexiones si ya existe una activa
    if (eventSource.value) return

    eventSource.value = new EventSource(`${api.defaults.baseURL}${url}`)
    isConnected.value = true

    eventSource.value.addEventListener('update', () => {
      console.log('¡Cambio detectado en el backend via SSE!')
      onUpdateCallback()
    })

    eventSource.value.onerror = (error) => {
      console.error('Error en el stream de SSE:', error)
    }
  }

  const disconnect = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      isConnected.value = false
      console.log('Conexión SSE cerrada explícitamente.')
    }
  }

  // Estructura tradicional: retornamos estados y funciones de control
  return {
    isConnected,
    connect,
    disconnect,
  }
}
