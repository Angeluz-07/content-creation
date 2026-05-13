<script setup lang="ts">
import Navbar from './components/Navbar.vue'
import { RouterView } from 'vue-router'
import { Toaster } from 'vue-sonner'
</script>

<template>
  <Navbar></Navbar>
  <main>
    <Toaster position="bottom-right" :visibleToasts="5" expand richColors theme="light"   />
    <RouterView></RouterView>
  </main>
</template>

<style scoped></style>
