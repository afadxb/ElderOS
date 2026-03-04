"""Tests for the confidence scorer."""

import pytest
from unittest.mock import MagicMock

from src.inference.base_detector import Detection
from src.processing.confidence_scorer import ConfidenceScorer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(boost: int = 15):
    config = MagicMock()
    config.inference.confidence_thresholds = {"high_min": 85, "medium_min": 60, "low_min": 30}
    config.fusion.confidence_boost = boost
    return config


def _score_and_label(confidence: float, fused: bool = False, boost: int = 15) -> tuple[float, str]:
    """Score a detection and return (final_score, label) using the same
    thresholds as EventProcessor._build_event."""
    scorer = ConfidenceScorer(_make_config(boost))
    det = Detection(event_type="fall", confidence_score=confidence, metadata={})
    scored = scorer.score(det, source="ai-vision", fused=fused)

    score = scored.confidence_score
    if score >= 0.85:
        label = "high"
    elif score >= 0.60:
        label = "medium"
    else:
        label = "low"
    return score, label


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_high_confidence():
    """A score >= 0.85 maps to the 'high' confidence label."""
    score, label = _score_and_label(0.92)
    assert score >= 0.85
    assert label == "high"


def test_medium_confidence():
    """A score between 0.60 and 0.84 maps to the 'medium' confidence label."""
    score, label = _score_and_label(0.72)
    assert 0.60 <= score < 0.85
    assert label == "medium"


def test_low_confidence():
    """A score between 0.30 and 0.59 maps to the 'low' confidence label."""
    score, label = _score_and_label(0.45)
    assert score < 0.60
    assert label == "low"


def test_fusion_boost_applied():
    """When fused=True the confidence boost is added to the raw score."""
    scorer = ConfidenceScorer(_make_config(boost=15))
    det = Detection(event_type="fall", confidence_score=0.70, metadata={})
    scored = scorer.score(det, source="ai-vision", fused=True)

    # 0.70 + 0.15 = 0.85
    assert scored.confidence_score == pytest.approx(0.85, abs=0.01)
    assert scored.metadata["fused"] is True


def test_fusion_boost_capped():
    """Fusion boost should not push the score above 1.0."""
    scorer = ConfidenceScorer(_make_config(boost=20))
    det = Detection(event_type="fall", confidence_score=0.95, metadata={})
    scored = scorer.score(det, source="ai-vision", fused=True)

    assert scored.confidence_score == 1.0


def test_source_recorded_in_metadata():
    """The sensor source label is recorded in detection metadata."""
    scorer = ConfidenceScorer(_make_config())
    det = Detection(event_type="fall", confidence_score=0.80, metadata={})
    scored = scorer.score(det, source="ai-sensor", fused=False)

    assert scored.metadata["source"] == "ai-sensor"
    assert scored.metadata["fused"] is False
