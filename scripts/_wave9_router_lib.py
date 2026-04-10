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
    "anything",
    "changed",
    "checked",
    "clear",
    "identify",
    "make",
    "map",
    "only",
    "than",
    "what",
}
NEGATION_PREFIXES = ("no", "not", "without")


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


def is_negated_phrase(task_normalized: str, normalized_phrase: str) -> bool:
    if not normalized_phrase:
        return False
    escaped_phrase = re.escape(normalized_phrase)
    patterns = [
        rf"\b(?:{'|'.join(NEGATION_PREFIXES)})(?: [a-z0-9]+){{0,6}} {escaped_phrase}\b",
        rf"\b(?:does not|do not)(?: [a-z0-9]+){{0,6}} {escaped_phrase}\b",
    ]
    return any(re.search(pattern, task_normalized) for pattern in patterns)


def phrase_hits(task_normalized: str, phrases: list[str]) -> list[str]:
    hits: list[str] = []
    for phrase in phrases:
        normalized_phrase = normalize(phrase)
        if (
            normalized_phrase
            and normalized_phrase in task_normalized
            and not is_negated_phrase(task_normalized, normalized_phrase)
        ):
            hits.append(phrase)
    return hits


def token_hits(task_normalized: str, task_tokens: set[str], tokens: list[str]) -> list[str]:
    hits = [
        token
        for token in tokens
        if token in task_tokens and not is_negated_phrase(task_normalized, normalize(token))
    ]
    return sorted(set(hits))


def token_match_ratio(matched_tokens: list[str], prompt_tokens: list[str]) -> float:
    unique_tokens = sorted(set(prompt_tokens))
    if not unique_tokens:
        return 0.0
    return len(matched_tokens) / len(unique_tokens)


def should_apply_prompt_penalty(
    matched_tokens: list[str],
    *,
    match_ratio: float,
    positive_prompt_tokens: list[str],
    positive_prompt_ratio: float,
) -> bool:
    return (
        len(matched_tokens) >= 2
        and match_ratio >= 0.2
        and (
            match_ratio > positive_prompt_ratio
            or len(matched_tokens) >= len(positive_prompt_tokens) + 2
        )
    )


def resolve_repo_family(task_normalized: str, repo_family: str | None, policy: dict[str, Any]) -> str | None:
    if repo_family:
        return repo_family
    for family_name, family_entry in (policy.get("repo_families") or {}).items():
        family_tokens = family_entry.get("tokens", [])
        if any(
            normalize(token) in task_normalized
            and not is_negated_phrase(task_normalized, normalize(token))
            for token in family_tokens
        ):
            return family_name
    return None


def resolve_stage_2_shortlist_limit(policy: dict[str, Any]) -> int:
    defaults = policy.get("defaults", {})
    return int(defaults.get("max_stage_2_shortlist", defaults.get("top_k", 3)))


