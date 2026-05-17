<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api/client'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useApi } from '@/composables/useApi'
import { toast } from 'vue-sonner'

const raw_items = ref([])
const items = computed(() => {
  return raw_items.value.map((item) => ({ outputFileName: item }))
})

const { loading: loadingItems, get: getItems } = useApi()

const loadItems = async () => {
  const { data } = await getItems('/video/raws/')
  if (data) {
    raw_items.value = data.values
  }

}

const modalForInputVideo = ref(null) // Referencia al elemento <dialog>
const videoUrl_in = ref('')
const isVideoLoaded_in = ref(false)

const handleModalForInputVideo = (filename) => {
  // 2. Construimos la URL solo cuando se llama la función
  // Agregamos el timestamp para evitar que el navegador use caché vieja
  const timestamp = Date.now()
  videoUrl_in.value = `http://localhost:8000/video/raw/${filename}?t=${timestamp}`
  modalForInputVideo.value.showModal()
}

onMounted(() => {
  loadItems()
})

</script>
<template>
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
</template>
