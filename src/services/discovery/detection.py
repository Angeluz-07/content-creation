from dataclasses import dataclass
from dataclasses import field
from abc import ABC, abstractmethod
from src.domain.discovery.parser import (
    parse_vtt,
    parse_discovery_results,
    parse_transcription,
    parse_vtt_,
    parse_transcription_,
)
from src.infra.dbs.qdrant import IVectorStore
from src.services.common.asset import AssetProvider
from src.domain.common import save_json, read_json
from src.domain.discovery.models import TextSegment
from typing import List
from pathlib import Path
from src.domain.discovery.parser import format_to_text_block

def find_metals(
    text_segments: List[TextSegment],
    vector_store: IVectorStore,
    sensitivity: float = 0.7,
):
    print("Looking for metals...")
    texts = [ts.text for ts in text_segments]
    most_similar_vectors = vector_store.search_batch(texts)
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
    vector_store: IVectorStore

    @abstractmethod
    def run(self):
        pass


class DetectorV2(BaseDetector):

    def run(self, data):
        input_filename = data.get("input_filename")
        output_filename = data.get("output_filename")
        url = data.get("url")
        source = data.get("source")
        output_path = self.assets.get_path("metals", output_filename)

        if Path(output_path).is_file() and not data.get("force", False):
            return read_json(output_path)

        print(f"Getting source {source} for metal detector..")
        if source == "vtt":
            vtt_path = self.assets.get_path("vtt", input_filename)
            result = parse_vtt(vtt_path)
        elif source == "audio":
            trascription_path = self.assets.get_path("transcriptions", input_filename)
            result = parse_transcription(trascription_path)
        else:
            raise ValueError("Source not valid")

        result = find_metals(result, self.vector_store, data.get("sensitivity"))
        result = parse_discovery_results(result, output_filename, url)
        save_json(result, output_path)
        return result

    def get_text(self, data):
        input_filename = data.get("input_filename")
        output_filename = data.get("output_filename")
        url = data.get("url")
        source = data.get("source")
        output_path = self.assets.get_path("metals", output_filename)

        if Path(output_path).is_file() and not data.get("force", False):
            return read_json(output_path)

        print(f"Getting source {source} for metal detector..")
        if source == "vtt":
            vtt_path = self.assets.get_path("vtt", input_filename)
            result = parse_vtt_(vtt_path)
        elif source == "audio":
            trascription_path = self.assets.get_path("transcriptions", input_filename)
            result = parse_transcription_(trascription_path)
        else:
            raise ValueError("Source not valid")

        return result


class DetectorV3:

    def __init__(self, assets, downloader, transcriber):
        self.assets = assets
        self.downloader = downloader
        self.transcriber = transcriber

    def run(self, data):
        text_segments = self.get_text_segments(data)
        text_for_llm = format_to_text_block(text_segments)
        return text_for_llm
    
    def get_text_segments(self, data):
        print("Looking for assets in detector...")
        output_filename = data["output_filename"]
        vtt_path = self.assets.get_path("vtt", output_filename)
        if Path(vtt_path).is_file(): # vtt exists
            print(f"Vtt exists {output_filename}")
            result = parse_vtt_(vtt_path)
            return result
    
        force_transcription = False
        transcription_path = self.assets.get_path("transcriptions", output_filename)
        if Path(transcription_path).is_file() and not force_transcription:
            print(f"Transcription exists {output_filename}")
            result = parse_transcription_(transcription_path)
            return result

        # if files dont exists...
        try:
            print("Vtt doesnt exists, downloading...")
            vtt_path = self.downloader.run({**data, "file_type": "vtt"})
            has_vtt = True
        except Exception as e:
            print("No vtt available.")
            has_vtt = False
    
        if has_vtt:
            result = parse_vtt_(vtt_path)
            return result
    
        print("VTT not available. Downloading audio...")
        audio_path = self.downloader.run({**data, "file_type": "audio"})
        print(f"Generating transcription for {audio_path}...")
        transcription = self.transcriber.transcribe(audio_path)
        save_json(transcription, transcription_path)
        print(f"Transcription saved at {transcription_path}")
        result = parse_transcription_(transcription_path)
        return result