def score_band(
    task_normalized: str,
    task_tokens: set[str],
    band: dict[str, Any],
    scoring: dict[str, Any],
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    matched_phrases = phrase_hits(task_normalized, band.get("cues", []))
    matched_tokens = token_hits(task_normalized, task_tokens, tokenize(" ".join(band.get("cues", []))))
    if matched_phrases:
        score += len(matched_phrases) * scoring["phrase_score_weight"]
        reasons.extend(f"cue:{phrase}" for phrase in matched_phrases[:3])
    if len(matched_tokens) >= 2:
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
    normalized_skill_name = normalize(signal["name"])
    explicit_skill_mention = (
        bool(normalized_skill_name)
        and normalized_skill_name in task_normalized
        and not is_negated_phrase(task_normalized, normalized_skill_name)
    )

    if signal["band"] in top_band_ids:
        score += scoring["band_score_weight"]
        reasons.append(f"band:{signal['band']}")
    if explicit_skill_mention:
        score += scoring["phrase_score_weight"] * 2
        reasons.append("explicit-skill-mention")

    positive_phrases = phrase_hits(task_normalized, signal.get("positive_cues", []))
    negative_phrases = phrase_hits(task_normalized, signal.get("negative_cues", []))
    positive_tokens = token_hits(task_normalized, task_tokens, signal.get("cue_tokens", []))
    negative_tokens = token_hits(task_normalized, task_tokens, signal.get("negative_tokens", []))
    positive_prompt_tokens = token_hits(
        task_normalized,
        task_tokens,
        tokenize(signal.get("primary_positive_prompt", "")),
    )
    positive_prompt_ratio = token_match_ratio(
        positive_prompt_tokens,
        tokenize(signal.get("primary_positive_prompt", "")),
    )
    negative_prompt_tokens = token_hits(
        task_normalized,
        task_tokens,
        tokenize(signal.get("primary_negative_prompt", "")),
    )
    negative_prompt_ratio = token_match_ratio(
        negative_prompt_tokens,
        tokenize(signal.get("primary_negative_prompt", "")),
    )
    defer_prompt_tokens = token_hits(
        task_normalized,
        task_tokens,
        tokenize(signal.get("primary_defer_prompt", "")),
    )
    defer_prompt_ratio = token_match_ratio(
        defer_prompt_tokens,
        tokenize(signal.get("primary_defer_prompt", "")),
    )
    has_positive_skill_signal = (
        explicit_skill_mention
        or bool(positive_phrases)
        or len(positive_tokens) >= 2
        or len(positive_prompt_tokens) >= 2
    )

    if positive_phrases:
        score += len(positive_phrases) * scoring["phrase_score_weight"]
        reasons.extend(f"positive:{phrase}" for phrase in positive_phrases[:3])
    if len(positive_tokens) >= 2:
        score += len(positive_tokens) * scoring["token_score_weight"]
        reasons.extend(f"token:{token}" for token in positive_tokens[:3])
    if len(positive_prompt_tokens) >= 2:
        score += len(positive_prompt_tokens) * scoring["token_score_weight"]
        reasons.extend(f"positive-prompt:{token}" for token in positive_prompt_tokens[:3])
    if negative_phrases:
        score -= len(negative_phrases) * scoring["negative_phrase_penalty"]
        reasons.extend(f"negative:{phrase}" for phrase in negative_phrases[:2])
    if negative_tokens:
        score -= len(negative_tokens) * scoring["negative_token_penalty"]
        reasons.extend(f"negative-token:{token}" for token in negative_tokens[:2])
    if should_apply_prompt_penalty(
        negative_prompt_tokens,
        match_ratio=negative_prompt_ratio,
        positive_prompt_tokens=positive_prompt_tokens,
        positive_prompt_ratio=positive_prompt_ratio,
    ):
        score -= len(negative_prompt_tokens) * scoring["negative_token_penalty"]
        reasons.extend(f"negative-prompt:{token}" for token in negative_prompt_tokens[:2])
    if should_apply_prompt_penalty(
        defer_prompt_tokens,
        match_ratio=defer_prompt_ratio,
        positive_prompt_tokens=positive_prompt_tokens,
        positive_prompt_ratio=positive_prompt_ratio,
    ):
        score -= len(defer_prompt_tokens) * scoring["negative_token_penalty"]
        reasons.extend(f"defer-prompt:{token}" for token in defer_prompt_tokens[:2])

    if signal.get("project_overlay"):
        if resolved_repo_family:
            family_entry = (policy.get("repo_families") or {}).get(resolved_repo_family, {})
            prefixes = family_entry.get("project_skill_prefixes", [])
            if any(signal["name"].startswith(prefix) for prefix in prefixes) and (
                has_positive_skill_signal or signal["band"] in top_band_ids
            ):
                score += scoring["overlay_repo_family_bonus"]
                reasons.append(f"overlay-family:{resolved_repo_family}")
        elif not explicit_skill_mention:
            score = min(score, 0)
            reasons.append("overlay-family-missing")

    return score, reasons


def build_fallback_candidates(
    fallback_names: list[str],
    signal_by_name: dict[str, dict[str, Any]],
    shortlisted_names: set[str],
) -> list[dict[str, Any]]:
    fallback_candidates: list[dict[str, Any]] = []
    for fallback_name in fallback_names:
        if fallback_name in shortlisted_names:
            continue
        signal = signal_by_name.get(fallback_name)
        if signal is None:
            continue
        fallback_candidates.append(
            {
                "name": signal["name"],
                "band": signal["band"],
                "manual_invocation_required": signal["manual_invocation_required"],
                "project_overlay": signal["project_overlay"],
                "score": 0,
                "reasons": ["fallback"],
            }
        )
    return fallback_candidates


def summarize_shortlist(shortlist: list[dict[str, Any]], policy: dict[str, Any]) -> tuple[str, int | None, int | None]:
    if not shortlist:
        return "empty", None, None

    lead_score = int(shortlist[0]["score"])
    runner_up_score = int(shortlist[1]["score"]) if len(shortlist) > 1 else 0
    lead_gap = lead_score - runner_up_score

    if (
        lead_score < int(policy["defaults"]["min_activate_score"])
        or lead_gap < int(policy["defaults"]["min_activate_gap"])
    ):
        return "weak", lead_score, lead_gap
    return "strong", lead_score, lead_gap


def infer_top_bands_from_shortlist(
    shortlist: list[dict[str, Any]],
    *,
    max_band_candidates: int,
) -> list[dict[str, Any]]:
    band_entries: dict[str, dict[str, Any]] = {}
    for entry in shortlist:
        band_id = entry["band"]
        best = band_entries.get(band_id)
        score = int(entry["score"])
        if best is not None and int(best["score"]) >= score:
            continue
        band_entries[band_id] = {
            "id": band_id,
            "score": score,
            "reasons": [f"shortlist:{entry['name']}"],
        }
    ranked_bands = sorted(
        band_entries.values(),
        key=lambda entry: (-int(entry["score"]), entry["id"]),
    )
    return ranked_bands[:max_band_candidates]


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
    requested_top_k = policy["defaults"]["top_k"] if top_k is None else top_k
    top_k = min(max(int(requested_top_k), 1), resolve_stage_2_shortlist_limit(policy))
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
    top_bands = [entry for entry in scored_bands if entry["score"] > 0][: policy["defaults"]["max_band_candidates"]]
    top_band_ids = {entry["id"] for entry in top_bands}

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
    if not top_bands and shortlist:
        top_bands = infer_top_bands_from_shortlist(
            shortlist,
            max_band_candidates=policy["defaults"]["max_band_candidates"],
        )
    confidence, lead_score, lead_gap = summarize_shortlist(shortlist, policy)
    fallback_candidates = build_fallback_candidates(
        policy["defaults"].get("fallback_skills", []),
        signal_by_name,
        {entry["name"] for entry in shortlist},
    )

    return {
        "task": task,
        "repo_family": resolved_repo_family,
        "top_bands": top_bands,
        "shortlist": shortlist,
        "confidence": confidence,
        "lead_score": lead_score,
        "lead_gap": lead_gap,
        "fallback_candidates": fallback_candidates,
    }


def coerce_preselect_result(task: str, preselect_result: dict[str, Any] | list[str]) -> dict[str, Any]:
    if isinstance(preselect_result, dict):
        return {
            "task": preselect_result.get("task", task),
            "repo_family": preselect_result.get("repo_family"),
            "top_bands": preselect_result.get("top_bands", []),
            "shortlist": preselect_result.get("shortlist", []),
            "confidence": preselect_result.get("confidence", "strong"),
            "lead_score": preselect_result.get("lead_score"),
            "lead_gap": preselect_result.get("lead_gap"),
            "fallback_candidates": preselect_result.get("fallback_candidates", []),
        }

    shortlist = [{"name": name} for name in preselect_result]
    return {
        "task": task,
        "repo_family": None,
        "top_bands": [],
        "shortlist": shortlist,
        "confidence": "strong" if shortlist else "empty",
        "lead_score": None,
        "lead_gap": None,
        "fallback_candidates": [],
    }


def build_decision_packet(
    task: str,
    preselect_result: dict[str, Any] | list[str],
    skills_root: Path,
    *,
    max_shortlist: int | None = None,
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
    preselect_payload = coerce_preselect_result(task, preselect_result)
    shortlist_entries = preselect_payload.get("shortlist", [])
    if max_shortlist is not None and len(shortlist_entries) > max_shortlist:
        raise ValueError(
            f"stage-2 shortlist exceeds configured max_shortlist={max_shortlist}: got {len(shortlist_entries)} entries"
        )
    shortlist_by_name = {
        entry.get("name"): entry for entry in shortlist_entries if entry.get("name")
    }

    candidates: list[dict[str, Any]] = []
    for name in shortlist_by_name:
        signal = signal_by_name.get(name)
        capsule = capsule_by_name.get(name)
        adapter = adapter_by_name.get(name)
        retention = retention_by_name.get(name)
        if signal is None or capsule is None or adapter is None or retention is None:
            continue
        shortlist_entry = shortlist_by_name[name]
        candidates.append(
            {
                "name": name,
                "band": signal["band"],
                "score": shortlist_entry.get("score"),
                "preselect_reasons": shortlist_entry.get("reasons", []),
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

    confidence = preselect_payload.get("confidence", "empty")
    lead_score = preselect_payload.get("lead_score")
    lead_gap = preselect_payload.get("lead_gap")
    fallback_candidates = preselect_payload.get("fallback_candidates", [])

    if confidence == "empty" or not candidates:
        suggested_decision = {
            "decision_mode": "no-skill",
            "skill": None,
            "next_step": "continue without a skill or use flat routing",
        }
        decision_reason = "no positive-signal shortlist under the precision-first routing policy"
    elif confidence == "weak":
        suggested_decision = {
            "decision_mode": "no-skill",
            "skill": None,
            "next_step": "continue without a skill or use flat routing",
        }
        decision_reason = "shortlist stayed below the precision-first activation thresholds"
    else:
        lead = candidates[0]
        if lead["manual_invocation_required"]:
            suggested_decision = {
                "decision_mode": "manual-invocation-required",
                "skill": lead["name"],
                "next_step": f"require explicit handle ${lead['name']} before activation",
            }
            decision_reason = "lead candidate is explicit-only even though the shortlist is strong"
        else:
            suggested_decision = {
                "decision_mode": "activate-candidate",
                "skill": lead["name"],
                "next_step": f"inspect or activate {lead['name']} using the skill runtime seam",
            }
            decision_reason = "lead candidate cleared the precision-first activation thresholds"

    return {
        "task": task,
        "confidence": confidence,
        "lead_score": lead_score,
        "lead_gap": lead_gap,
        "candidate_count": len(candidates),
        "fallback_candidates": fallback_candidates,
        "candidates": candidates,
        "decision_reason": decision_reason,
        "suggested_decision": suggested_decision,
        "stage_2_checklist": [
            "choose at most one skill to activate",
            "if the lead candidate is explicit-only, require an explicit handle",
            "do not load full skill bodies for non-shortlisted skills",
            "continue without a skill when the shortlist is weak or empty",
            "keep fallback candidates visible without treating them as the live shortlist",
        ],
    }
