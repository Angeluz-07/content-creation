// useFileUpload.ts
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

interface SignedUrlData {
  uploadUrl: string
  fileKey: string
}

export const useFileUpload = () => {
  const { post, putExternal, loading, error: apiError } = useApi()
  const uploadProgress = ref(0)
  const error = ref<string | null>(null)

  const uploadFile = async (file: File): Promise<string | null> => {
    error.value = null
    uploadProgress.value = 0

    // 1. POST a tu backend para obtener la Signed URL
    const resSignedUrl = await post('/storage/signed-url', {
      fileName: file.name,
      fileType: file.type,
    })

    if (!resSignedUrl.success) {
      error.value = apiError.value || 'Error al obtener la URL firmada'
      return null
    }

    const { uploadUrl, fileKey } = resSignedUrl.data as SignedUrlData

    // 2. PUT directo a la Signed URL usando el composable corregido
    const resUpload = await putExternal(uploadUrl, file, {
      headers: {
        'x-ms-blob-type': 'BlockBlob', // 👈 OBLIGATORIO para Azure Storage,
        'Content-Type': file.type,
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      },
    })

    if (!resUpload.success) {
      error.value = apiError.value || 'Error al redirigir el archivo al storage'
      return null
    }

    console.log('✅ Subida completada exitosamente:', { fileName: file.name, fileKey })
    return fileKey
  }

  return {
    uploadFile,
    isUploading: loading,
    uploadProgress,
    error,
  }
}
