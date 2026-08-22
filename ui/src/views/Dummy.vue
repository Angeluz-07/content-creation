<script setup lang="ts">
import FileUpload from 'primevue/fileupload'
import { useFileUpload } from '@/composables/useFileUpload'
const { uploadFile, isUploading, uploadProgress, error } = useFileUpload()

const onFileSelect = async (event: any) => {
  // PrimeVue entrega los archivos en event.files
  const file = event.files?.[0]
  if (!file) return

  const fileKey = await uploadFile(file)

  if (fileKey) {
    // Archivo cargado con éxito en la nube
    // Aquí puedes emitir un evento o actualizar la lista local de archivos
  }
}
</script>

<template>
  <div class="w-full max-w-md p-6 bg-white rounded-lg border border-gray-200 shadow-sm space-y-4">
    <h3 class="text-lg font-semibold text-gray-800">Cargar Archivo</h3>

    <!-- Componente de PrimeVue configurado para disparo automático -->
    <FileUpload
      mode="basic"
      customUpload
      @uploader="onFileSelect"
      :auto="true"
      :disabled="isUploading"
      chooseLabel="Seleccionar Archivo"
      class="w-full"
    />

    <!-- Barra de progreso visual durante el PUT al Storage -->
    <div v-if="isUploading" class="space-y-1">
      <div class="flex justify-between text-xs font-medium text-gray-600">
        <span>Subiendo a la nube...</span>
        <span>{{ uploadProgress }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-emerald-500 h-2 rounded-full transition-all duration-200"
          :style="{ width: `${uploadProgress}%` }"
        ></div>
      </div>
    </div>

    <!-- Mensaje de error -->
    <p v-if="error" class="text-sm text-red-600 font-medium">
      {{ error }}
    </p>
  </div>
</template>
