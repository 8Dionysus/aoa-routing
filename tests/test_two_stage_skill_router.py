from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_router
import validate_two_stage_skill_router
from _wave9_router_lib import build_decision_packet, preselect


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


def load_fixture_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_outputs_include_two_stage_router_surfaces() -> None:
    outputs = build_fixture_outputs()

    assert "two_stage_skill_entrypoints.json" in outputs
    assert "two_stage_router_prompt_blocks.json" in outputs
    assert "two_stage_router_tool_schemas.json" in outputs
    assert "two_stage_router_examples.json" in outputs
    assert "two_stage_router_manifest.json" in outputs
    assert "two_stage_router_eval_cases.jsonl" in outputs
    assert outputs["two_stage_skill_entrypoints.json"]["stage_1"]["activation_policy"] == "never-activate"
    example = outputs["two_stage_router_examples.json"]["examples"][0]
    assert "confidence" in example["preselect_result"]
    assert "decision_reason" in example["decision_packet"]


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


def test_preselect_keeps_fallback_candidates_out_of_shortlist_for_empty_signal() -> None:
    policy = load_fixture_json(FIXTURES_ROOT / "aoa-routing" / "config" / "two_stage_router_policy.json")
    signals = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_skill_signals.json")
    bands = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_candidate_bands.json")

    preselected = preselect(
        "Make a small scoped repository update and summarize what changed.",
        signals,
        bands,
        policy,
    )

    assert preselected["shortlist"] == []
    assert preselected["confidence"] == "empty"
    assert preselected["fallback_candidates"] == [
        {
            "name": "aoa-change-protocol",
            "band": "change-validation",
            "manual_invocation_required": False,
            "project_overlay": False,
            "score": 0,
            "reasons": ["fallback"],
        }
    ]


def test_preselect_marks_close_scores_as_weak_and_stage_2_stays_no_skill() -> None:
    policy = load_fixture_json(FIXTURES_ROOT / "aoa-routing" / "config" / "two_stage_router_policy.json")
    signals = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_skill_signals.json")
    bands = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_candidate_bands.json")
    prompt = (
        "Before a bounded change with verification, scan the repo just far enough to identify "
        "the relevant files and stop once the key surfaces are clear."
    )

    preselected = preselect(prompt, signals, bands, policy)
    packet = build_decision_packet(prompt, preselected, FIXTURES_ROOT / "aoa-skills")

    assert [entry["name"] for entry in preselected["shortlist"]] == [
        "aoa-change-protocol",
        "aoa-context-scan",
    ]
    assert preselected["confidence"] == "weak"
    assert preselected["lead_gap"] == 1
    assert packet["suggested_decision"]["decision_mode"] == "no-skill"
    assert packet["decision_reason"] == "shortlist stayed below the precision-first activation thresholds"


def test_build_decision_packet_requires_manual_handle_for_strong_explicit_only_lead(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    generated_dir = skills_root / "generated"
    write_json(
        generated_dir / "tiny_router_skill_signals.json",
        {
            "skills": [
                {
                    "name": "aoa-approval-gate-check",
                    "band": "risk-ops-safety",
                    "invocation_mode": "explicit-only",
                    "manual_invocation_required": True,
                    "project_overlay": False,
                    "companions": [],
                }
            ]
        },
    )
    write_json(
        generated_dir / "skill_capsules.json",
        {
            "skills": [
                {
                    "name": "aoa-approval-gate-check",
                    "summary": "Classify whether a risky action may proceed.",
                    "trigger_boundary_short": "Use when the authority boundary is unclear.",
                    "verification_short": "Report whether the request may proceed.",
                }
            ]
        },
    )
    write_json(
        generated_dir / "local_adapter_manifest.json",
        {"skills": [{"name": "aoa-approval-gate-check", "allowlist_paths": ["scripts"]}]},
    )
    write_json(
        generated_dir / "context_retention_manifest.json",
        {"skills": [{"name": "aoa-approval-gate-check", "rehydration_hint": "re-read the approval notes"}]},
    )

    packet = build_decision_packet(
        "Classify whether a destructive request may proceed.",
        {
            "task": "Classify whether a destructive request may proceed.",
            "shortlist": [
                {
                    "name": "aoa-approval-gate-check",
                    "score": 12,
                    "reasons": ["positive:destructive"],
                }
            ],
            "confidence": "strong",
            "lead_score": 12,
            "lead_gap": 12,
            "fallback_candidates": [],
        },
        skills_root,
    )

    assert packet["confidence"] == "strong"
    assert packet["suggested_decision"]["decision_mode"] == "manual-invocation-required"
    assert packet["suggested_decision"]["skill"] == "aoa-approval-gate-check"


def test_validate_two_stage_outputs_reports_behavioral_mismatch(tmp_path: Path) -> None:
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

    eval_cases_path = generated_dir / "two_stage_router_eval_cases.jsonl"
    cases = [json.loads(line) for line in eval_cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases[0]["expected_top1"] = "aoa-context-scan"
    eval_cases_path.write_text("".join(json.dumps(row) + "\n" for row in cases), encoding="utf-8")

    issues = validate_two_stage_skill_router.validate_outputs(routing_root, FIXTURES_ROOT / "aoa-skills")

    assert any(
        location == "two_stage_router_eval_cases.jsonl:fixture-change:expected_top1"
        and "expected top1" in message
        for location, message in issues
    )


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
    assert payload["preselect"]["confidence"] == "strong"
    assert payload["decision_packet"]["suggested_decision"]["decision_mode"] == "activate-candidate"
    assert "fallback_candidates" in payload["decision_packet"]
    assert payload["decision_packet"]["decision_reason"] == "lead candidate cleared the precision-first activation thresholds"
