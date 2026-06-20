// mappers/config.ts
import type { ShortProductionParams, DownloadParams } from '../types/config';

// todo: I could prescind of mappers by defining the API to receive properties as camelCase
// since by now the mapping is redundant
// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface ShortProductionParamsPayload {
  debug_frame: boolean;
  hook_text: string;
  input_filename: string;
  watermark_text: string;
  frame_ts: string;
  font_name: string;
  output_filename: string;
}

export const toShortProductionParamsPayload = (data: ShortProductionParams): ShortProductionParamsPayload => {
  return {
    debug_frame: data.debugVideoFrame,
    hook_text: data.hookText,
    input_filename : data.inputFileName,
    watermark_text: data.watermarkText,
    frame_ts: data.frameTs,
    font_name: data.fontName,
    output_filename: data.outputFileName
  };
};

export interface DownloadParamsPayload {
  url: string;
  force_download: boolean;
  start_segment: string;
  end_segment: string;
  output_filename: string;
}

export const toDownloadParamsPayload = (data: DownloadParams): DownloadParamsPayload => {
  return {
    url: data.url,
    force_download: data.forceDownload,
    start_segment: data.startSegment,
    end_segment: data.endSegment,
    output_filename: data.outputFileName,
  };
};