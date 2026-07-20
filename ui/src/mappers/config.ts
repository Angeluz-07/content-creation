// mappers/config.ts
import type { VideoBuildInput, DownloadParams, DiscoveryInput } from '../types/config'

// todo: I could prescind of mappers by defining the API to receive properties as camelCase
// since by now the mapping is redundant
// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface VideoBuildPayload {
  debug_frame: boolean
  hook_text: string
  input_filename: string
  frame_ts: string
  template_name: string
  output_filename: string
}

export const toVideoBuildPayload = (
  data: VideoBuildInput,
): VideoBuildPayload => {
  return {
    debug_frame: data.debugVideoFrame,
    hook_text: data.hookText,
    input_filename: data.inputFileName,
    frame_ts: data.frameTs,
    template_name: data.templateName,
    output_filename: data.outputFileName,
  }
}

export interface DownloadParamsPayload {
  url: string
  force_download: boolean
  start_segment: string
  end_segment: string
  output_filename: string
  file_type: string
}

export interface DiscoveryPayload {
  input_filename: string
  output_filename: string
  sensitivity: number
  url: string
}

export const toDownloadParamsPayload = (data: DownloadParams): DownloadParamsPayload => {
  return {
    url: data.url,
    force_download: data.forceDownload,
    start_segment: data.startSegment,
    end_segment: data.endSegment,
    output_filename: data.outputFileName,
    file_type: data.file_type,
  }
}

export const toDiscoveryPayload = (data: DiscoveryInput): DiscoveryPayload => {
  return {
    input_filename: data.inputFileName,
    output_filename: data.outputFileName,
    sensitivity: data.sensitivity,
    url: data.url,
  }
}
