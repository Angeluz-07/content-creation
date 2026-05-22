<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ShortProductionParamsForm from './ShortProductionParamsForm.vue'
import { useVideoStore } from '@/stores/useVideoStore'
import ShortPreviewVideo from './ShortPreviewVideo.vue'
import ShortPreviewImg from './ShortPreviewImg.vue'

const videoStore = useVideoStore()
const { lastProductionTs, latestVideoId } = storeToRefs(videoStore)
const imageId = ref(`images/`)
const videoId = ref('')

const refreshImage = () => {
  const timestamp = Date.now()
  imageId.value = `images/?ts=${timestamp}`
}

const refreshVideo = (filename: string) => {
  const timestamp = Date.now()
  videoId.value = `${filename}/?t=${timestamp}`
}

watch(lastProductionTs, (newTs) => {
  if (newTs) {
    refreshImage()
    refreshVideo(latestVideoId.value)
  }
})

</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
    <ShortProductionParamsForm></ShortProductionParamsForm>
    <ShortPreviewImg :src="imageId"></ShortPreviewImg>
    <!--ShortPreviewVideo :src="videoId"></ShortPreviewVideo-->
  </div>
</template>

<style scoped></style>
