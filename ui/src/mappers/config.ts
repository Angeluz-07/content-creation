// mappers/config.ts
import type { Config, DownloadParams } from '../types/config';

// todo: I could prescind of mappers by defining the API to receive properties as camelCase
// since by now the mapping is redundant
// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface ConfigPayload {
  url: string;
  force_download: boolean;
  debug_video_frame: boolean;
  start_segment: string;
  end_segment: string;
  hook_text: string;
  outname: string;
  watermark_text: string;
  frame_ts: string;
  font_name: string;
}

export const mapConfigToPayload = (data: Config): ConfigPayload => {
  return {
    url: data.url,
    force_download: data.forceDownload,
    debug_video_frame: data.debugVideoFrame,
    start_segment: data.startSegment,
    end_segment: data.endSegment,
    hook_text: data.hookText,
    outname: data.outname,
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