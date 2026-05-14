<script setup lang="ts">
import { reactive } from 'vue'
import { ref, computed, onMounted } from 'vue'
import type { DownloadParams } from '../types/config'
import { toDownloadParamsPayload } from '../mappers/config'
import api from '@/api/client'
import { toast } from 'vue-sonner'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const raw_items = ref([])
const items = computed(() => {
  return raw_items.value.map((item) => ({ outputFileName: item }))
})

const testToast = () => {
  toast.success('Descarga iniciada', {
    description: 'Se ha enviado a descargar el archivo',
  })
}

const form = reactive<DownloadParams>({
  url: 'https://www.youtube.com/watch',
  startSegment: '00:00:10',
  endSegment: '00:00:20',
  outputFileName: 'test',
  forceDownload: false,
})

const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  try {
    console.log('Datos a enviar:', form)

    const payload = toDownloadParamsPayload(form)
    const { data } = await api.post('/download-segment', payload)
    testToast()
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
  const filename = form.outputFileName
  videoUrl.value = `http://localhost:8000/video/raw/${filename}?t=${timestamp}`
}

const getItems = async () => {
  try {
    const { data } = await api.get('/video/raws/')
    raw_items.value = data.values
  } catch (error) {
    console.error('Failed to load options:', error)
  }
}
onMounted(async () => {
  try {
    const { data } = await api.get('/download-params/last')
    if (data.value) {
      const params = data.value
      form.url = params.url
      form.startSegment = params.start_segment
      form.endSegment = params.end_segment
    }
  } catch (error) {
    console.error('Failed to load options:', error)
  }
  getItems()
})

const isVideoLoaded_in = ref(false)
const videoUrl_in = ref('')
const modalForInputVideo = ref(null) // Referencia al elemento <dialog>
const handleModalForInputVideo = (filename) => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  videoUrl_in.value = `http://localhost:8000/video/raw/${filename}?t=${timestamp}`
  modalForInputVideo.value.showModal()
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid md:grid-cols-5 gap-8 items-start">
    <div class="card w-full bg-base-100 shadow-xl col-span-2">
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
              <span class="label-text">Output Filename</span>
            </label>
            <input
              v-model="form.outputFileName"
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

    <div
      class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden p-light col-span-2"
    >
      <div class="card-body p-4">
        <h2 class="card-title">Descargas</h2>
      </div>
      <DataTable :value="items" tableStyle="min-width: 50rem" scrollable scrollHeight="500px">
        <Column field="outputFileName" header="Output File Name"></Column>
        <Column field="" header="Play">
          <template #body="slotProps">
            <button
              type="button"
              @click="handleModalForInputVideo(slotProps.data.outputFileName)"
              class="btn btn-square btn-primary col-span-1"
            >
              <!-- Icono de Play (SVG) -->
              <svg xmlns="http://w3.org" fill="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
            <dialog
              id="inputFilePlayer"
              class="modal"
              ref="modalForInputVideo"
              @close="videoUrl_in = ''"
            >
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
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<style scoped></style>
