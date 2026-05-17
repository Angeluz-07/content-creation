<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useApi } from '@/composables/useApi'
import ModalVideoPlayer from './ModalVideoPlayer.vue'

const raw_items = ref([])
const items = computed(() => {
  return raw_items.value.map((item) => ({ outputFileName: item }))
})

const { loading: loadingItems, get: getItems } = useApi()

const loadItems = async () => {
  const { data } = await getItems('/video/raws/')
  if (data) {
    raw_items.value = data.values
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
      <h2 class="card-title">Descargas</h2>
    </div>
    <DataTable :value="items" tableStyle="min-width: 50rem" scrollable scrollHeight="500px">
      <Column field="outputFileName" header="Output File Name"></Column>
      <Column field="" header="Play">
        <template #body="slotProps">
          <ModalVideoPlayer :fileName="slotProps.data.outputFileName"></ModalVideoPlayer>
        </template>
      </Column>
    </DataTable>
  </div>
</template>
