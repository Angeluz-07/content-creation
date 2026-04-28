// types/config.ts
export interface Config {
  url: string;
  forceDownload: boolean;
  debugVideoFrame: boolean;
  startSegment: string;
  endSegment: string;
  hookText: string;
  outname: string;
}