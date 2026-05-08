// mappers/config.ts
import type { ShortProductionParams, DownloadParams } from '../types/config';

// todo: I could prescind of mappers by defining the API to receive properties as camelCase
// since by now the mapping is redundant
// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface ShortProductionParamsPayload {
  debug_video_frame: boolean;
  hook_text: string;
  filename: string;
  watermark_text: string;
  frame_ts: string;
  font_name: string;
}

export const toShortProductionParamsPayload = (data: ShortProductionParams): ShortProductionParamsPayload => {
  return {
    debug_video_frame: data.debugVideoFrame,
    hook_text: data.hookText,
    filename: data.fileName,
    watermark_text: data.watermarkText,
    frame_ts: data.frameTs,
    font_name: data.fontName
  };
};

export interface DownloadParamsPayload {
  url: string;
  force_download: boolean;
  start_segment: string;
  end_segment: string;
  filename: string;
}

export const toDownloadParamsPayload = (data: DownloadParams): DownloadParamsPayload => {
  return {
    url: data.url,
    force_download: data.forceDownload,
    start_segment: data.startSegment,
    end_segment: data.endSegment,
    filename: data.fileName,
  };
};