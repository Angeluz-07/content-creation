from pathlib import Path
from typing import Literal
from src.domain.common import run_async_subprocess

FileType = Literal["video", "vtt", "audio"]


# --- PURE HELPERS & COMMAND BUILDERS ---
def remove_middle_extension(file_path: Path) -> Path:
    """Cleans intermediate language/type extensions like '.es.vtt' -> '.vtt'"""
    if len(file_path.suffixes) >= 2:
        clean_name = f"{file_path.stem.split('.')[0]}{file_path.suffix}"
        new_path = file_path.with_name(clean_name)
        if file_path.exists():
            file_path.rename(new_path)
        return new_path
    return file_path


def _base_ytdlp_cmd(cookies_path: Path | str) -> list[str]:
    """Base yt-dlp arguments shared across all media download types."""
    # fmt: off
    return [
        "yt-dlp",
        "--external-downloader-args", "ffmpeg:-loglevel error",
        "--postprocessor-args", "ffmpeg:-loglevel error",
        "--force-overwrites",
        "--no-playlist",
        "--cookies", str(cookies_path),
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
    ]
    # fmt: on


def build_video_cmd(
    url: str, start: str, end: str, output_path: Path, cookies: Path | str
) -> list[str]:
    # fmt: off
    return [
        *_base_ytdlp_cmd(cookies),
        url,
        "-f", "bestvideo[height=720]+bestaudio/best[height=720]",
        "--download-sections", f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        "--merge-output-format", "mp4",
        "--extractor-args", "youtube:player_client=default",
        "-o", str(output_path),
    ]
    # fmt: on


def build_vtt_cmd(url: str, output_path: Path, cookies: Path | str) -> list[str]:
    # fmt: off
    return [
        *_base_ytdlp_cmd(cookies),
        url,
        "--write-subs",
        "--write-auto-sub",
        "--sub-lang", "es",
        "--skip-download",
        "--convert-subs", "vtt",
        "-o", str(output_path),
    ]
    # fmt: on


def build_audio_cmd(url: str, output_path: Path, cookies: Path | str) -> list[str]:
    # fmt: off
    return [
        *_base_ytdlp_cmd(cookies),
        url,
        "--extract-audio",
        "--audio-format", "m4a",
        "-f", "wa[ext=m4a]",
        "--postprocessor-args", "ExtractAudio:-c:a aac -ac 1 -b:a 48k -af aresample=async=1",
        "-o", str(output_path),
    ]
    # fmt: on


# --- AGNOSTIC WORKFLOWS ---
async def download_video(
    url: str,
    output_path: Path | str,
    cookies_path: Path | str,
    start: str,
    end: str,
    force: bool = False,
) -> Path:
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not out_p.is_file() or force:
        cmd = build_video_cmd(url, start, end, out_p, cookies_path)
        await run_async_subprocess(cmd)
    return out_p


async def download_vtt(
    url: str,
    output_filename: str,
    output_dir: Path | str,
    cookies_path: Path | str,
    force: bool = False,
) -> Path:
    out_p = Path(output_dir) / output_filename
    out_p.parent.mkdir(parents=True, exist_ok=True)

    base_output = out_p.with_suffix("")
    target_vtt = out_p.with_suffix(".vtt")

    if not target_vtt.is_file() or force:
        cmd = build_vtt_cmd(url, base_output, cookies_path)
        await run_async_subprocess(cmd)

    raw_vtt = Path(f"{base_output}.es.vtt")
    if not raw_vtt.is_file() and not target_vtt.is_file():
        raise ValueError(f"Subtitle download failed: '{raw_vtt}' not generated.")

    return remove_middle_extension(raw_vtt) if raw_vtt.is_file() else target_vtt


async def download_audio(
    url: str,
    output_path: Path | str,
    cookies_path: Path | str,
    force: bool = False,
) -> Path:
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not out_p.is_file() or force:
        cmd = build_audio_cmd(url, out_p.with_suffix(""), cookies_path)
        await run_async_subprocess(cmd)
    return out_p.with_suffix(".m4a")


# --- UNIFIED DISPATCHER ---
async def download_media(params: dict, cookies_path: str | Path, base) -> Path:
    """
    Expects params dict with 'file_type', 'url', 'output_path', and 'cookies_path'.
    """
    file_type: FileType = params["file_type"]
    url: str = params["url"]
    output_path: Path | str = params["output_path"]
    cookies_path: Path | str = params["cookies_path"]
    force: bool = params.get("force_download", False)

    if file_type == "video":
        path = await download_video(
            url=url,
            output_path=output_path,
            cookies_path=cookies_path,
            start=params["start_segment"],
            end=params["end_segment"],
            force=force,
        )
    elif file_type == "vtt":
        path = await download_vtt(
            url=url,
            output_path=output_path,
            cookies_path=cookies_path,
            force=force,
        )
    elif file_type == "audio":
        path = await download_audio(
            url=url,
            output_path=output_path,
            cookies_path=cookies_path,
            force=force,
        )
    else:
        raise ValueError(f"Unknown file_type: {file_type}")

    print(f"File saved in {path}")
    return path


class YTDownloader:

    def __init__(self, base_dir, cookies_path):
        self.cookies_path = cookies_path
        self.base_dir = base_dir

    async def run(self, params):
        params = params.copy()
        file_type = params.get("file_type")
        params["output_path"] = (
            Path(self.base_dir) / file_type / params.pop("output_filename")
        )
        params["cookies_path"] = self.cookies_path
        return await download_media(params)
