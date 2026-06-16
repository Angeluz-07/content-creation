import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useDownloadStore = defineStore('download', () => {
  const lastDownloadTs = ref('')

  function setLastDownloadTs(ts: string) {
    lastDownloadTs.value = ts
  }

  function taskDownloadSent() {
    setLastDownloadTs(Date.now().toString())
  }
  return { lastDownloadTs, setLastDownloadTs , taskDownloadSent}
})
