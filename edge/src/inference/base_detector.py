"""Abstract base class for all edge detectors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Detection:
    event_type: str  # 'fall'|'bed-exit'|'inactivity'|'unsafe-transfer'
    confidence_score: float  # 0.0-1.0
    bounding_box: tuple[int, int, int, int] | None = None  # x, y, w, h
    metadata: dict = field(default_factory=dict)


class BaseDetector(ABC):
    @abstractmethod
    def load_model(self, model_path: str) -> None: ...

    @abstractmethod
    def detect(self, input_data) -> list[Detection]: ...
