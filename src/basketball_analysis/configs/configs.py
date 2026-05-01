"""Default paths for models, stubs, assets, and outputs.

All paths are resolved relative to the repository root (parent of ``src/``), so the
pipeline behaves the same regardless of the current working directory.
"""

import os
from pathlib import Path


def _repo_root() -> Path:
    root = os.environ.get("BASKETBALL_ANALYSIS_ROOT")
    if root:
        return Path(root).resolve()
    # This file: src/basketball_analysis/configs/configs.py
    return Path(__file__).resolve().parent.parent.parent.parent


_DATA = _repo_root() / "data"

STUBS_DEFAULT_PATH = str(_DATA / "stubs")
PLAYER_DETECTOR_PATH = str(_DATA / "models" / "player_detector.pt")
BALL_DETECTOR_PATH = str(_DATA / "models" / "ball_detector_model.pt")
COURT_KEYPOINT_DETECTOR_PATH = str(_DATA / "models" / "court_keypoint_detector.pt")
OUTPUT_VIDEO_PATH = str(_DATA / "output" / "output_video.avi")
COURT_IMAGE_PATH = str(_DATA / "assets" / "basketball_court.png")
