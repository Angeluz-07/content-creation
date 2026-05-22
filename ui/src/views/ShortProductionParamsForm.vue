<script setup lang="ts">
import { useApi } from '@/composables/useApi'
import type { ShortProductionParams } from '../types/config'
import { toShortProductionParamsPayload } from '../mappers/config'
import { reactive, ref, onMounted, computed , watch} from 'vue'
import ModalVideoPlayer from './ModalVideoPlayer.vue'
import { useVideoStore } from '@/stores/useVideoStore'

const WATERMARK_TEXT = import.meta.env.VITE_WATERMARK_TEXT

const form = reactive<ShortProductionParams>({
  inputFileName: '',
  watermarkText: WATERMARK_TEXT,
  debugVideoFrame: true,
  hookText: 'test',
  frameTs: '00:00:03',
  fontName: 'GoogleSans-Medium',
  outputFileName: ''
})

watch(
  () => form.inputFileName,
  (fileName) => {
    form.outputFileName = `${fileName}_produced`;
  }
);
const fontList = ref([
  'GoogleSans-Medium',
  'Anton-Regular',
  'Bangers-Regular',
  'CascadiaCode',
  'LuckiestGuy-Regular',
  'Montserrat-Bold',
  'PassionOne-Regular',
  'ProtestStrike-Regular',
])

const fileNames = ref([])
const { loading: isSubmitting, post: sendForm } = useApi()
const { loading: loadingVideoFileNames, get: getVideoFileNames } = useApi()
const videoStore = useVideoStore()

const handleSubmit = async () => {
  const payload = toShortProductionParamsPayload(form)
  const { success, data } = await sendForm('/produce-short', payload)
  if (success) {
    videoStore.setLastProductionTs(Date.now().toString())
    videoStore.setFinishedVideo(form.outputFileName)
  }
}

async function loadVideoFileNames() {
  const { data } = await getVideoFileNames('/video/raws/')

  if (data && data.values.length > 0) {
    fileNames.value = data.values
    form.inputFileName = data.values[0]
  }
}

onMounted(async () => {
  loadVideoFileNames()
})
</script>

<template>
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
            <ModalVideoPlayer :fileName="form.inputFileName"></ModalVideoPlayer>
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
              <input v-model="form.debugVideoFrame" type="checkbox" class="toggle toggle-primary" />
              <span class="label-text">Debug Video Frame</span>
            </label>
          </div>
        </div>

        <div class="card-actions justify-end mt-6">
          <button
            type="submit"
            :class="{ 'pointer-events-none': isSubmitting }"
            :tabindex="isSubmitting ? -1 : 0"
            class="btn btn-primary w-full md:w-auto"
          >
            <span v-if="isSubmitting" class="loading loading-spinner"></span>
            {{ isSubmitting ? 'Procesando...' : 'Enviar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
