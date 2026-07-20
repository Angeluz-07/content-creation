// types/config.ts
export interface VideoBuildInput {
  inputFileName: string;
  templateName: string;
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

export interface DiscoveryInput {
  inputFileName: string
  outputFileName: string;
  sensitivity: number;
  url: string;
}