<script setup lang="ts">
import { reactive } from 'vue'
import { ref, onMounted, computed } from 'vue'
import type { ShortProductionParams } from '../types/config'
import { toShortProductionParamsPayload } from '../mappers/config'
import api from '@/api/client'

const WATERMARK_TEXT = import.meta.env.VITE_WATERMARK_TEXT

const form = reactive<ShortProductionParams>({
  inputFileName: '',
  watermarkText: WATERMARK_TEXT,
  debugVideoFrame: true,
  hookText: 'test',
  frameTs: '00:00:10',
  fontName: 'GoogleSans-Medium',
})

const fileNames = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/video/raws/')
    fileNames.value = data.values

    // // Optional: Pre-select the first item if the list isn't empty
    if (fileNames.value.length > 0) {
      form.inputFileName = fileNames.value[0]
    }
  } catch (error) {
    console.error('Failed to load options:', error)
  }
})
const fontList = ref([
  'GoogleSans-Medium',
  'Anton-Regular',
  'Bangers-Regular',
  'CascadiaCode',
  'LuckiestGuy-Regular',
  'Montserrat-Bold',
  'PassionOne-Regular',
  'ProtestStrike-Regular',
  'RammettoOne-Regular',
  'SpaceGrotesk-Regular',
])

const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  try {
    console.log('Datos a enviar:', form)

    const payload = toShortProductionParamsPayload(form)
    const { data } = await api.post('/produce-short', payload)
    refreshImage()
    refreshVideo()
    // console.log(data)
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
  const filename = form.inputFileName
  videoUrl.value = `http://localhost:8000/video/${filename}_produced?t=${timestamp}`
}

const isVideoLoaded_in = ref(false)
const videoUrl_in = ref('')
const modalForInputVideo = ref(null) // Referencia al elemento <dialog>
const handleModalForInputVideo = () => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  const filename = form.inputFileName
  videoUrl_in.value = `http://localhost:8000/video/raw/${filename}?t=${timestamp}`
  modalForInputVideo.value.showModal()
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
    <div class="card w-full bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title mb-4">Params</h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Input Filename</span>
            </label>
            <div class="grid grid-cols-6 gap-4">
              <select
                v-model="form.inputFileName"
                class="select select-bordered w-full col-span-5"
                required
              >
                <option value="" disabled selected>Select a file</option>
                <!-- Loop through the list of strings -->
                <option v-for="fileName in fileNames" :key="fileName" :value="fileName">
                  {{ fileName }}
                </option>
              </select>
              <button
                type="button"
                @click="handleModalForInputVideo"
                class="btn btn-square btn-primary col-span-1"
              >
                <!-- Icono de Play (SVG) -->
                <svg xmlns="http://w3.org" fill="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </button>
              <dialog id="inputFilePlayer" class="modal" ref="modalForInputVideo" @close="videoUrl_in = ''">
                <div class="modal-box w-11/12 max-w-full md:max-w-5xl p-0">
                  <div class="card w-full bg-base-100 shadow-xl overflow-hidden">
                    <div class="card-body p-4">
                      <h2 class="card-title">Video</h2>
                    </div>
                    <!-- 2. Kept aspect ratio, removed fixed 600px, let flex/grid handle sizing -->

                    <figure class="relative aspect-video w-full bg-black">
                      <!-- Skeleton loader -->
                      <div v-if="!isVideoLoaded_in" class="absolute inset-0 skeleton"></div>

                      <video
                        v-if="videoUrl_in"
                        :key="videoUrl_in"
                        :src="videoUrl_in"
                        controls
                        class="absolute inset-0 w-full h-full object-contain"
                        @loadeddata="isVideoLoaded_in = true"
                      >
                        Tu navegador no soporta la etiqueta de video.
                      </video>
                    </figure>
                  </div>
                  <div class="modal-action p-4">
                    <form method="dialog">
                      <button class="btn">Close [Esc]</button>
                    </form>
                  </div>
                </div>
              </dialog>
            </div>
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Font</span>
            </label>
            <!-- Use v-model for binding and select tag instead of input -->
            <select v-model="form.fontName" class="select select-bordered w-full" required>
              <option value="" disabled selected>Select a font</option>
              <!-- Loop through the list of strings -->
              <option v-for="fontName in fontList" :key="fontName" :value="fontName">
                {{ fontName }}
              </option>
            </select>
          </div>

          <div class="form-control w-full">
            <label class="label">
              <span class="label-text font-semibold">Watermark text</span>
            </label>
            <input
              v-model="form.watermarkText"
              type="text"
              placeholder="@theExample"
              class="input input-bordered w-full"
              required
            />
          </div>
          <div class="form-control w-full">
            <label class="label">
              <span class="label-text">Hook Text</span>
            </label>
            <input
              v-model="form.hookText"
              type="text"
              placeholder="Escribe el hook aquí"
              class="input input-bordered w-full"
            />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label">
                <span class="label-text">Frame to use (HH:MM:SS)</span>
              </label>
              <input
                v-model="form.frameTs"
                type="text"
                pattern="^([0-9]{2}:){2}[0-9]{2}$"
                placeholder="00:00:00"
                class="input input-bordered w-full"
              />
            </div>
          </div>

          <div class="flex flex-col md:flex-row gap-6 pt-4">
            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-3">
                <input
                  v-model="form.debugVideoFrame"
                  type="checkbox"
                  class="toggle toggle-primary"
                />
                <span class="label-text">Debug Video Frame</span>
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
