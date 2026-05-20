<script setup lang="ts">
import DownloadForm from './DownloadForm.vue'
import DownloadTasks from './DownloadTasks.vue';
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid md:grid-cols-5 gap-8 items-start">
    <DownloadForm></DownloadForm>
    <DownloadTasks></DownloadTasks>
  </div>
</template>

<style scoped></style>
