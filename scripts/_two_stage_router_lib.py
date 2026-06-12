"""Compatibility import shim for the active two-stage router library."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_LIB = (
    REPO_ROOT
    / "routing"
    / "two-stage-skill-selection"
    / "scripts"
    / "two_stage_router_lib.py"
)


def _load_active() -> ModuleType:
    active_dir = str(ACTIVE_LIB.parent)
    if active_dir not in sys.path:
        sys.path.insert(0, active_dir)
    spec = importlib.util.spec_from_file_location("_aoa_routing_two_stage_router_lib", ACTIVE_LIB)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ACTIVE_LIB}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ACTIVE = _load_active()

build_decision_packet = _ACTIVE.build_decision_packet
coerce_preselect_result = _ACTIVE.coerce_preselect_result
load_json = _ACTIVE.load_json
load_jsonl = _ACTIVE.load_jsonl
normalize = _ACTIVE.normalize
preselect = _ACTIVE.preselect
resolve_stage_2_shortlist_limit = _ACTIVE.resolve_stage_2_shortlist_limit
