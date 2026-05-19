<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useApi } from '@/composables/useApi'
import ModalVideoPlayer from './ModalVideoPlayer.vue'
import { useDownloadStore } from '@/stores/useDownloadStore'
import { storeToRefs } from 'pinia'

const downloadStore = useDownloadStore()
const { lastDownloadTs } = storeToRefs(downloadStore)

watch(lastDownloadTs, (newTs) => {
  if (newTs) {
    loadItems()
  }
})
const raw_items = ref([])
const items = computed(() => {
  return raw_items.value.map((item) => ({
    outputFileName: item.target?.output_filename,
    status: item.status,
  }))
})

const { loading: loadingItems, get: getItems } = useApi()

const loadItems = async () => {
  const { data } = await getItems('/tasks/agg')
  if (data) {
    console.log(data)
    raw_items.value = data.value
  }
}

onMounted(() => {
  loadItems()
})
</script>
<template>
  <div
    class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden p-light col-span-2"
  >
    <div class="card-body p-4">
      <h2 class="card-title">Tareas</h2>
    </div>
    <DataTable :value="items" tableStyle="min-width: 50rem" scrollable scrollHeight="500px">
      <Column field="outputFileName" header="Output Filename"></Column>
      <Column field="status" header="Status"></Column>
    </DataTable>
  </div>
</template>
