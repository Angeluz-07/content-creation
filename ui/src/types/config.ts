// types/config.ts
export interface ShortProductionParams {
  fileName: string;
  fontName: string;
  watermarkText: string; 
  frameTs: string;  
  hookText: string;
  debugVideoFrame: boolean;
}

export interface DownloadParams {
  url: string;
  startSegment: string;
  endSegment: string;
  fileName: string;
  forceDownload: boolean;
}