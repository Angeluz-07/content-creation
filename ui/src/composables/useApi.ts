import { ref } from 'vue'
import api from '@/api/client'

export const useApi = () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  // El wrapper ahora devuelve un contrato claro: { success: boolean, data: any }
  async function request(axiosPromise: Promise<any>) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axiosPromise;
      // Retorno explícito de éxito
      return { success: true, data: response.data };
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Error';
      // Retorno explícito de fallo
      return { success: false, data: null };
    } finally {
      loading.value = false;
    }
  }

  const get = (url: string) => request(api.get(url));
  const post = (url: string, data: any) => request(api.post(url, data));

  return { loading, error, get, post };
}