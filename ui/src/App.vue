<script setup lang="ts">
import Navbar from './components/Navbar.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <Navbar></Navbar>
  <main>
    <RouterView></RouterView>
  </main>
</template>

<style scoped></style>
