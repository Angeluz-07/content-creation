<script setup lang="ts">
import { reactive } from 'vue'
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'

import api from '@/api/client'
import ShortProductionParamsForm from './ShortProductionParamsForm.vue'
import { useVideoStore } from '@/stores/useVideoStore'

const videoStore = useVideoStore()
const { lastProductionTs, latestVideoId } = storeToRefs(videoStore)

const refreshImage = () => {
  const timestamp = Date.now()
  imageUrl.value = `http://localhost:8000/images/?ts=${timestamp}`
}

const refreshVideo = (filename: string) => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  videoUrl.value = `http://localhost:8000/video/${filename}?t=${timestamp}`
}

watch(lastProductionTs, (newTs) => {
  if (newTs) {
    refreshImage()
    refreshVideo(`${latestVideoId.value}_produced`)
  }
})

const imageUrl = ref(`http://localhost:8000/images/`)
const isLoaded = ref(false)
const onImageLoad = () => {
  isLoaded.value = true
}
const imgKey = ref(0)

const isVideoLoaded = ref(true)
const videoUrl = ref('')
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
    <ShortProductionParamsForm></ShortProductionParamsForm>
    <div class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden">
      <div class="card-body p-4">
        <h2 class="card-title">Vista previa</h2>
      </div>
      <figure class="relative aspect-[9/16] w-full md:w-[400px] bg-base-200">
        <div :key="imgKey" v-if="!isLoaded" class="absolute inset-0 skeleton"></div>

        <img
          v-show="isLoaded"
          :src="imageUrl"
          alt="Resultado"
          @load="onImageLoad"
          class="absolute inset-0 w-full h-full object-contain"
        />
      </figure>
    </div>
    <div class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden">
      <div class="card-body p-4">
        <h2 class="card-title">Video</h2>
      </div>
      <figure class="relative aspect-[9/16] w-full md:w-[400px] bg-black">
        <div v-if="!isVideoLoaded" class="absolute inset-0 skeleton"></div>

        <video
          v-if="videoUrl"
          :key="videoUrl"
          controls
          class="absolute inset-0 w-full h-full object-contain"
          @loadeddata="isVideoLoaded = true"
        >
          <source :src="videoUrl" type="video/mp4" />
          Tu navegador no soporta la etiqueta de video.
        </video>
      </figure>
    </div>
  </div>
</template>

<style scoped></style>
