import webvtt
from difflib import SequenceMatcher
from .models import TextSegment

class VTTParser:

    def run(self, archivo_vtt, min_words=90):
        result = self.clean_vtt(archivo_vtt)
        result = self.group_by_semantic_sense(result, min_words)
        result = [TextSegment(**values) for values in result]
        return result
    
    def clean_vtt(self, archivo_vtt):
        vtt = webvtt.read(archivo_vtt)
        resultado = []
        texto_previo = ""

        for c in vtt:
            texto_actual = c.text.replace("\n", " ").strip()

            matcher = SequenceMatcher(None, texto_previo, texto_actual)
            match = matcher.find_longest_match(
                0, len(texto_previo), 0, len(texto_actual)
            )

            if match.a + match.size == len(texto_previo):
                novedad = texto_actual[match.b + match.size :].strip()
            else:
                novedad = texto_actual

            if novedad:
                resultado.append({"start": c.start, "end": c.end, "text": novedad})
                texto_previo = texto_actual

        return resultado

    def group_by_semantic_sense(self, fragmentos, min_words):
        """
        Agrupa fragmentos respetando los cierres de oraciones (puntos, signos).
        Asegura un mínimo de palabras para mantener la riqueza del embedding.
        """
        bloques = []
        acumulador = []
        start_ts = None

        for frag in fragmentos:
            if not acumulador:
                start_ts = frag["start"]

            acumulador.append(frag["text"])
            texto_actual_combinado = " ".join(acumulador)
            palabras = texto_actual_combinado.split()

            # Condición de cierre semántico: termina en punto/signo AND tiene longitud suficiente
            termina_idea = frag["text"].endswith((".", "!", "?", "..."))

            if len(palabras) >= min_words and (termina_idea or len(palabras) > 60):
                bloques.append(
                    {
                        "text": texto_actual_combinado,
                        "start": start_ts,
                        "end": frag["end"],
                    }
                )
                acumulador = []

        # Asegurar el remanente final si existe
        if acumulador:
            bloques.append(
                {
                    "text": " ".join(acumulador),
                    "start": start_ts,
                    "end": fragmentos[-1]["end"],
                }
            )

        return bloques