<script setup lang="ts">
import DownloadForm from './DownloadForm.vue'
import DownloadList from './DownloadList.vue'
import TaskList from './TaskList.vue';
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 grid md:grid-cols-5 gap-8 items-start">
    <DownloadForm></DownloadForm>
    <DownloadList></DownloadList>
    <TaskList></TaskList>
  </div>
</template>

<style scoped></style>
