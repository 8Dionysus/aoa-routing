#!/usr/bin/env python3
"""Compatibility launcher for the active two-stage source-home validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SCRIPT = (
    REPO_ROOT
    / "routing"
    / "two-stage-skill-selection"
    / "scripts"
    / "validate_two_stage_skill_router.py"
)


def _load_active() -> ModuleType:
    active_dir = str(ACTIVE_SCRIPT.parent)
    if active_dir not in sys.path:
        sys.path.insert(0, active_dir)
    spec = importlib.util.spec_from_file_location("_aoa_routing_two_stage_validator", ACTIVE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ACTIVE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ACTIVE = _load_active()

validate_outputs = _ACTIVE.validate_outputs
main = _ACTIVE.main


if __name__ == "__main__":
    raise SystemExit(main())
