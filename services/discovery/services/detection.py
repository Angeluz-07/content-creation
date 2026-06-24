from pathlib import Path
import webvtt
from difflib import SequenceMatcher
import json


class Detector:
    def __init__(self, vector_store, embedder, vtt_dir, output_dir):
        self.vector_store = vector_store
        self.embedder = embedder
        self.vtt_dir = vtt_dir
        self.output_dir = output_dir

    def run(self, data: dict):
        vtt_path = str(Path(self.vtt_dir) / data.get("input_filename"))
        result = self.scan_vtt(vtt_path, data.get("sensitivity"), data.get("min_words"))
        output_path = str(Path(self.output_dir) / f"{data.get("output_filename")}.json")
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=4)

        print("Scan of vtt completed")

    def scan_vtt(self, vtt_path, sensitivity=0.70, min_words=90):
        """
        Escanea el VTT usando el Detector de Calor Semántico.
        Retorna segmentos continuos fusionados que superen la temperatura mínima.
        """
        # 1. Limpieza inicial del VTT
        fragmentos_limpios = self.clean_vtt(vtt_path)

        # 2. Agrupamiento por bloques de sentido (Estructura fluida)
        bloques = self.group_by_semantic_sense(fragmentos_limpios, min_words)
        if not bloques:
            return []

        textos = [b["texto"] for b in bloques]

        # 3. Inferencia Batch (Un solo viaje para todos los embeddings)
        vectores = self.embedder.get_vectors(textos)

        # 4. Medidor de Temperatura Semántica
        bloques_calientes = []
        for i, bloque in enumerate(bloques):
            resultados = self.vector_store.search(vectores[i], top_k=1)
            points = resultados.points if hasattr(resultados, "points") else resultados

            if points and len(points) > 0:
                mejor_resultado = points[0]
                score = mejor_resultado.score

                # Evaluamos si entra en Zona Templada o Caliente
                if score >= sensitivity:
                    bloques_calientes.append(
                        {
                            "start": bloque["start"],
                            "end": bloque["end"],
                            "score": score,
                            "texto": bloque["texto"],
                            "match": mejor_resultado.payload.get("archivo"),
                        }
                    )

        # 5. Fusión temporal de momentos contiguos de alto interés
        candidatos_finales = self.merge_adjacent_segments(bloques_calientes)
        return candidatos_finales

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
                        "texto": texto_actual_combinado,
                        "start": start_ts,
                        "end": frag["end"],
                    }
                )
                acumulador = []

        # Asegurar el remanente final si existe
        if acumulador:
            bloques.append(
                {
                    "texto": " ".join(acumulador),
                    "start": start_ts,
                    "end": fragmentos[-1]["end"],
                }
            )

        return bloques

    def merge_adjacent_segments(self, bloques_calientes):
        """
        Toma bloques individuales de interés y, si son consecutivos en el tiempo,
        los unifica en un solo clip extendido de video viral para evitar micro-cortes.
        """
        if not bloques_calientes:
            return []

        segmentos_fusionados = []
        # Inicializamos el primer candidato con la data del primer bloque caliente
        actual = {
            "start": bloques_calientes[0]["start"],
            "end": bloques_calientes[0]["end"],
            "max_score": bloques_calientes[0]["score"],
            "textos": [bloques_calientes[0]["texto"]],
            "matches": (
                {bloques_calientes[0]["match"]}
                if bloques_calientes[0]["match"]
                else set()
            ),
        }

        for siguiente in bloques_calientes[1:]:
            # Si el inicio del bloque siguiente coincide con el final del actual, se fusionan
            if siguiente["start"] == actual["end"]:
                actual["end"] = siguiente["end"]
                actual["max_score"] = max(actual["max_score"], siguiente["score"])
                actual["textos"].append(siguiente["texto"])
                if siguiente["match"]:
                    actual["matches"].add(siguiente["match"])
            else:
                # Si hay una brecha de tiempo, cerramos el actual y abrimos uno nuevo
                segmentos_fusionados.append(self._build_segment_payload(actual))
                actual = {
                    "start": siguiente["start"],
                    "end": siguiente["end"],
                    "max_score": siguiente["score"],
                    "textos": [siguiente["texto"]],
                    "matches": {siguiente["match"]} if siguiente["match"] else set(),
                }

        segmentos_fusionados.append(self._build_segment_payload(actual))
        return segmentos_fusionados

    def _build_segment_payload(self, data):
        return {
            "start": data["start"],
            "end": data["end"],
            "peak_score": data["max_score"],
            "full_context": " ".join(data["textos"]),
            "referenced_patterns": list(data["matches"]),
        }
