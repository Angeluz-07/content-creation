from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum
from datetime import datetime, timezone


@dataclass
class TextSegment:
    text: str
    start: str
    end: str
