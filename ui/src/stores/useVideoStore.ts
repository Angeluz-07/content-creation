import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useVideoStore = defineStore('video', () => {
  const latestVideoId = ref('')
  const lastProductionTs = ref('')

  function setFinishedVideo(id: string) {
    latestVideoId.value = id
  }
 function setLastProductionTs(ts: string) {
    lastProductionTs.value = ts
  }
  return { latestVideoId, setFinishedVideo, lastProductionTs, setLastProductionTs }
})
