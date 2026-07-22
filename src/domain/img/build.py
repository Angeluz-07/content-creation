import os
from PIL import Image, ImageEnhance, ImageFilter, PngImagePlugin


def resize_to_fb_res(image_path, output_path, target_res=(1440, 1800)):

    with Image.open(image_path) as img:
        img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
        tw, th = target_res

        # 1. FONDO: Reducción drástica ultra rápida con BOX -> Blur -> Reescalado BILINEAR
        bg = (
            img.resize((64, 64), Image.Resampling.BOX)
            .filter(ImageFilter.GaussianBlur(3))
            .resize(target_res, Image.Resampling.BILINEAR)
        )
        canvas = ImageEnhance.Brightness(bg).enhance(0.85)

        # 2. IMAGEN PRINCIPAL: Mantiene máxima calidad visual (LANCZOS)
        scale = min(tw / img.width, th / img.height)
        new_size = (int(img.width * scale), int(img.height * scale))
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

        # 3. COMPOSICIÓN Y GUARDADO VELOZ
        x_offset = (tw - new_size[0]) // 2
        y_offset = (th - new_size[1]) // 2
        canvas.paste(img_resized, (x_offset, y_offset))

        # compress_level=1 escribe el PNG de forma casi instantánea en disco
        canvas.save(
            output_path, "PNG", pnginfo=PngImagePlugin.PngInfo(), compress_level=1
        )
        return output_path


def apply_overlay(image_path, overlay_path, output_path):
    """
    Toma una imagen base (1440x1800) y le aplica la plantilla PNG con transparencia arriba.
    """

    with Image.open(image_path).convert("RGB") as base, Image.open(
        overlay_path
    ).convert("RGBA") as overlay:
        # Asegurar que la plantilla coincida en tamaño
        if overlay.size != base.size:
            overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)

        # Aplicar la plantilla usando su propio canal alfa como máscara
        base.paste(overlay, (0, 0), mask=overlay)

        # Guardado ultra rápido
        base.save(
            output_path, "PNG", pnginfo=PngImagePlugin.PngInfo(), compress_level=1
        )

    return output_path


import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


def render_tiktok_style_text(
    image_path,
    text,
    output_path,
    font_path="arial.ttf",  # Se recomienda una fuente gruesa (Arial Bold, Impact, Montserrat Bold)
    font_size=52,
    style="white_on_black",  # Opciones: "black_on_white" o "white_on_black"
    max_chars_per_line=24,
    y_position=1350,  # Posición vertical sugerida para el tercio inferior
):
    """
    Renders text in the classic TikTok editor sticker style with a rounded background box.
    """

    # Definir paleta según el estilo
    if style == "black_on_white":
        bg_color = (255, 255, 255)
        text_color = (0, 0, 0)
    else:  # "white_on_black"
        bg_color = (0, 0, 0)
        text_color = (255, 255, 255)

    with Image.open(image_path).convert("RGB") as base:
        draw = ImageDraw.Draw(base)
        img_w, _ = base.size

        # 1. Cargar fuente
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            font = ImageFont.load_default()

        # 2. Formatear en multilínea
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)

        # 3. Calcular caja del texto
        bbox = draw.multiline_textbbox(
            (0, 0), wrapped_text, font=font, align="center", spacing=8
        )
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # 4. Dimensiones y coordenadas de la caja (Sticker Padding)
        pad_x = 28
        pad_y = 18

        box_w = text_w + (pad_x * 2)
        box_h = text_h + (pad_y * 2)

        # Centrado horizontal de la caja
        box_x1 = (img_w - box_w) // 2
        box_y1 = y_position
        box_x2 = box_x1 + box_w
        box_y2 = box_y1 + box_h

        # 5. Dibujar caja redondeada de fondo (Estilo TikTok)
        draw.rounded_rectangle(
            [box_x1, box_y1, box_x2, box_y2], radius=18, fill=bg_color
        )

        # 6. Dibujar texto centrado dentro de la caja
        text_x = box_x1 + pad_x
        text_y = box_y1 + pad_y - bbox[1]  # Compensar offset interno de Pillow

        draw.multiline_text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=text_color,
            align="center",
            spacing=8,
        )

        # 7. Guardado ultra-rápido
        base.save(
            output_path, "PNG", pnginfo=PngImagePlugin.PngInfo(), compress_level=1
        )

    return output_path
