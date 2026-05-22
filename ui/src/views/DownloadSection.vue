<script setup lang="ts">
import DownloadForm from './DownloadForm.vue'
import TaskDownloads from './TaskDownloads.vue';
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid md:grid-cols-5 gap-8 items-start">
    <DownloadForm></DownloadForm>
    <TaskDownloads></TaskDownloads>
  </div>
</template>

<style scoped></style>
