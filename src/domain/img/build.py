import textwrap
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


def resize_to_fb_res(img: Image.Image, target_res=(1440, 1800)) -> Image.Image:
    """Ajusta resolución a formato FB creando un fondo borroso."""
    img = img.convert("RGB") if img.mode in ("RGBA", "P") else img.copy()
    tw, th = target_res

    # 1. Fondo borroso
    bg = (
        img.resize((64, 64), Image.Resampling.BOX)
        .filter(ImageFilter.GaussianBlur(3))
        .resize(target_res, Image.Resampling.BILINEAR)
    )
    canvas = ImageEnhance.Brightness(bg).enhance(0.85)

    # 2. Reescalado principal
    scale = min(tw / img.width, th / img.height)
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # 3. Composición
    x_offset = (tw - new_size[0]) // 2
    y_offset = (th - new_size[1]) // 2
    canvas.paste(img_resized, (x_offset, y_offset))

    return canvas


def apply_overlay(
    base_img: Image.Image, overlay_img: Image.Image
) -> Image.Image:
    """Aplica una plantilla PNG con transparencia sobre la imagen base."""
    base = base_img.copy().convert("RGB")
    overlay = overlay_img.convert("RGBA")

    if overlay.size != base.size:
        overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)

    base.paste(overlay, (0, 0), mask=overlay)
    return base


def render_tiktok_style_text(
    img: Image.Image,
    text: str,
    font_path="arial.ttf",
    font_size=52,
    style="white_on_black",
    max_chars_per_line=24,
    y_position=1350,
) -> Image.Image:
    """Renderiza texto estilo TikTok con fondo redondeado."""
    base = img.copy().convert("RGB")
    draw = ImageDraw.Draw(base)
    img_w, _ = base.size

    bg_color, text_color = (
        ((255, 255, 255), (0, 0, 0))
        if style == "black_on_white"
        else ((0, 0, 0), (255, 255, 255))
    )

    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        font = ImageFont.load_default()

    wrapped_text = textwrap.fill(text, width=max_chars_per_line)
    bbox = draw.multiline_textbbox(
        (0, 0), wrapped_text, font=font, align="center", spacing=8
    )
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x, pad_y = 28, 18
    box_w, box_h = text_w + (pad_x * 2), text_h + (pad_y * 2)

    box_x1 = (img_w - box_w) // 2
    box_y1 = y_position
    box_x2, box_y2 = box_x1 + box_w, box_y1 + box_h

    draw.rounded_rectangle(
        [box_x1, box_y1, box_x2, box_y2], radius=18, fill=bg_color
    )

    text_x = box_x1 + pad_x
    text_y = box_y1 + pad_y - bbox[1]

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font,
        fill=text_color,
        align="center",
        spacing=8,
    )
    return base