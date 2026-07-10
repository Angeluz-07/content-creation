// mappers/config.ts
import type { ShortProductionParams, DownloadParams, DiscoveryInput } from '../types/config'

// todo: I could prescind of mappers by defining the API to receive properties as camelCase
// since by now the mapping is redundant
// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface ShortProductionParamsPayload {
  debug_frame: boolean
  hook_text: string
  input_filename: string
  watermark_text: string
  frame_ts: string
  font_name: string
  output_filename: string
  background_color: string
}

export const toShortProductionParamsPayload = (
  data: ShortProductionParams,
): ShortProductionParamsPayload => {
  return {
    debug_frame: data.debugVideoFrame,
    hook_text: data.hookText,
    input_filename: data.inputFileName,
    watermark_text: data.watermarkText,
    frame_ts: data.frameTs,
    font_name: data.fontName,
    output_filename: data.outputFileName,
    background_color: data.backgroundColor
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
  min_words: number
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
    min_words: data.min_words,
    url: data.url,
  }
}
