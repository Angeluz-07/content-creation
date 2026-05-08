<script setup lang="ts">
import { reactive } from 'vue'
import { ref, computed } from 'vue'
import type { Config } from '../types/config'
import { mapConfigToPayload } from '../mappers/config'
import api from '@/api/client'

const WATERMARK_TEXT = import.meta.env.VITE_WATERMARK_TEXT

const form = reactive<Config>({
  url: 'https://www.youtube.com/watch',
  watermarkText: WATERMARK_TEXT,
  forceDownload: false,
  debugVideoFrame: true,
  startSegment: '00:00:10',
  endSegment: '00:00:20',
  hookText: 'test',
  outname: 'test4',
  frameTs: '00:00:10',
  fontName: 'CascadiaCode',
})

const fontList = ref([
  'Anton-Regular',
  'Bangers-Regular',
  'BowlbyOne-Regular',
  'CascadiaCode',
  'GoogleSans-Medium',
  'Kanit-Black',
  'LuckiestGuy-Regular',
  'Montserrat-Bold',
  'Oswald-Medium',
  'PassionOne-Regular',
  'Poppins-ExtraBold',
  'ProtestStrike-Regular',
  'RammettoOne-Regular',
  'Rubik-Black',
  'Rubik-Medium',
  'SpaceGrotesk-Regular',
])

const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  try {
    console.log('Datos a enviar:', form)

    const payload = mapConfigToPayload(form)
    const { data } = await api.post('/produce-short', payload)
    refreshImage()
    refreshVideo()
    console.log(data)
  } catch (error) {
    console.error('Error al enviar:', error)
  } finally {
    isLoading.value = false
  }
}

const isLoaded = ref(false)
const isVideoLoaded = ref(true)

// Construimos la URL de la API
const imageUrl = ref(`http://localhost:8000/images/`)

const onImageLoad = () => {
  isLoaded.value = true
}
const imgKey = ref(0)

const refreshImage = () => {
  const timestamp = new Date().getTime()
  imageUrl.value = `http://localhost:8000/images/?ts=${timestamp}`
}
const videoUrl = ref('')

const refreshVideo = () => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  const filename = form.outname
  videoUrl.value = `http://localhost:8000/video/${filename}?t=${timestamp}`
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
              v-model="form.outname"
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
