// mappers/config.ts
import type { Config } from '../types/config';

// Definimos el tipo de lo que espera el API (opcional, pero recomendado)
export interface ConfigPayload {
  url: string;
  force_download: boolean;
  debug_video_frame: boolean;
  start_segment: string;
  end_segment: string;
  hook_text: string;
  outname: string;
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
  };
};