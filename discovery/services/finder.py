import webvtt
from difflib import SequenceMatcher


class Finder:
    def __init__(self, retriever, embedder):
        self.retriever = retriever
        self.embedder = embedder

    def find_candidates(self, vtt_path, threshold=0.8):
        # 1. Extraer (Solo CPU)
        bloques = self.clean_vtt(vtt_path)
        bloques = self.group_fragments(bloques)
        textos = [b["texto"] for b in bloques]
        # 2. Inferencia Batch (Un solo round-trip de red)
        vectores = self.embedder.get_vectors(textos)

        # 3. Procesamiento final
        candidatos = []
        for i, bloque in enumerate(bloques):
            # Aquí puedes usar retriever.search_by_vector si tu retriever lo permite
            # para evitar volver a calcular el embedding
            resultados = self.retriever.search_by_vector(vectores[i], top_k=1)
            points = resultados.points if hasattr(resultados, "points") else resultados
            mejor_resultado = points[0]
            if mejor_resultado.score >= threshold:
                candidatos.append(
                    {
                        "start": bloque["start"],
                        "end": bloque["end"],
                        "score": mejor_resultado.score,
                        "match": mejor_resultado.payload.get("archivo"),
                        "texto": bloque["texto"],
                    }
                )
        return candidatos

    def clean_vtt(self, archivo_vtt):
        vtt = webvtt.read(archivo_vtt)
        resultado = []
        texto_previo = ""

        for c in vtt:
            texto_actual = c.text.replace("\n", " ").strip()

            # 1. Encontrar el solapamiento exacto entre el bloque anterior y el actual
            # (Busca la coincidencia más larga al final de uno y al inicio del otro)
            matcher = SequenceMatcher(None, texto_previo, texto_actual)
            match = matcher.find_longest_match(
                0, len(texto_previo), 0, len(texto_actual)
            )

            # 2. Si el solapamiento ocurre al final del texto previo, lo recortamos
            if match.a + match.size == len(texto_previo):
                novedad = texto_actual[match.b + match.size :].strip()
            else:
                # Si no hay solapamiento claro, el bloque es texto nuevo completo
                novedad = texto_actual

            # 3. Guardar el resultado si aporta texto nuevo
            if novedad:
                resultado.append({"start": c.start, "end": c.end, "text": novedad})
                texto_previo = texto_actual

        return resultado

    def group_fragments(self, fragmentos_limpios):
        bloques = []
        acumulador_texto = []
        start_ts = None
        end_ts = None

        for frag in fragmentos_limpios:
            if start_ts is None:
                start_ts = frag["start"]

            acumulador_texto.append(frag["text"])
            end_ts = frag["end"]  # Actualizamos el final con el fragmento actual

            # Calcular la duración actual del bloque en segundos
            duracion = self.vtt_time_to_seconds(end_ts) - self.vtt_time_to_seconds(
                start_ts
            )

            # Si alcanzamos o superamos los 30 segundos, cerramos el bloque
            if duracion >= 30.0:
                bloques.append(
                    {
                        "texto": " ".join(acumulador_texto),
                        "start": start_ts,
                        "end": end_ts,
                    }
                )
                acumulador_texto = []
                start_ts = None  # Reiniciamos la ventana temporal

        # Guardar el residuo final si quedó texto sin completar los últimos 30s
        if acumulador_texto and start_ts and end_ts:
            bloques.append(
                {"texto": " ".join(acumulador_texto), "start": start_ts, "end": end_ts}
            )

        return bloques

    def _vtt_time_to_seconds(self, timestamp):
        parts = timestamp.split(":")
        h, m = int(parts[0]), int(parts[1])
        s, ms = map(float, parts[2].split("."))
        return h * 3600 + m * 60 + s + (ms / 1000)
