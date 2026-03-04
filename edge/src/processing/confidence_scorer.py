"""Score a detection and optionally apply the fusion confidence boost."""

from src.inference.base_detector import Detection


class ConfidenceScorer:
    def __init__(self, config) -> None:
        self.thresholds = config.inference.confidence_thresholds
        self.fusion_boost = config.fusion.confidence_boost / 100.0

    def score(self, detection: Detection, source: str, fused: bool) -> Detection:
        """Apply scoring to a detection.

        If the detection was fused across multiple sensor modalities the
        configured boost is added (capped at 1.0).  Source and fusion state
        are recorded in the detection metadata.

        Args:
            detection: The raw detection to score.
            source: Sensor source label ('ai-vision' or 'ai-sensor').
            fused: Whether fusion was successful.

        Returns:
            The same Detection instance with updated confidence_score and
            metadata.
        """
        score = detection.confidence_score
        if fused:
            score = min(1.0, score + self.fusion_boost)
        detection.confidence_score = score
        detection.metadata["source"] = source
        detection.metadata["fused"] = fused
        return detection
