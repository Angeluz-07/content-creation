<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ShortProductionParamsForm from './ShortProductionParamsForm.vue'
import { useVideoStore } from '@/stores/useVideoStore'
import ShortPreviewVideo from './ShortPreviewVideo.vue'
import ShortPreviewImg from './ShortPreviewImg.vue'
import TaskShortProductions from './TaskShortProductions.vue'

const videoStore = useVideoStore()
const { lastProductionTs, latestVideoId } = storeToRefs(videoStore)
const imageId = ref(`images/`)
const videoId = ref('')

const refreshImage = () => {
  const timestamp = Date.now()
  imageId.value = `images/?ts=${timestamp}`
}

// const refreshVideo = (filename: string) => {
//   const timestamp = Date.now()
//   videoId.value = `${filename}/?t=${timestamp}`
// }

watch(lastProductionTs, (newTs) => {
  if (newTs) {
    refreshImage()
    //refreshVideo(latestVideoId.value)
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
    <ShortProductionParamsForm></ShortProductionParamsForm>
    <!-- name of each tab group should be unique -->
    <div class="tabs tabs-box md:col-span-2">
      <label class="tab">
        <input type="radio" name="my_tabs_4" checked="checked" />
        <i class="pi pi-eye me-2"> </i>

        Vista Previa
      </label>
      <div class="tab-content bg-base-100 p-6">
        <ShortPreviewImg :src="imageId"></ShortPreviewImg>
      </div>

      <label class="tab">
        <input type="radio" name="my_tabs_4" />
        <i class="pi pi-video me-2"> </i>
        Productions
      </label>
      <div class="tab-content bg-base-100 p-6">
        <div class="card w-full md:w-fit mx-auto bg-base-100 overflow-hidden p-light col-span-2">
          <TaskShortProductions></TaskShortProductions>
        </div>
      </div>
    </div>
    <!--ShortPreviewVideo :src="videoId"></ShortPreviewVideo-->
  </div>
</template>

<style scoped></style>
