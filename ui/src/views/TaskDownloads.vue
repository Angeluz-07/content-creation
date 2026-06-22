<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { Tag } from 'primevue'
import { useApi } from '@/composables/useApi'
import ModalVideoPlayer from './ModalVideoPlayer.vue'
import { useDownloadStore } from '@/stores/useDownloadStore'
import { storeToRefs } from 'pinia'
import { usePolling } from '@/composables/usePolling.ts'

const downloadStore = useDownloadStore()
const { lastDownloadTs } = storeToRefs(downloadStore)
const polling = usePolling( 2000)

watch(lastDownloadTs, (newTs) => {
  if (newTs) {
    polling.start(loadItems)
  }
})

const raw_items = ref([])
const items = computed(() => {
  return raw_items.value.map((item) => ({
    outputFileName: item.payload?.output_filename,
    status: item.status,
  }))
})

watch(
  raw_items,
  (newItems) => {
    const hasActiveTasks = newItems.some((i) => ['PENDING', 'PROCESSING'].includes(i.status))
    if (!hasActiveTasks) {
      polling.stop() // Detención explícita basada en tu regla de negocio
    }
  },
  { deep: true },
)

const { loading: loadingItems, get: getItems } = useApi()

const loadItems = async () => {
  const { data } = await getItems('/tasks?target_entity_type=download')
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
onMounted(() => {
  polling.start(loadItems)
})
</script>
<template>
  <div
    class="card w-full md:w-fit mx-auto bg-base-100 shadow-xl overflow-hidden p-light col-span-2"
  >
    <DataTable
      :value="items"
      :loading="loadingItems"
      tableStyle="min-width: 50rem"
      scrollable
      scrollHeight="500px"
    >
      <template #header>
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xl font-bold">Descargas</span>
          <!--Button
            @click="loadItems()"
            icon="pi pi-sync"
            rounded
            raised
            outlined
            severity="secondary"
          /-->
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
            <ModalVideoPlayer
              url="/video/raw"
              :fileName="slotProps.data.outputFileName"
            ></ModalVideoPlayer>
          </template>
        </template>
      </Column>
    </DataTable>
  </div>
</template>
