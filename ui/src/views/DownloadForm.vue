<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { DownloadParams } from '@/types/config'
import { toDownloadParamsPayload } from '@/mappers/config'
import { toast } from 'vue-sonner'
import { useApi } from '@/composables/useApi'

const form = reactive<DownloadParams>({
  url: 'https://www.youtube.com/watch',
  startSegment: '00:00:10',
  endSegment: '00:00:20',
  outputFileName: 'test',
  forceDownload: false,
})

const { loading: loadingParams, get: getParams } = useApi()
const { loading: isSubmitting, error: submitError, post: sendForm } = useApi()

async function loadLastParams() {
  const { data } = await getParams('/download-params/last')

  if (data) {
    const params = data.value
    form.url = params.url
    form.startSegment = params.start_segment
    form.endSegment = params.end_segment
  }
}

const handleSubmit = async () => {
  const payload = toDownloadParamsPayload(form)
  const { success } = await sendForm('/download-segment', payload)

  // Disparar efectos colaterales de UI basados en el éxito de la acción
  if (success) {
    toast.success('Descarga iniciada', {
      description: 'Se ha enviado a descargar el archivo',
    })
  }
}

onMounted(() => {
  loadLastParams()
})
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
          <label class="label"><span class="label-text font-semibold">URL</span></label>
          <input v-model="form.url" type="url" class="input input-bordered w-full" required />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control w-full">
            <label class="label"><span class="label-text">Start Segment (HH:MM:SS)</span></label>
            <input
              v-model="form.startSegment"
              type="text"
              pattern="^([0-9]{2}:){2}[0-9]{2}$"
              placeholder="00:00:00"
              class="input input-bordered w-full"
            />
          </div>
          <div class="form-control w-full">
            <label class="label"><span class="label-text">End Segment (HH:MM:SS)</span></label>
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
          <label class="label"><span class="label-text">Output Filename</span></label>
          <input
            v-model="form.outputFileName"
            type="text"
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
          <button type="submit" :disabled="isSubmitting" class="btn btn-primary w-full md:w-auto">
            <span v-if="isSubmitting" class="loading loading-spinner"></span>
            {{ isSubmitting ? 'Procesando...' : 'Enviar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
