import subprocess

def download_segment_from_yt(start_ts: str, end_ts : str, url:str, output_path: str):
    """
    start_ts -> "00:01:00"
    end_ts -> "00:01:28"
    """
    ydl_opts = [
        'yt-dlp', '--quiet', '--no-warnings',
        '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4',
        '--external-downloader', 'ffmpeg',
        '--external-downloader-args', f'ffmpeg_i:-ss {start_ts} -to {end_ts}',
        url, '-o', output_path
    ]
    try:
        print("📥 Downloading segment from YouTube...")
        subprocess.run(ydl_opts, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error on download: {e}")
        return