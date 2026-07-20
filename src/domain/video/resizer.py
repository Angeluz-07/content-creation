from pathlib import Path
from src.domain.common import run_async_subprocess
from src.domain.common import run_subprocess


def get_filter_zoomed_square(input, output):
    CANVAS_W, CANVAS_H = 720, 1280
    ZOOM_FACTOR = 1.53
    TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

    # fmt: off
    video_filter = (
        f"scale={TARGET_W}:-1:flags=fast_bilinear,"
        f"setsar=1:1,"
        f"crop={CANVAS_W}:ih,"
    )        
    encoders = [
        "-c:v", "libx264",
        "-crf", "14", # the lower the better fidelity quality of input, 14 is ok.
        "-preset", "superfast",
    ]
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loglevel","error",
        "-stats",
        "-i", input,
        "-vf", video_filter,
        *encoders,
        "-pix_fmt", "yuv420p", # ensures compatibility
        "-c:a", "copy",
        output,
    ]
    # fmt: on
    return ffmpeg_cmd


def get_filter_full_vertical(input, output, percentage):
    CANVAS_W, CANVAS_H = 720, 1280
    # fmt: off
    video_filter = (
        f"scale=-1:{CANVAS_H}:flags=lanczos,"
        f"crop={CANVAS_W}:{CANVAS_H}:"
        f"(iw-{CANVAS_W})*{percentage}:0,"
        f"setsar=1:1"
    ) 
    encoders = [
        "-c:v", "libx264",
        "-crf", "14", # the lower the better fidelity quality of input, 14 is ok.
        "-preset", "superfast",
    ]
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loglevel","error",
        "-stats",
        "-i", input,
        "-vf", video_filter,
        *encoders,
        "-pix_fmt", "yuv420p", # ensures compatibility
        "-c:a", "copy",
        output,
    ]
    # fmt: on
    return ffmpeg_cmd


def resize_zoomed_square(input: str, output: str, force: bool):
    resized = output
    resized_exists = Path(output).is_file()
    if force or not resized_exists:
        print("Start resizing (Sync)...")
        ffmpeg_cmd = get_filter_zoomed_square(input, output)
        run_subprocess(command=ffmpeg_cmd)
        print(f"Resizing successful with file: {resized}")
        return resized
    else:
        print("Resized file exists. Skipping resizing...")
        return resized


def resize_full_vertical(input: str, output: str, force: bool, percentage=0.0):
    resized = output
    resized_exists = Path(output).is_file()
    if force or not resized_exists:
        print("Start resizing (Sync)*...")
        ffmpeg_cmd = get_filter_full_vertical(input, output, percentage)
        run_subprocess(command=ffmpeg_cmd)
        print(f"Resizing successful with file: {resized}")
        return resized
    else:
        print("Resized file exists. Skipping resizing...")
        return resized


async def resize_zoomed_square_async(input: str, output: str, force: bool):
    resized = output
    resized_exists = Path(output).is_file()
    if force or not resized_exists:
        print("Start resizing (Async)*...")
        ffmpeg_cmd = get_filter_zoomed_square(input, output)
        await run_async_subprocess(command=ffmpeg_cmd)
        print(f"Resizing successful with file: {resized}")
        return resized
    else:
        print("Resized file exists. Skipping resizing...")
        return resized
