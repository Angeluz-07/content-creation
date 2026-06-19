from uuid import uuid4
from typing import Dict
import requests
from domain.models import Production


class ProductionValidationError(Exception):
    """Raises when a condition is not me to start a video production"""

    pass


class ProductionService:
    def __init__(
        self,
        production_repo,
    ):
        self.production_repo = production_repo
        self.url = "http://localhost:8003"

    def trigger_sync(self, params: Dict):
        input_filename = params["input"]
        font_name = params["font_name"]
        watermark_text = params["watermark_text"]
        frame_ts = params["frame_ts"]
        hook_text = params["hook_text"]
        output_filename = params["output"]
        debug_video_frame = params["debug_frame"]

        response = requests.post(
            f"{self.url}/produce-short/synchronous",
            json={
                "input": input_filename,
                "font_name": font_name,
                "watermark_text": watermark_text,
                "frame_ts": frame_ts,
                "hook_text": hook_text,
                "output": output_filename,
                "debug_frame": debug_video_frame,
            },
        )

    def trigger_async(self, params: Dict):
        input_filename = params["input"]
        font_name = params["font_name"]
        watermark_text = params["watermark_text"]
        frame_ts = params["frame_ts"]
        hook_text = params["hook_text"]
        output_filename = params["output"]
        debug_video_frame = params["debug_frame"]

        response = requests.post(
            f"{self.url}/produce-short/prefect",
            json={
                "input": input_filename,
                "font_name": font_name,
                "watermark_text": watermark_text,
                "frame_ts": frame_ts,
                "hook_text": hook_text,
                "output": output_filename,
                "debug_frame": debug_video_frame,
            },
        )

    def project(self, params: Dict):
        item = Production(**params)
        self.production_repo.add(item)

    def get_new_uuid(self):
        return str(uuid4())

    def validate(self, params: Dict) -> None:
        """
        Ejecuta todas las reglas ad-hoc de forma secuencial.
        Lanza RuleValidationError si alguna falla.
        """
        self._validate_filename_not_exists(params)

    def _validate_filename_not_exists(self, params: Dict) -> None:
        filename = params.get("output")
        exists = self.production_repo.exists_by_filename(filename)
        if exists:
            raise ProductionValidationError(
                f"El archivo '{filename}' ya existe en la base de datos."
            )
