from pathlib import Path
from domain.services.build.common import run_async_subprocess


class Resizer:

    def __init__(self, temp_path):
        self.temp_path = temp_path

    async def run(self, input_filepath: str, output_type: str = "almost_at_top"):

        video_filters = {
            "almost_at_top": self.get_filter_almost_at_top(),
            "at_top": self.get_filter_at_top(),
            "full_vertical": self.get_filter_full_vertical(),
        }
        video_filter: str = video_filters[output_type]
        resized_filepath = await self._resize_video_segment(
            input_filepath, video_filter
        )
        return resized_filepath

    async def _resize_video_segment(
        self, input_filepath: str, video_filter: str, force_resize: bool = False
    ):
        file_id = Path(input_filepath).stem
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if force_resize or not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
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
                "-i", input_filepath,
                "-vf", video_filter,
                *encoders,
                "-pix_fmt", "yuv420p", # ensures compatibility
                "-c:a", "copy",
                resized_filepath,
            ]
            # fmt: on
            print("Resizing video for mobile canvas...")
            await run_async_subprocess(command=ffmpeg_cmd)

            print(f"Resizing successful with file: {resized_filepath}")
            return resized_filepath
        else:
            print("Resized file exists. Skipping resizing...")
            return resized_filepath

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

    def get_filter_full_vertical(self):
        percentage = 0
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
