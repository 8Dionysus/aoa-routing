#!/usr/bin/env python3
"""Compatibility launcher for the active two-stage routing CLI."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SCRIPT = (
    REPO_ROOT
    / "routing"
    / "two-stage-skill-selection"
    / "scripts"
    / "two_stage_skill_router.py"
)


if __name__ == "__main__":
    active_dir = str(ACTIVE_SCRIPT.parent)
    if active_dir not in sys.path:
        sys.path.insert(0, active_dir)
    runpy.run_path(str(ACTIVE_SCRIPT), run_name="__main__")
