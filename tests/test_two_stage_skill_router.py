from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_router
import validate_two_stage_skill_router


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


def build_fixture_outputs() -> dict[str, dict[str, object] | list[dict[str, object]]]:
    return build_router.build_outputs(
        FIXTURES_ROOT / "aoa-techniques",
        FIXTURES_ROOT / "aoa-skills",
        FIXTURES_ROOT / "aoa-evals",
        FIXTURES_ROOT / "aoa-memo",
        FIXTURES_ROOT / "aoa-agents",
        FIXTURES_ROOT / "Agents-of-Abyss",
        FIXTURES_ROOT / "aoa-playbooks",
        FIXTURES_ROOT / "aoa-kag",
        FIXTURES_ROOT / "Tree-of-Sophia",
    )


def test_build_outputs_include_two_stage_router_surfaces() -> None:
    outputs = build_fixture_outputs()

    assert "two_stage_skill_entrypoints.json" in outputs
    assert "two_stage_router_prompt_blocks.json" in outputs
    assert "two_stage_router_tool_schemas.json" in outputs
    assert "two_stage_router_examples.json" in outputs
    assert "two_stage_router_manifest.json" in outputs
    assert "two_stage_router_eval_cases.jsonl" in outputs
    assert outputs["two_stage_skill_entrypoints.json"]["stage_1"]["activation_policy"] == "never-activate"


def test_validate_two_stage_outputs_accepts_fixture_build(tmp_path: Path) -> None:
    routing_root = tmp_path / "aoa-routing"
    shutil.copytree(FIXTURES_ROOT / "aoa-routing", routing_root)
    generated_dir = routing_root / "generated"
    outputs = build_fixture_outputs()
    for filename, payload in outputs.items():
        path = generated_dir / filename
        if filename.endswith(".jsonl"):
            path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in payload),
                encoding="utf-8",
            )
        else:
            write_json(path, payload)

    issues = validate_two_stage_skill_router.validate_outputs(routing_root, FIXTURES_ROOT / "aoa-skills")
    assert issues == []


def test_two_stage_skill_router_cli_routes_fixture_task(tmp_path: Path) -> None:
    routing_root = tmp_path / "aoa-routing"
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-routing", routing_root)
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
    outputs = build_fixture_outputs()
    for filename, payload in outputs.items():
        path = routing_root / "generated" / filename
        if filename.endswith(".jsonl"):
            path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in payload),
                encoding="utf-8",
            )
        else:
            write_json(path, payload)

    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "two_stage_skill_router.py"),
            "route",
            "--routing-root",
            str(routing_root),
            "--skills-root",
            str(skills_root),
            "--task",
            "Make a bounded repository change with a clear verification step and a final report.",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["preselect"]["shortlist"][0]["name"] == "aoa-change-protocol"
    assert payload["decision_packet"]["suggested_decision"]["decision_mode"] == "activate-candidate"
