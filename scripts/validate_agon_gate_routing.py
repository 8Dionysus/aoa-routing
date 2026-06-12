#!/usr/bin/env python3
"""Compatibility launcher for the Agon gate-routing part validator."""

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
    / "validate_agon_gate_routing.py"
)


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
