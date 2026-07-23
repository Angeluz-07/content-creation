from dataclasses import dataclass
from dataclasses import field
from abc import ABC, abstractmethod
from src.domain.discovery.parser import VTTParser
from src.domain.discovery.discovery_parser import DiscoveryParser
from src.domain.discovery.scanner import Scanner
from src.services.common.asset import AssetProvider
from src.domain.common import save_json


@dataclass
class BaseDetector(ABC):
    assets: AssetProvider
    scanner: Scanner
    vtt_parser: VTTParser = field(default_factory=VTTParser)
    discovery_parser: DiscoveryParser = field(default_factory=DiscoveryParser)

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
        result = self.vtt_parser.run(vtt_path)
        result = self.scanner.run(result, data.get("sensitivity"))
        result = self.discovery_parser.run(result, output_filename, url)
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
