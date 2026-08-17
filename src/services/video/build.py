from src.domain.video.resizer import resize_zoomed_square
from src.domain.video.layer import add_text_to_template
from src.domain.video.assembler import assemble_video_and_template
from pathlib import Path


async def build_v1(
    params,
    input_dir: Path | str,
    output_dir: Path | str,
    temp_dir: Path | str,
    template_dir: Path | str,
    font_dir: Path | str,
):
    input_filename = params.get("input_filename")
    force_resize = params.get("force_resize", True)
    input_fp = Path(input_dir) / f"{input_filename}.mp4"
    resized_fp = Path(temp_dir) / "temp_resized.mp4"

    resized_fp = await resize_zoomed_square(input_fp, resized_fp, force_resize)

    template_name = params.get("template_name", "fp")
    template_path = Path(template_dir) / f"{template_name}.png"
    font_path = Path(font_dir) / "GoogleSans-Bold.ttf"
    hook_text = params.get("hook_text")
    hook_text = hook_text.replace("\\n", "\n")
    layer_fp = Path(temp_dir) / "temp_ui.png"
    layer_fp = add_text_to_template(
        template_path,
        font_path,
        hook_text,
        output_path=layer_fp,
    )

    output_filename = params.get("output_filename")
    output_fp = Path(output_dir) / f"{output_filename}.mp4"
    debug_frame = params.get("debug_frame")
    result = await assemble_video_and_template(
        resized_fp, output_fp, layer_fp, debug_frame, temp_dir
    )
    if debug_frame:
        print(f"Debug frame built at {Path(temp_dir) / "debug_frame.png"}")
    else:
        print(f"Video built at {result}")
