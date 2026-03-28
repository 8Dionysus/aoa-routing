from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "can",
    "code",
    "config",
    "do",
    "docs",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "local",
    "not",
    "of",
    "on",
    "or",
    "repo",
    "repository",
    "task",
    "the",
    "to",
    "use",
    "when",
    "with",
    "work",
    "workflow",
    "you",
    "your",
    "already",
    "only",
    "than",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(text: str) -> str:
    normalized = text.lower()
    normalized = normalized.replace("aoa-", "aoa ")
    normalized = normalized.replace("atm10-", "atm10 ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def tokenize(text: str) -> list[str]:
    return [token for token in normalize(text).split() if len(token) > 2 and token not in STOPWORDS]


def phrase_hits(task_normalized: str, phrases: list[str]) -> list[str]:
    hits: list[str] = []
    for phrase in phrases:
        normalized_phrase = normalize(phrase)
        if normalized_phrase and normalized_phrase in task_normalized:
            hits.append(phrase)
    return hits


def token_hits(task_tokens: set[str], tokens: list[str]) -> list[str]:
    hits = [token for token in tokens if token in task_tokens]
    return sorted(set(hits))


def resolve_repo_family(task_normalized: str, repo_family: str | None, policy: dict[str, Any]) -> str | None:
    if repo_family:
        return repo_family
    for family_name, family_entry in (policy.get("repo_families") or {}).items():
        family_tokens = family_entry.get("tokens", [])
        if any(normalize(token) in task_normalized for token in family_tokens):
            return family_name
    return None


def score_band(
    task_normalized: str,
    task_tokens: set[str],
    band: dict[str, Any],
    scoring: dict[str, Any],
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    matched_phrases = phrase_hits(task_normalized, band.get("cues", []))
    matched_tokens = token_hits(task_tokens, tokenize(" ".join(band.get("cues", []))))
    if matched_phrases:
        score += len(matched_phrases) * scoring["phrase_score_weight"]
        reasons.extend(f"cue:{phrase}" for phrase in matched_phrases[:3])
    if matched_tokens:
        score += len(matched_tokens) * scoring["token_score_weight"]
        reasons.extend(f"token:{token}" for token in matched_tokens[:3])
    if normalize(band.get("summary", "")) in task_normalized:
        score += scoring["band_score_weight"]
        reasons.append("summary-match")
    return score, reasons


def score_skill(
    task_normalized: str,
    task_tokens: set[str],
    signal: dict[str, Any],
    top_band_ids: set[str],
    policy: dict[str, Any],
    resolved_repo_family: str | None,
) -> tuple[int, list[str]]:
    scoring = policy["scoring"]
    score = 0
    reasons: list[str] = []

    if signal["band"] in top_band_ids:
        score += scoring["band_score_weight"]
        reasons.append(f"band:{signal['band']}")

    positive_phrases = phrase_hits(task_normalized, signal.get("positive_cues", []))
    negative_phrases = phrase_hits(task_normalized, signal.get("negative_cues", []))
    positive_tokens = token_hits(task_tokens, signal.get("cue_tokens", []))
    negative_tokens = token_hits(task_tokens, signal.get("negative_tokens", []))

    if positive_phrases:
        score += len(positive_phrases) * scoring["phrase_score_weight"]
        reasons.extend(f"positive:{phrase}" for phrase in positive_phrases[:3])
    if positive_tokens:
        score += len(positive_tokens) * scoring["token_score_weight"]
        reasons.extend(f"token:{token}" for token in positive_tokens[:3])
    if negative_phrases:
        score -= len(negative_phrases) * scoring["negative_phrase_penalty"]
        reasons.extend(f"negative:{phrase}" for phrase in negative_phrases[:2])
    if negative_tokens:
        score -= len(negative_tokens) * scoring["negative_token_penalty"]
        reasons.extend(f"negative-token:{token}" for token in negative_tokens[:2])

    if resolved_repo_family and signal.get("project_overlay"):
        family_entry = (policy.get("repo_families") or {}).get(resolved_repo_family, {})
        prefixes = family_entry.get("project_skill_prefixes", [])
        if any(signal["name"].startswith(prefix) for prefix in prefixes):
            score += scoring["overlay_repo_family_bonus"]
            reasons.append(f"overlay-family:{resolved_repo_family}")

    return score, reasons


def preselect(
    task: str,
    signals_doc: dict[str, Any],
    bands_doc: dict[str, Any],
    policy: dict[str, Any],
    *,
    top_k: int | None = None,
    repo_family: str | None = None,
) -> dict[str, Any]:
    task_normalized = normalize(task)
    task_tokens = set(tokenize(task))
    scoring = policy["scoring"]
    top_k = top_k or policy["defaults"]["top_k"]
    resolved_repo_family = resolve_repo_family(task_normalized, repo_family, policy)

    scored_bands: list[dict[str, Any]] = []
    for band in bands_doc.get("bands", []):
        score, reasons = score_band(task_normalized, task_tokens, band, scoring)
        scored_bands.append(
            {
                "id": band["id"],
                "score": score,
                "reasons": reasons,
            }
        )
    scored_bands.sort(key=lambda entry: (-entry["score"], entry["id"]))
    top_bands = scored_bands[: policy["defaults"]["max_band_candidates"]]
    top_band_ids = {entry["id"] for entry in top_bands if entry["score"] > 0} or {
        entry["id"] for entry in top_bands
    }

    scored_skills: list[dict[str, Any]] = []
    signal_by_name = {entry["name"]: entry for entry in signals_doc.get("skills", [])}
    for signal in signals_doc.get("skills", []):
        score, reasons = score_skill(
            task_normalized,
            task_tokens,
            signal,
            top_band_ids,
            policy,
            resolved_repo_family,
        )
        scored_skills.append(
            {
                "name": signal["name"],
                "band": signal["band"],
                "manual_invocation_required": signal["manual_invocation_required"],
                "project_overlay": signal["project_overlay"],
                "score": score,
                "reasons": reasons[:6],
            }
        )

    scored_skills.sort(key=lambda entry: (-entry["score"], entry["name"]))
    shortlist = [entry for entry in scored_skills if entry["score"] > 0][:top_k]
    if not shortlist:
        for fallback_name in policy["defaults"].get("fallback_skills", []):
            signal = signal_by_name.get(fallback_name)
            if signal is None:
                continue
            shortlist.append(
                {
                    "name": signal["name"],
                    "band": signal["band"],
                    "manual_invocation_required": signal["manual_invocation_required"],
                    "project_overlay": signal["project_overlay"],
                    "score": 0,
                    "reasons": ["fallback"],
                }
            )
            if len(shortlist) >= top_k:
                break

    return {
        "task": task,
        "repo_family": resolved_repo_family,
        "top_bands": top_bands,
        "shortlist": shortlist,
    }


def build_decision_packet(
    task: str,
    shortlist_names: list[str],
    skills_root: Path,
) -> dict[str, Any]:
    generated_dir = skills_root / "generated"
    signals = load_json(generated_dir / "tiny_router_skill_signals.json")
    capsules = load_json(generated_dir / "skill_capsules.json")
    local_adapter = load_json(generated_dir / "local_adapter_manifest.json")
    context_retention = load_json(generated_dir / "context_retention_manifest.json")

    signal_by_name = {entry["name"]: entry for entry in signals.get("skills", [])}
    capsule_by_name = {entry["name"]: entry for entry in capsules.get("skills", [])}
    adapter_by_name = {entry["name"]: entry for entry in local_adapter.get("skills", [])}
    retention_by_name = {entry["name"]: entry for entry in context_retention.get("skills", [])}

    candidates: list[dict[str, Any]] = []
    for name in shortlist_names:
        signal = signal_by_name.get(name)
        capsule = capsule_by_name.get(name)
        adapter = adapter_by_name.get(name)
        retention = retention_by_name.get(name)
        if signal is None or capsule is None or adapter is None or retention is None:
            continue
        candidates.append(
            {
                "name": name,
                "band": signal["band"],
                "summary": capsule["summary"],
                "trigger_boundary_short": capsule["trigger_boundary_short"],
                "verification_short": capsule["verification_short"],
                "invocation_mode": signal["invocation_mode"],
                "manual_invocation_required": signal["manual_invocation_required"],
                "activation_hint": f"${name}" if signal["manual_invocation_required"] else "implicit-ok",
                "allowlist_paths": adapter["allowlist_paths"],
                "context_rehydration_hint": retention["rehydration_hint"],
                "companions": signal["companions"],
            }
        )

    if not candidates:
        suggested_decision = {
            "decision_mode": "no-skill",
            "skill": None,
            "next_step": "continue without a skill or use flat routing",
        }
    else:
        lead = candidates[0]
        if lead["manual_invocation_required"]:
            suggested_decision = {
                "decision_mode": "manual-invocation-required",
                "skill": lead["name"],
                "next_step": f"require explicit handle ${lead['name']} before activation",
            }
        else:
            suggested_decision = {
                "decision_mode": "activate-candidate",
                "skill": lead["name"],
                "next_step": f"inspect or activate {lead['name']} using the skill runtime seam",
            }

    return {
        "task": task,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "suggested_decision": suggested_decision,
        "stage_2_checklist": [
            "choose at most one skill to activate",
            "if the lead candidate is explicit-only, require an explicit handle",
            "do not load full skill bodies for non-shortlisted skills",
            "continue without a skill when the shortlist is weak",
        ],
    }
