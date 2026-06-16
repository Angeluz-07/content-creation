<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import api from '@/api/client'

const props = defineProps({
  src: { type: String, required: true },
})

const isVideoLoaded = ref(false)
const fullSrc = computed(() => `${api.defaults.baseURL}/video/${props.src}`)

// Cuando la prop cambie, reiniciamos el estado de carga inmediatamente
watch(() => props.src, () => {
  isVideoLoaded.value = false
})
</script>

<template>
  <div class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden">
    <div class="card-body p-4">
      <h2 class="card-title">Video</h2>
    </div>
    
    <figure class="relative aspect-[9/16] w-full md:w-[400px] bg-black">
      <!-- Skeleton Loader -->
      <div v-if="!isVideoLoaded" class="absolute inset-0 skeleton"></div>

      <!-- 
        Al usar :key="fullSrc", Vue recrea el elemento <video> automáticamente
        cuando la URL cambia, forzando al navegador a cargar el nuevo recurso.
      -->
      <video
        v-show="isVideoLoaded"
        :key="fullSrc"
        :src="fullSrc"
        controls
        class="absolute inset-0 w-full h-full object-contain"
        @loadeddata="isVideoLoaded = true"
      >
        Tu navegador no soporta la etiqueta de video.
      </video>
    </figure>
  </div>
</template>