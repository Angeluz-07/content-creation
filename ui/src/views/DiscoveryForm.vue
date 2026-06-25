<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import type { DiscoveryInput } from '@/types/config'
import { toDiscoveryPayload } from '@/mappers/config'
import { toast } from 'vue-sonner'
import { useApi } from '@/composables/useApi'
import { useDiscoveryStore } from '@/stores/useDiscoveryStore'

const discoveryStore = useDiscoveryStore()

const form = reactive<DiscoveryInput>({
  inputFileName: '',
  outputFileName: 'test',
  sensitivity: 0.75,
  min_words: 90,
  url: 'https://www.youtube.com/watch',
})

watch(
  () => form.inputFileName,
  (fileName) => {
    form.outputFileName = `${getFilenameStem(fileName)}_candidates`
  },
)

const getFilenameStem = (filename) => {
    const lastDotIndex = filename.lastIndexOf('.');
    
    // Return the stem if a dot exists, otherwise return the whole filename
    return lastDotIndex !== -1 ? filename.slice(0, lastDotIndex) : filename;
}
const fileNames = ref([])
const { loading: loadingFileNames, get: getFileNames } = useApi()

async function loadFileNames() {
  const { data } = await getFileNames('/assets/vtt/')

  if (data && data.values.length > 0) {
    fileNames.value = data.values
    form.inputFileName = data.values[0]
  }
}

onMounted(async () => {
  loadFileNames()
})
const { loading: loadingParams, get: getParams } = useApi()
const { loading: isSubmitting, error: submitError, post: sendForm } = useApi()

const handleSubmit = async () => {
  const payload = toDiscoveryPayload(form)
  const { success } = await sendForm('/discovery', payload)

  // Disparar efectos colaterales de UI basados en el éxito de la acción
  if (success) {
    toast.success('Descarga iniciada', {
      description: 'Se ha enviado a descargar el archivo',
    })
    discoveryStore.taskSent()
  }
}
</script>

<template>
  <div class="card w-full bg-base-100 shadow-xl col-span-2">
    <div class="card-body">
      <h2 class="card-title mb-4">Params</h2>

      <!-- MENSAJE DE ERROR DECLARATIVO -->
      <!-- Si el composable atrapa un error, la UI reacciona sola. No manejas esto en JS -->
      <div v-if="submitError" class="alert alert-error shadow-sm text-sm mb-4">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="stroke-current shrink-0 h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span>{{ submitError }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- ... Campos del formulario permanecen igual con v-model ... -->
          <div class="form-control w-full">
          <label class="label">
            <span class="label-text font-semibold">Input Filename</span>
          </label>
          <!-- Use v-model for binding and select tag instead of input -->
          <select v-model="form.inputFileName" class="select select-bordered w-full" required>
            <option value="" disabled selected>Select a file</option>
            <!-- Loop through the list of strings -->
            <option v-for="item in fileNames" :key="item" :value="item">
              {{ item }}
            </option>
          </select>
        </div>
        <div class="form-control w-full">
          <label class="label"><span class="label-text">Output Filename</span></label>
          <input
            v-model="form.outputFileName"
            type="text"
            class="input input-bordered w-full"
            required
          />
        </div>
           <div class="form-control w-full">
          <label class="label"><span class="label-text">Sensitivity</span></label>
          <input
            v-model="form.sensitivity"
            type="text"
            class="input input-bordered w-full"
            required
          />
        </div>
           <div class="form-control w-full">
          <label class="label"><span class="label-text">Min Words</span></label>
          <input
            v-model="form.min_words"
            type="text"
            class="input input-bordered w-full"
            required
          />
        </div>
           <div class="form-control w-full">
          <label class="label"><span class="label-text">URL</span></label>
          <input
            v-model="form.url"
            type="text"
            class="input input-bordered w-full"
            required
          />
        </div>


       
        <div class="card-actions justify-end mt-6">
          <button type="submit" :disabled="isSubmitting" class="btn btn-primary w-full md:w-auto">
            <span v-if="isSubmitting" class="loading loading-spinner"></span>
            {{ isSubmitting ? 'Procesando...' : 'Enviar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
