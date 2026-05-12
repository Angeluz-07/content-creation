<script setup lang="ts">
import { reactive } from 'vue'
import { ref, computed } from 'vue'
import type { DownloadParams } from '../types/config'
import { toDownloadParamsPayload } from '../mappers/config'
import api from '@/api/client'


const form = reactive<DownloadParams>({
  url: 'https://www.youtube.com/watch',
  startSegment: '00:00:10',
  endSegment: '00:00:20',
  fileName: 'test',
  forceDownload: false,
})


const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  try {
    console.log('Datos a enviar:', form)

    const payload = toDownloadParamsPayload(form)
    const { data } = await api.post('/download-segment', payload)
    refreshVideo()
  } catch (error) {
    console.error('Error al enviar:', error)
  } finally {
    isLoading.value = false
  }
}

const isVideoLoaded = ref(true)
const videoUrl = ref('')

const refreshVideo = () => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  const filename = form.fileName
  videoUrl.value = `http://localhost:8000/video/raw/${filename}?t=${timestamp}`
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-4 grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
    
    <div class="card w-full bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title mb-4">Params</h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">URL</span>
            </label>
            <input
              v-model="form.url"
              type="url"
              placeholder="https://ejemplo.com/video"
              class="input input-bordered w-full"
              required
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label">
                <span class="label-text">Start Segment (HH:MM:SS)</span>
              </label>
              <input
                v-model="form.startSegment"
                type="text"
                pattern="^([0-9]{2}:){2}[0-9]{2}$"
                placeholder="00:00:00"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control w-full">
              <label class="label">
                <span class="label-text">End Segment (HH:MM:SS)</span>
              </label>
              <input
                v-model="form.endSegment"
                type="text"
                pattern="^([0-9]{2}:){2}[0-9]{2}$"
                placeholder="00:00:00"
                class="input input-bordered w-full"
              />
            </div>
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Filename</span>
            </label>
            <input
              v-model="form.fileName"
              type="text"
              placeholder="nombre_archivo"
              class="input input-bordered w-full"
              required
            />
          </div>

          <div class="flex flex-col md:flex-row gap-6 pt-4">
            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-3">
                <input v-model="form.forceDownload" type="checkbox" class="toggle toggle-primary" />
                <span class="label-text">Force Download</span>
              </label>
            </div>
          </div>

          <div class="card-actions justify-end mt-6">
            <button
              type="submit"
              :class="{ 'pointer-events-none': isLoading }"
              :tabindex="isLoading ? -1 : 0"
              class="btn btn-primary w-full md:w-auto"
            >
              <span v-if="isLoading" class="loading loading-spinner"></span>
              {{ isLoading ? 'Procesando...' : 'Enviar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    
    <div class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden">
      <div class="card-body p-4">
        <h2 class="card-title">Video</h2>
      </div>
      <figure class="relative aspect-[16/12] w-full md:w-[600px] bg-black">
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
