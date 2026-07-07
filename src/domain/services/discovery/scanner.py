from typing import List
from .models import TextSegment

class Scanner:
    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def run(self, texts: List[TextSegment], sensitivity=0.7):
        result = self.scan_result(texts, sensitivity)
        print("Scan of text segments is completed")
        return result

    def scan_result(self, bloques: List[TextSegment], sensitivity):
        """
        Escanea el VTT usando el Detector de Calor Semántico.
        Retorna segmentos continuos fusionados que superen la temperatura mínima.
        """

        textos = [b.text for b in bloques]

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
                            "start": bloque.start,
                            "end": bloque.end,
                            "score": score,
                            "texto": bloque.text,
                            "match": mejor_resultado.payload.get("archivo"),
                        }
                    )

        # 5. Fusión temporal de momentos contiguos de alto interés
        candidatos_finales = self.merge_adjacent_segments(bloques_calientes)
        return candidatos_finales



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
