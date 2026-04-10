from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import build_two_stage_skill_router
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
        FIXTURES_ROOT / "aoa-stats",
        FIXTURES_ROOT / "aoa-agents",
        FIXTURES_ROOT / "Agents-of-Abyss",
        FIXTURES_ROOT / "aoa-playbooks",
        FIXTURES_ROOT / "aoa-kag",
        FIXTURES_ROOT / "Tree-of-Sophia",
        FIXTURES_ROOT / "aoa-sdk",
        FIXTURES_ROOT / "Dionysus",
        FIXTURES_ROOT / "8Dionysus",
        FIXTURES_ROOT / "abyss-stack",
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
    assert outputs["two_stage_skill_entrypoints.json"]["schema_version"] == "aoa_routing_two_stage_skill_entrypoints_v2"
    assert outputs["two_stage_skill_entrypoints.json"]["schema_ref"] == "schemas/two-stage-skill-entrypoints.schema.json"
    assert outputs["two_stage_skill_entrypoints.json"]["owner_repo"] == "aoa-routing"
    assert outputs["two_stage_skill_entrypoints.json"]["surface_kind"] == "two_stage_skill_entrypoints"
    assert outputs["two_stage_skill_entrypoints.json"]["stage_1"]["activation_policy"] == "never-activate"
    assert outputs["two_stage_skill_entrypoints.json"]["stage_1"]["starter_ref"] == "skill-root"
    assert outputs["two_stage_skill_entrypoints.json"]["stage_1"]["max_stage_1_tokens"] == 1200
    assert outputs["two_stage_skill_entrypoints.json"]["stage_2"]["max_shortlist"] == 3
    assert outputs["two_stage_skill_entrypoints.json"]["tiny_model_handoff"] == {
        "starter_ref": "skill-root",
        "entry_surface": "generated/tiny_model_entrypoints.json",
        "handoff_name": "two-stage-skill-selection",
        "handoff_mode": "optional-adjacent",
        "activation_authority": "source-owned",
    }
    build_packet_tool = next(
        tool
        for tool in outputs["two_stage_router_tool_schemas.json"]["tools"]
        if tool["name"] == "build_skill_decision_packet"
    )
    assert build_packet_tool["input_schema"]["properties"]["shortlist_names"].get("minItems", 0) == 0
    assert build_packet_tool["input_schema"]["properties"]["shortlist_names"]["maxItems"] == 3
    preselect_tool = next(
        tool
        for tool in outputs["two_stage_router_tool_schemas.json"]["tools"]
        if tool["name"] == "preselect_skills"
    )
    assert preselect_tool["input_schema"]["properties"]["top_k"]["maximum"] == 3
    example = outputs["two_stage_router_examples.json"]["examples"][0]
    assert "confidence" in example["preselect_result"]
    assert "decision_reason" in example["decision_packet"]
    assert set(example["decision_packet"]["candidates"][0]) == {
        "name",
        "band",
        "score",
        "preselect_reasons",
        "invocation_mode",
        "manual_invocation_required",
        "activation_hint",
    }


