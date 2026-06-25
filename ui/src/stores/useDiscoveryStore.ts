import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useDiscoveryStore = defineStore('discovery', () => {
  const lastTs = ref('')

  function setLastDiscoveryTs(ts: string) {
    lastTs.value = ts
  }

  function taskSent() {
    setLastDiscoveryTs(Date.now().toString())
  }
  return { lastTs, setLastDiscoveryTs , taskSent}
})
