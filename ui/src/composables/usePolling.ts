import { ref, onUnmounted } from 'vue'

export function usePolling(intervalMs = 2000) {
  const isActive = ref(false)
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let currentFn: (() => Promise<void>) | null = null

  // El motor es una función común y corriente
  const loop = async () => {
    // Si en medio del camino se apagó el interruptor, frenamos en seco
    if (!isActive.value || !currentFn) return

    await currentFn()

    // Si después de la petición HTTP sigue activo, agendamos el siguiente pulso
    if (isActive.value) {
      timeoutId = setTimeout(loop, intervalMs)
    }
  }

  const start = (fn: () => Promise<void>) => {
    if (isActive.value) return // Evitamos duplicar hilos
    isActive.value = true
    currentFn = fn
    loop() // Arranca la cadena
  }

  const stop = () => {
    isActive.value = false
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  // El seguro de vida es explícito, tú ves cuándo se registra
  onUnmounted(() => {
    stop()
  })

  return {
    isActive,
    start,
    stop
  }
}