def test_example_projection_keeps_runtime_decision_packet_rich_but_examples_redacted(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    generated_dir = skills_root / "generated"
    write_json(
        generated_dir / "tiny_router_skill_signals.json",
        {
            "skills": [
                {
                    "name": "aoa-source-of-truth-check",
                    "band": "decision-doc-authority",
                    "invocation_mode": "explicit-preferred",
                    "manual_invocation_required": False,
                    "project_overlay": False,
                    "companions": ["aoa-change-protocol"],
                }
            ]
        },
    )
    write_json(
        generated_dir / "skill_capsules.json",
        {
            "skills": [
                {
                    "name": "aoa-source-of-truth-check",
                    "summary": "Clarify which files are authoritative.",
                    "trigger_boundary_short": "Use when repository guidance overlaps or conflicts.",
                    "verification_short": "Report the authoritative files and entrypoints.",
                }
            ]
        },
    )
    write_json(
        generated_dir / "local_adapter_manifest.json",
        {"skills": [{"name": "aoa-source-of-truth-check", "allowlist_paths": ["docs"]}]},
    )
    write_json(
        generated_dir / "context_retention_manifest.json",
        {"skills": [{"name": "aoa-source-of-truth-check", "rehydration_hint": "re-open the canonical docs"}]},
    )

    packet = build_decision_packet(
        "Clarify the canonical docs and authority boundaries.",
        {
            "task": "Clarify the canonical docs and authority boundaries.",
            "shortlist": [
                {
                    "name": "aoa-source-of-truth-check",
                    "score": 12,
                    "reasons": ["positive:authority"],
                }
            ],
            "confidence": "strong",
            "lead_score": 12,
            "lead_gap": 12,
            "fallback_candidates": [],
        },
        skills_root,
    )

    projected = build_two_stage_skill_router.project_example_decision_packet(packet)

    assert "summary" in packet["candidates"][0]
    assert "allowlist_paths" in packet["candidates"][0]
    assert "summary" not in projected["candidates"][0]
    assert "allowlist_paths" not in projected["candidates"][0]
    assert "context_rehydration_hint" not in projected["candidates"][0]
    assert set(projected["candidates"][0]) == {
        "name",
        "band",
        "score",
        "preselect_reasons",
        "invocation_mode",
        "manual_invocation_required",
        "activation_hint",
    }


def test_build_outputs_anchor_eval_expectations_to_source_contracts() -> None:
    outputs = build_fixture_outputs()
    eval_cases = {
        entry["case_id"]: entry
        for entry in outputs["two_stage_router_eval_cases.jsonl"]
    }

    assert eval_cases["fixture-change"]["expected_band"] == "change-validation"
    assert eval_cases["fixture-change"]["stage_2_expectation"] == "activate-candidate"
    assert eval_cases["fixture-context"]["expected_band"] == "boundary-architecture"
    assert eval_cases["fixture-context"]["stage_2_expectation"] == "activate-candidate"


def test_expected_stage_2_mode_tracks_strong_manual_only_lead_when_no_explicit_expectation() -> None:
    stage_2_mode = build_two_stage_skill_router.expected_stage_2_mode(
        {
            "case_id": "manual-only-lead-without-explicit-stage-2",
            "expected_shortlist_excludes": ["aoa-quest-harvest"],
        },
        preselected={
            "shortlist": [{"name": "aoa-session-donor-harvest", "score": 11}],
            "confidence": "strong",
        },
        signal_by_name={
            "aoa-session-donor-harvest": {
                "manual_invocation_required": True,
            }
        },
    )

    assert stage_2_mode == "manual-invocation-required"


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


def test_validate_two_stage_outputs_rejects_missing_stage_2_activation_surface(tmp_path: Path) -> None:
    routing_root = tmp_path / "aoa-routing"
    shutil.copytree(FIXTURES_ROOT / "aoa-routing", routing_root)
    skills_root = tmp_path / "aoa-skills"
    shutil.copytree(FIXTURES_ROOT / "aoa-skills", skills_root)
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

    adapter_manifest_path = skills_root / "generated" / "local_adapter_manifest.json"
    adapter_manifest = load_fixture_json(adapter_manifest_path)
    adapter_manifest["skills"] = [
        entry
        for entry in adapter_manifest["skills"]
        if entry["name"] != "aoa-change-protocol"
    ]
    write_json(adapter_manifest_path, adapter_manifest)

    issues = validate_two_stage_skill_router.validate_outputs(routing_root, skills_root)

    assert (
        "local_adapter_manifest.json",
        "stage-2 surface coverage mismatch: missing ['aoa-change-protocol']",
    ) in issues


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


def test_preselect_caps_top_k_to_declared_stage_2_shortlist_limit() -> None:
    policy = load_fixture_json(FIXTURES_ROOT / "aoa-routing" / "config" / "two_stage_router_policy.json")
    signals = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_skill_signals.json")
    bands = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_candidate_bands.json")
    prompt = (
        "Use explicit verification, a bounded change workflow, a contract check, "
        "and a test-first slice while keeping the repo guidance authoritative."
    )

    preselected = preselect(prompt, signals, bands, policy, top_k=7)

    assert len(preselected["shortlist"]) <= 3


def test_preselect_clamps_non_positive_top_k_to_one() -> None:
    policy = load_fixture_json(FIXTURES_ROOT / "aoa-routing" / "config" / "two_stage_router_policy.json")
    signals = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_skill_signals.json")
    bands = load_fixture_json(FIXTURES_ROOT / "aoa-skills" / "generated" / "tiny_router_candidate_bands.json")
    prompt = (
        "Use explicit verification, a bounded change workflow, a contract check, "
        "and a test-first slice while keeping the repo guidance authoritative."
    )

    preselected = preselect(prompt, signals, bands, policy, top_k=-1)

    assert len(preselected["shortlist"]) == 1


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


def test_preselect_infers_top_band_from_shortlist_when_band_cues_absent() -> None:
    policy = {
        "defaults": {
            "top_k": 3,
            "max_band_candidates": 2,
            "min_activate_score": 6,
            "min_activate_gap": 3,
            "fallback_skills": [],
        },
        "scoring": {
            "band_score_weight": 3,
            "phrase_score_weight": 5,
            "token_score_weight": 2,
            "negative_phrase_penalty": 4,
            "negative_token_penalty": 2,
            "overlay_repo_family_bonus": 6,
            "companion_bonus": 1,
        },
        "repo_families": {},
    }
    signals = {
        "skills": [
            {
                "name": "aoa-approval-gate-check",
                "band": "risk-ops-safety",
                "manual_invocation_required": True,
                "project_overlay": False,
                "positive_cues": ["approval gate"],
                "negative_cues": [],
                "cue_tokens": ["approval", "gate", "destructive"],
                "negative_tokens": [],
                "primary_positive_prompt": "",
                "primary_negative_prompt": "",
                "primary_defer_prompt": "",
            }
        ]
    }
    bands = {
        "bands": [
            {
                "id": "risk-ops-safety",
                "summary": "Risk review and operational safety.",
                "cues": ["runtime bringup"],
            }
        ]
    }

    preselected = preselect(
        "Use $aoa-approval-gate-check before this destructive action proceeds.",
        signals,
        bands,
        policy,
    )

    assert [entry["name"] for entry in preselected["shortlist"]] == ["aoa-approval-gate-check"]
    assert preselected["top_bands"][0]["id"] == "risk-ops-safety"
    assert preselected["top_bands"][0]["reasons"] == ["shortlist:aoa-approval-gate-check"]


def test_preselect_prefers_positive_base_skill_over_repo_family_only_overlay(tmp_path: Path) -> None:
    policy = {
        "defaults": {
            "top_k": 3,
            "max_band_candidates": 2,
            "min_activate_score": 6,
            "min_activate_gap": 3,
            "fallback_skills": [],
        },
        "scoring": {
            "band_score_weight": 3,
            "phrase_score_weight": 5,
            "token_score_weight": 2,
            "negative_phrase_penalty": 4,
            "negative_token_penalty": 2,
            "overlay_repo_family_bonus": 6,
            "companion_bonus": 1,
        },
        "repo_families": {
            "atm10": {
                "tokens": ["atm10"],
                "project_skill_prefixes": ["atm10-"],
            }
        },
    }
    signals = {
        "skills": [
            {
                "name": "aoa-source-of-truth-check",
                "band": "decision-doc-authority",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": False,
                "companions": [],
                "positive_cues": [],
                "negative_cues": [],
                "cue_tokens": [],
                "negative_tokens": [],
                "primary_positive_prompt": "which files authoritative",
                "primary_negative_prompt": "which files authoritative",
                "primary_defer_prompt": "which files authoritative",
            },
            {
                "name": "atm10-change-protocol",
                "band": "change-validation",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": True,
                "companions": [],
                "positive_cues": [],
                "negative_cues": [],
                "cue_tokens": [],
                "negative_tokens": [],
                "primary_positive_prompt": "repo relative atm10 paths",
                "primary_negative_prompt": "",
                "primary_defer_prompt": "",
            },
        ]
    }
    bands = {
        "bands": [
            {
                "id": "decision-doc-authority",
                "summary": "Canonical docs and authority maps.",
                "cues": ["decision record"],
            },
            {
                "id": "change-validation",
                "summary": "Scoped changes and verification.",
                "cues": ["bounded change"],
            },
        ]
    }
    prompt = (
        "This repo has three conflicting architecture guides and two outdated runbooks. "
        "Identify which files are authoritative and shorten the entrypoints into a link-driven map."
    )

    preselected = preselect(
        prompt,
        signals,
        bands,
        policy,
        repo_family="atm10",
    )

    assert [entry["name"] for entry in preselected["shortlist"]] == ["aoa-source-of-truth-check"]
    assert preselected["confidence"] == "strong"
    assert preselected["top_bands"][0]["id"] == "decision-doc-authority"

    skills_root = tmp_path / "aoa-skills"
    generated_dir = skills_root / "generated"
    write_json(generated_dir / "tiny_router_skill_signals.json", signals)
    write_json(
        generated_dir / "skill_capsules.json",
        {
            "skills": [
                {
                    "name": "aoa-source-of-truth-check",
                    "summary": "Clarify which files are authoritative.",
                    "trigger_boundary_short": "Use when repository guidance overlaps or conflicts.",
                    "verification_short": "Report the authoritative files and entrypoints.",
                }
            ]
        },
    )
    write_json(
        generated_dir / "local_adapter_manifest.json",
        {"skills": [{"name": "aoa-source-of-truth-check", "allowlist_paths": ["docs"]}]},
    )
    write_json(
        generated_dir / "context_retention_manifest.json",
        {"skills": [{"name": "aoa-source-of-truth-check", "rehydration_hint": "re-open the canonical docs"}]},
    )

    packet = build_decision_packet(prompt, preselected, skills_root)

    assert packet["suggested_decision"]["decision_mode"] == "activate-candidate"
    assert packet["suggested_decision"]["skill"] == "aoa-source-of-truth-check"


def test_preselect_uses_defer_prompt_overlap_to_exclude_overlay_without_family() -> None:
    policy = {
        "defaults": {
            "top_k": 3,
            "max_band_candidates": 2,
            "min_activate_score": 6,
            "min_activate_gap": 3,
            "fallback_skills": [],
        },
        "scoring": {
            "band_score_weight": 3,
            "phrase_score_weight": 5,
            "token_score_weight": 2,
            "negative_phrase_penalty": 4,
            "negative_token_penalty": 2,
            "overlay_repo_family_bonus": 6,
            "companion_bonus": 1,
        },
        "repo_families": {
            "atm10": {
                "tokens": ["atm10"],
                "project_skill_prefixes": ["atm10-"],
            }
        },
    }
    signals = {
        "skills": [
            {
                "name": "aoa-change-protocol",
                "band": "change-validation",
                "manual_invocation_required": False,
                "project_overlay": False,
                "positive_cues": ["bounded change"],
                "negative_cues": [],
                "cue_tokens": ["apply", "change", "service"],
                "negative_tokens": [],
                "primary_positive_prompt": "apply bounded change",
                "primary_negative_prompt": "",
                "primary_defer_prompt": "",
            },
            {
                "name": "atm10-change-protocol",
                "band": "change-validation",
                "manual_invocation_required": False,
                "project_overlay": True,
                "positive_cues": ["bounded change"],
                "negative_cues": [],
                "cue_tokens": ["apply", "change", "service"],
                "negative_tokens": [],
                "primary_positive_prompt": "apply atm10 repo relative change",
                "primary_negative_prompt": "",
                "primary_defer_prompt": (
                    "Apply the bounded change workflow in this generic service repo. "
                    "There is no atm10 overlay or project-specific path layer here."
                ),
            },
        ]
    }
    bands = {
        "bands": [
            {
                "id": "change-validation",
                "summary": "Scoped changes and verification.",
                "cues": ["bounded change"],
            }
        ]
    }
    prompt = (
        "Apply the bounded change workflow in this generic service repo. "
        "There is no atm10 overlay or project-specific path layer here."
    )

    preselected = preselect(prompt, signals, bands, policy)

    assert [entry["name"] for entry in preselected["shortlist"]] == ["aoa-change-protocol"]
    assert preselected["confidence"] == "strong"


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


def test_build_decision_packet_rejects_shortlist_beyond_declared_limit(tmp_path: Path) -> None:
    skills_root = tmp_path / "aoa-skills"
    generated_dir = skills_root / "generated"
    signals = {
        "skills": [
            {
                "name": "skill-one",
                "band": "change-validation",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": False,
                "companions": [],
            },
            {
                "name": "skill-two",
                "band": "change-validation",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": False,
                "companions": [],
            },
            {
                "name": "skill-three",
                "band": "change-validation",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": False,
                "companions": [],
            },
            {
                "name": "skill-four",
                "band": "change-validation",
                "invocation_mode": "explicit-preferred",
                "manual_invocation_required": False,
                "project_overlay": False,
                "companions": [],
            },
        ]
    }
    capsules = {
        "skills": [
            {
                "name": name,
                "summary": f"{name} summary",
                "trigger_boundary_short": f"{name} trigger",
                "verification_short": f"{name} verification",
            }
            for name in ["skill-one", "skill-two", "skill-three", "skill-four"]
        ]
    }
    adapters = {
        "skills": [
            {"name": name, "allowlist_paths": [".agents/skills"]}
            for name in ["skill-one", "skill-two", "skill-three", "skill-four"]
        ]
    }
    retention = {
        "skills": [
            {"name": name, "rehydration_hint": f"reload {name}"}
            for name in ["skill-one", "skill-two", "skill-three", "skill-four"]
        ]
    }
    write_json(generated_dir / "tiny_router_skill_signals.json", signals)
    write_json(generated_dir / "skill_capsules.json", capsules)
    write_json(generated_dir / "local_adapter_manifest.json", adapters)
    write_json(generated_dir / "context_retention_manifest.json", retention)

    try:
        build_decision_packet(
            "Route a bounded change",
            {
                "task": "Route a bounded change",
                "shortlist": [{"name": name} for name in ["skill-one", "skill-two", "skill-three", "skill-four"]],
                "confidence": "strong",
                "lead_score": 12,
                "lead_gap": 6,
                "fallback_candidates": [],
            },
            skills_root,
            max_shortlist=3,
        )
    except ValueError as exc:
        assert "max_shortlist=3" in str(exc)
    else:
        raise AssertionError("expected build_decision_packet to reject an oversized shortlist")


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


def test_validate_two_stage_outputs_rejects_activate_candidate_defer_case_without_shortlist_target(
    tmp_path: Path,
) -> None:
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
    cases.append(
        {
            "case_id": "tiny-defer-aoa-context-scan",
            "prompt": "Make a bounded repository change with a clear verification step and a final report.",
            "repo_family_hint": None,
            "expected_shortlist_includes": [],
            "expected_shortlist_excludes": ["aoa-context-scan"],
            "expected_top1": None,
            "expected_top1_not": "aoa-context-scan",
            "expected_band": "change-validation",
            "stage_2_expectation": "activate-candidate",
        }
    )
    eval_cases_path.write_text("".join(json.dumps(row) + "\n" for row in cases), encoding="utf-8")

    issues = validate_two_stage_skill_router.validate_outputs(routing_root, FIXTURES_ROOT / "aoa-skills")

    assert (
        "two_stage_router_eval_cases.jsonl",
        "activate-candidate defer cases must keep expected_shortlist_includes",
    ) in issues


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


def test_live_workspace_two_stage_outputs_are_normalized_v2() -> None:
    generated_root = Path(__file__).resolve().parents[1] / "generated"
    entrypoints = load_fixture_json(generated_root / "two_stage_skill_entrypoints.json")
    prompt_blocks = load_fixture_json(generated_root / "two_stage_router_prompt_blocks.json")
    tool_schemas = load_fixture_json(generated_root / "two_stage_router_tool_schemas.json")
    examples = load_fixture_json(generated_root / "two_stage_router_examples.json")
    manifest = load_fixture_json(generated_root / "two_stage_router_manifest.json")

    assert entrypoints["schema_version"] == "aoa_routing_two_stage_skill_entrypoints_v2"
    assert entrypoints["schema_ref"] == "schemas/two-stage-skill-entrypoints.schema.json"
    assert entrypoints["owner_repo"] == "aoa-routing"
    assert entrypoints["surface_kind"] == "two_stage_skill_entrypoints"
    assert entrypoints["tiny_model_handoff"]["starter_ref"] == "skill-root"
    assert entrypoints["tiny_model_handoff"]["entry_surface"] == "generated/tiny_model_entrypoints.json"
    assert entrypoints["tiny_model_handoff"]["handoff_name"] == "two-stage-skill-selection"
    assert entrypoints["tiny_model_handoff"]["handoff_mode"] == "optional-adjacent"
    assert entrypoints["tiny_model_handoff"]["activation_authority"] == "source-owned"
    assert prompt_blocks["schema_version"] == "aoa_routing_two_stage_router_prompt_blocks_v2"
    assert prompt_blocks["schema_ref"] == "schemas/two-stage-router-prompt-blocks.schema.json"
    assert prompt_blocks["owner_repo"] == "aoa-routing"
    assert prompt_blocks["surface_kind"] == "two_stage_router_prompt_blocks"
    assert prompt_blocks["low_context_boundary"] == {
        "wording_scope": "routing-owned",
        "source_payload_copying": "forbidden",
        "stage_1_source_refs": [
            "aoa-skills:generated/tiny_router_capsules.min.json",
            "aoa-skills:generated/tiny_router_candidate_bands.json",
            "aoa-skills:generated/tiny_router_skill_signals.json",
        ],
        "stage_2_source_refs": [
            "aoa-skills:generated/skill_capsules.json",
            "aoa-skills:generated/local_adapter_manifest.json",
            "aoa-skills:generated/context_retention_manifest.json",
        ],
        "forbidden_source_payload_fields": [
            "summary",
            "trigger_boundary_short",
            "verification_short",
            "skill_path",
            "allowlist_paths",
            "rehydration_hint",
            "context_rehydration_hint",
            "companions",
        ],
    }
    for field_name in prompt_blocks["low_context_boundary"]["forbidden_source_payload_fields"]:
        assert field_name not in prompt_blocks["tiny_preselector_system"]
        assert field_name not in prompt_blocks["main_model_decision_system"]
    assert tool_schemas["schema_version"] == "aoa_routing_two_stage_router_tool_schemas_v2"
    assert tool_schemas["schema_ref"] == "schemas/two-stage-router-tool-schemas.schema.json"
    assert tool_schemas["owner_repo"] == "aoa-routing"
    assert tool_schemas["surface_kind"] == "two_stage_router_tool_schemas"
    assert tool_schemas["low_context_boundary"] == prompt_blocks["low_context_boundary"]
    expected_tool_properties = {
        "preselect_skills": {"task", "repo_family", "top_k"},
        "build_skill_decision_packet": {"task", "shortlist_names"},
        "route_skill_task": {"task", "repo_family", "top_k"},
    }
    for tool in tool_schemas["tools"]:
        for field_name in tool_schemas["low_context_boundary"]["forbidden_source_payload_fields"]:
            assert field_name not in tool["description"]
        assert set(tool["input_schema"]["properties"]) == expected_tool_properties[tool["name"]]
    assert examples["schema_version"] == "aoa_routing_two_stage_router_examples_v2"
    assert examples["schema_ref"] == "schemas/two-stage-router-examples.schema.json"
    assert examples["owner_repo"] == "aoa-routing"
    assert examples["surface_kind"] == "two_stage_router_examples"
    example_candidate = examples["examples"][0]["decision_packet"]["candidates"][0]
    assert "summary" not in example_candidate
    assert "trigger_boundary_short" not in example_candidate
    assert "verification_short" not in example_candidate
    assert "allowlist_paths" not in example_candidate
    assert "context_rehydration_hint" not in example_candidate
    assert "companions" not in example_candidate
    assert manifest["schema_version"] == "aoa_routing_two_stage_router_manifest_v2"
    assert manifest["schema_ref"] == "schemas/two-stage-router-manifest.schema.json"
    assert manifest["owner_repo"] == "aoa-routing"
    assert manifest["surface_kind"] == "two_stage_router_manifest"
