// types/config.ts
export interface Config {
  url: string;
  watermarkText: string; 
  forceDownload: boolean;
  debugVideoFrame: boolean;
  startSegment: string;
  endSegment: string;
  hookText: string;
  outname: string;
  frameTs: string;
  fontName: string;
}

export interface DownloadParams {
  url: string;
  startSegment: string;
  endSegment: string;
  fileName: string;
  forceDownload: boolean;
}