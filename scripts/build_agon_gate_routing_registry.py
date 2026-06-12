#!/usr/bin/env python3
"""Compatibility launcher for the Agon gate-routing part builder."""

from __future__ import annotations

import runpy
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "mechanics"
    / "agon"
    / "parts"
    / "gate-routing"
    / "scripts"
    / "build_agon_gate_routing_registry.py"
)


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
