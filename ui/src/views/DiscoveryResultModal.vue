<script setup lang="ts">
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { Tag } from 'primevue'

const props = defineProps({
  fileName: {
    type: String,
    required: true,
  },
  url: {
    type: String,
    required: true,
  },
})

// SOLUCIÓN 1: El nombre de la variable debe coincidir EXACTAMENTE con ref="modalForInputVideo" del template
const modalForInputVideo = ref<HTMLDialogElement | null>(null) 
const videoUrl_in = ref('')

const handleModal = async () => {
  // SOLUCIÓN 2: Esperamos a que los elementos carguen antes de abrir visualmente el modal
  await loadItems()
  if (modalForInputVideo.value) {
    modalForInputVideo.value.showModal()
  }
}

const raw_items = ref<any[]>([])
const items = computed(() => {
  // SOLUCIÓN 3: Añadimos encadenamiento opcional (?.) para evitar que falle si la estructura viene vacía
  return raw_items.value?.map((item: any) => ({
    start: item?.start || '',
    end: item?.end || '',    
    text: item?.full_context || '',
  })) || []
})

const { loading: loadingItems, get: getItems } = useApi()

const loadItems = async () => {
  try {
    const response = await getItems(`${props.url}/${props.fileName}`)
    
    // SOLUCIÓN 4: Desestructuramos la respuesta de forma segura. 
    // Dependiendo de tu useApi, la respuesta puede estar en response.data o directo en response.
    const responseData = response?.data || response

    if (responseData && responseData.values) {
      // Mapeamos los "values" que vienen directamente del JSON de tu FastAPI
      raw_items.value = responseData.values
    } else if (Array.isArray(responseData)) {
      raw_items.value = responseData
    }
  } catch (error) {
    console.error("Error cargando los resultados de la API:", error)
    raw_items.value = []
  }
}
</script>

<template>
  <button
    type="button"
    @click="handleModal"
    class="btn btn-square btn-primary col-span-1"
  >
    <!-- SOLUCIÓN 5: Corregido el namespace inválido del SVG (xmlns) -->
    <svg xmlns="http://w3.org" fill="currentColor" viewBox="0 0 24 24" class="w-6 h-6">
      <path d="M8 5v14l11-7z" />
    </svg>
  </button>

  <dialog id="inputFilePlayer" class="modal" ref="modalForInputVideo" @close="videoUrl_in = ''">
    <div class="modal-box w-11/12 max-w-full md:max-w-5xl p-0">
      <div class="card w-full bg-base-100 shadow-xl overflow-hidden">
        <!-- SOLUCIÓN 6: Limpieza de clases repetidas y contenedores innecesarios para que la tabla use todo el ancho -->
        <div class="w-full mx-auto p-6">
          <DataTable
            :value="items"
            :loading="loadingItems"
            tableStyle="min-width: 100%"
            scrollable
            scrollHeight="500px"
          >
            <template #header>
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="text-xl font-bold">Discover Tasks</span>
              </div>
            </template>
            <!-- Vinculamos las columnas mapeadas en el computed con la propiedad 'field' -->
            <Column field="start" header="Start"></Column>
            <Column field="end" header="End"></Column>
            <Column field="text" header="Text"></Column>
          </DataTable>
        </div>
      </div>
      <div class="modal-action p-4">
        <form method="dialog">
          <button class="btn">Close [Esc]</button>
        </form>
      </div>
    </div>
  </dialog>
</template>