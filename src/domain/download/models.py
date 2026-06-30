from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum
from datetime import datetime, timezone


@dataclass
class Download:
    url: str
    start_segment: str
    end_segment: str
    output_filename: str
    force_download: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
