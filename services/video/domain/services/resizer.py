from pathlib import Path
from domain.services.common import run_async_subprocess
from domain.services.common import run_subprocess


class Resizer:

    def __init__(self, temp_path):
        self.temp_path = temp_path

    async def run_async(
        self, input: str, output_type: str = "almost_at_top", force=False, **kwargs
    ):
        resized = self.get_resized_filepath(input)
        resized_exists = Path(resized).is_file()
        if force or not resized_exists:
            print("Start resizing (Async)...")

            video_filter = self.get_video_filter(output_type, **kwargs)
            ffmpeg_cmd = self.get_comand(input, video_filter, resized)

            await run_async_subprocess(command=ffmpeg_cmd)

            print(f"Resizing successful with file: {resized}")
            return resized
        else:
            print("Resized file exists. Skipping resizing...")
            return resized

    def run(
        self, input: str, output_type: str = "almost_at_top", force=False, **kwargs
    ):
        resized = self.get_resized_filepath(input)
        resized_exists = Path(resized).is_file()
        if force or not resized_exists:
            print("Start resizing (Sync)...")

            video_filter = self.get_video_filter(output_type, **kwargs)
            ffmpeg_cmd = self.get_comand(input, video_filter, resized)

            run_subprocess(command=ffmpeg_cmd)

            print(f"Resizing successful with file: {resized}")
            return resized
        else:
            print("Resized file exists. Skipping resizing...")
            return resized

    def get_resized_filepath(self, input_path: str):
        file_id = Path(input_path).stem
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_resized.mp4")
        return resized_filepath

    def get_video_filter(self, output_type: str, **kwargs):
        video_filters = {
            "almost_at_top": self.get_filter_almost_at_top,
            "at_top": self.get_filter_at_top,
            "full_vertical": self.get_filter_full_vertical,
            "middle": self.get_filter_middle,
        }
        filter_fn = video_filters[output_type]
        if output_type == "full_vertical":
            percentage = kwargs.get(
                "percentage", 0.0
            )  # 0.0 es el valor por defecto si no se pasa
            return filter_fn(percentage=percentage)

        return filter_fn()

    def get_comand(self, input: str, video_filter: str, resized: str) -> list[str]:
        # fmt: off
        encoders = [
            "-c:v", "libx264",
            "-crf", "21",
            "-preset", "fast"
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
            resized,
        ]
        # fmt: on
        return ffmpeg_cmd

    def get_filter_middle(self):
        POS_Y = 480
        CANVAS_W, CANVAS_H = 1080, 1920
        ZOOM_FACTOR = 1.53
        TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

        # fmt: off
        safe_filter = (
            f"scale={TARGET_W}:-1,"
            "setsar=1:1,"
            f"crop={CANVAS_W}:ih,"
            f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
        )        
        # fmt: on
        return safe_filter

    def get_filter_almost_at_top(self):
        POS_Y = 180
        CANVAS_W, CANVAS_H = 1080, 1920
        ZOOM_FACTOR = 1.53
        TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

        # fmt: off
        safe_filter = (
            f"scale={TARGET_W}:-1,"
            "setsar=1:1,"
            f"crop={CANVAS_W}:ih,"
            f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
        )        
        # fmt: on
        return safe_filter

    def get_filter_at_top(self):
        POS_Y = 0
        CANVAS_W, CANVAS_H = 1080, 1920
        ZOOM_FACTOR = 1.53
        TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

        # fmt: off
        safe_filter = (
            f"scale={TARGET_W}:-1,"
            "setsar=1:1,"
            f"crop={CANVAS_W}:ih,"
            f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
        )
        return safe_filter

    def get_filter_full_vertical(self, percentage=0.0):
        CANVAS_W, CANVAS_H = 1080, 1920
        # fmt: off
        safe_filter = (
            f"scale=-1:{CANVAS_H}:flags=lanczos,"
            f"crop={CANVAS_W}:{CANVAS_H}:"
            f"(iw-{CANVAS_W})*{percentage}:0,"
            f"setsar=1:1"
        )
        # fmt: on
        return safe_filter
