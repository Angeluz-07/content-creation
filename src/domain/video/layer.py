from PIL import Image, ImageDraw, ImageFont


def add_text_to_template(template_path, font_path, text, output_path):

    imagen = Image.open(template_path).convert("RGBA")
    capa_texto = Image.new("RGBA", imagen.size, (255, 255, 255, 0))
    canvas = ImageDraw.Draw(capa_texto)

    fuente = ImageFont.truetype(font_path, size=60)
    texto_dinamico = text

    # fixed for the template
    x_centro = 720 // 2
    y_pos = 920

    canvas.text(
        (x_centro, y_pos),
        texto_dinamico,
        font=fuente,
        fill="#E0E0E0",  # Blanco sólido en RGBA
        anchor="mm",  # Centro geométrico
        align="center",  # Centra las líneas de texto entre sí
        stroke_width=1,  # <--- Grosor del borde en píxeles (Prueba con 2 o 3)
        stroke_fill="#E0E0E0",  # <--- El mismo color del texto para engrosarlo
    )

    enfoque_final = Image.alpha_composite(imagen, capa_texto)

    # 8. Guardar en PNG (mantiene la transparencia del fondo si la había)
    enfoque_final.save(output_path, "PNG")
    return output_path
