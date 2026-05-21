from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum
from datetime import datetime, timezone


@dataclass
class DownloadParams:
    url: str
    start_segment: str
    end_segment: str
    output_filename: str
    force_download: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ShortProductionParams:
    input_filename: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    debug_video_frame: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Task:
    """
    Entity to track asychronous tasks
    """

    target_entity_id: str  # linked domain model
    target_entity_type: str
    status: TaskStatus = TaskStatus.PENDING
    payload: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Event:
    """
    Entity to track events during the workflow of asychronous task.
    """

    task_id: str
    event_type: str
    payload: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))
