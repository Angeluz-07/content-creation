// types/config.ts
export interface ShortProductionParams {
  inputFileName: string;
  fontName: string;
  watermarkText: string; 
  frameTs: string;  
  hookText: string;
  debugVideoFrame: boolean;
  outputFileName: string;
}

export interface DownloadParams {
  url: string;
  startSegment: string;
  endSegment: string;
  outputFileName: string;
  forceDownload: boolean;
  file_type: string
}