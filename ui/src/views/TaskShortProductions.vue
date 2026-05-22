<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { Button } from 'primevue'
import { Tag } from 'primevue'
import { useApi } from '@/composables/useApi'
import ModalVideoPlayer from './ModalVideoPlayer.vue'
import { useDownloadStore } from '@/stores/useDownloadStore'
import { storeToRefs } from 'pinia'
import { useTaskStream } from '@/composables/useTaskStream'

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
    outputFileName: item.payload?.output_filename,
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

const statusSeverityMap = {
  PENDING: 'secondary',
  PROCESSING: 'info',
  COMPLETED: 'success',
  FAILED: 'warn',
}
const { connect, disconnect } = useTaskStream()

onMounted(() => {
  loadItems()
  connect('tasks/stream', loadItems)
})
onUnmounted(() => {
  disconnect()
})
</script>
<template>
  <DataTable
    :value="items"
    :loading="loadingItems"
    tableStyle="min-width: 45rem"
    scrollable
    scrollHeight="500px"
  >
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xl font-bold">Productions</span>
        <Button
          @click="loadItems()"
          icon="pi pi-sync"
          rounded
          raised
          outlined
          severity="secondary"
        />
      </div>
    </template>
    <Column field="outputFileName" header="Output Filename"></Column>
    <Column field="status" header="Status">
      <template #body="slotProps">
        <Tag
          :value="slotProps.data.status"
          :severity="statusSeverityMap[slotProps.data.status] || null"
        />
      </template>
    </Column>
    <Column field="" header="Play">
      <template #body="slotProps">
        <template v-if="slotProps.data.status == 'COMPLETED'">
          <ModalVideoPlayer :fileName="slotProps.data.outputFileName"></ModalVideoPlayer>
        </template>
      </template>
    </Column>
  </DataTable>
</template>
