from dataclasses import dataclass
from dataclasses import field
from abc import ABC, abstractmethod
from src.domain.discovery.parser import parse_vtt, parse_discovery_results
from src.dbs.qdrant import IVectorStore
from src.services.common.asset import AssetProvider
from src.domain.common import save_json
from src.services.discovery.embedding import Embedder

from src.domain.discovery.models import TextSegment
from typing import List


def find_metals(
    text_segments: List[TextSegment],
    embedder: Embedder,
    vector_store: IVectorStore,
    sensitivity: float = 0.7,
):
    texts = [ts.text for ts in text_segments]
    vectors = embedder.get_vectors(texts)
    most_similar_vectors = vector_store.search_batch(vectors)
    result = []
    for i, ts in enumerate(text_segments):
        score = most_similar_vectors[i].points[0].score
        if score >= sensitivity:
            result.append(
                {
                    "start": ts.start,
                    "end": ts.end,
                    "text": ts.text,
                    "score": score,
                }
            )
    return result


@dataclass
class BaseDetector(ABC):
    assets: AssetProvider
    embedder: Embedder
    vector_store: IVectorStore

    @abstractmethod
    def run(self):
        pass


class DetectorV2(BaseDetector):

    def run(self, data):
        input_filename = data.get("input_filename")
        output_filename = data.get("output_filename")
        url = data.get("url")
        vtt_path = self.assets.get_path("vtt", input_filename)
        output_path = self.assets.get_path("metals", output_filename)
        result = parse_vtt(vtt_path)
        result = find_metals(
            result, self.embedder, self.vector_store, data.get("sensitivity")
        )
        result = parse_discovery_results(result, output_filename, url)
        save_json(result, output_path)
        return result


class DetectorV3(BaseDetector):

    def run(self, data, transcription_parser):
        input_filename = data.get("input_filename")
        output_filename = data.get("output_filename")
        url = data.get("url")

        transcription_path = self.assets.get_path("transcriptions", input_filename)
        output_path = self.assets.get_path("metals", output_filename)

        result = transcription_parser.run(transcription_path, data.get("min_words"))
        print("debug v3", result[0])
        result = self.scanner.run(result, data.get("sensitivity"))
        result = self.discovery_parser.run(result, output_filename, url)
        save_json(result, output_path)
        return result
