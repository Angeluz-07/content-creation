<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import api from '@/api/client'

const props = defineProps({
  src: { type: String, required: true },
  alt: { type: String, default: '' }
})

const isLoaded = ref(false)
const fullSrc = computed(() => `${api.defaults.baseURL}${props.src}`)

watch(() => props.src, () => {
  isLoaded.value = false
})

</script>
<template>
    <div class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden">
      <div class="card-body p-4">
        <h2 class="card-title">Vista previa</h2>
      </div>
      <figure class="relative aspect-[9/16] w-full md:w-[400px] bg-base-200">
        <div v-if="!isLoaded" class="absolute inset-0 skeleton"></div>

        <img
          v-show="isLoaded"
          :src="fullSrc"
          alt="Resultado"
          @load="isLoaded = true"
          class="absolute inset-0 w-full h-full object-contain"
        />
      </figure>
    </div>
</template>