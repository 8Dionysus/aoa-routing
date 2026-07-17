#!/usr/bin/env python3
"""Reject legacy route names from active local topology."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OLD_STAGE = "wa" + "ve"
OLD_BOOTSTRAP = "se" + "ed"
OLD_AGON_RECEIPT_PREFIX = "AOR" + "-Q-" + "AGON"
OLD_SOURCE_DOC_ALIAS = "planting" + "_" + "protocol"


@dataclass(frozen=True)
class LegacyPathRule:
    pattern: re.Pattern[str]
    message: str


LEGACY_PATH_RULES = (
    LegacyPathRule(
        re.compile(rf"(?:^|/){OLD_AGON_RECEIPT_PREFIX}-\d+"),
        "historical Agon quest receipts belong under mechanics/agon/legacy/raw/",
    ),
    LegacyPathRule(
        re.compile(
            rf"(?:^|/)test_experience_{OLD_STAGE}[2-5]_{OLD_BOOTSTRAP}_contracts\.py$"
        ),
        "root-stage experience test names must use operation names in active paths",
    ),
    LegacyPathRule(
        re.compile(rf"(?:^|/)tests/test_.*_{OLD_BOOTSTRAP}_contracts\.py$"),
        "root active contract tests must use operation names, not bootstrap-stage names",
    ),
    LegacyPathRule(
        re.compile(rf"(?:^|/)test_{OLD_STAGE}1_owner_dispatch_seam\.py$"),
        "owner-dispatch tests must use operation names in active paths",
    ),
    LegacyPathRule(
        re.compile(rf"(?:^|/)routing-stress-chaos-{OLD_STAGE}1\.md$"),
        "stress routing docs must use operation names in active paths",
    ),
    LegacyPathRule(
        re.compile(rf"(?:^|/|[_-]){OLD_STAGE}[0-9]+(?:[_./-]|$)", re.IGNORECASE),
        "old rollout labels belong under package-local legacy, not active path names",
    ),
    LegacyPathRule(
        re.compile(
            rf"(?:^|/|[_-]){OLD_BOOTSTRAP}(?:s|ed|ing)?(?:[_./-]|$)|"
            rf"{OLD_SOURCE_DOC_ALIAS}",
            re.IGNORECASE,
        ),
        "old bootstrap labels belong under package-local legacy, not active path names",
    ),
)
LEGACY_CONTENT_RULES = (
    LegacyPathRule(
        re.compile(rf"{OLD_AGON_RECEIPT_PREFIX}-\d+|{OLD_AGON_RECEIPT_PREFIX}-\*"),
        "concrete historical Agon receipt ids belong under package-local legacy",
    ),
    LegacyPathRule(
        re.compile(
            rf"\b{OLD_STAGE}(?:[-_ ]?[0-9]+)?\b|{OLD_STAGE}_scope|{OLD_STAGE.upper()}[0-9]",
            re.IGNORECASE,
        ),
        "old rollout labels belong under package-local legacy, not active local content",
    ),
    LegacyPathRule(
        re.compile(
            rf"active-{OLD_BOOTSTRAP}ed|{OLD_BOOTSTRAP}ed_pre_protocol|"
            rf"automation_{OLD_BOOTSTRAP}_candidate|"
            rf"{OLD_BOOTSTRAP} example|{OLD_BOOTSTRAP.title()} schema|"
            rf"federation harvest {OLD_BOOTSTRAP}"
        ),
        "bootstrap-stage wording must not name active local routing contracts",
    ),
    LegacyPathRule(
        re.compile(
            rf"\b{OLD_BOOTSTRAP}(?:s|ed|ing)?\b|"
            rf"{OLD_BOOTSTRAP}[-_]|[-_]{OLD_BOOTSTRAP}|"
            rf"{OLD_SOURCE_DOC_ALIAS}",
            re.IGNORECASE,
        ),
        "old bootstrap labels belong under package-local legacy, not active local content",
    ),
)

EXCLUDED_PARTS = {
    ".git",
    ".deps",
    ".pytest_cache",
    "__pycache__",
    "legacy",
}
EXCLUDED_PREFIXES: tuple[Path, ...] = tuple(
    Path(name)
    for name in (
        "8Dionysus",
        "Agents-of-Abyss",
        "Dionysus",
        "Tree-of-Sophia",
        "abyss-machine",
        "abyss-stack",
        "aoa-agents",
        "aoa-evals",
        "aoa-kag",
        "aoa-memo",
        "aoa-playbooks",
        "aoa-sdk",
        "aoa-skills",
        "aoa-stats",
        "aoa-techniques",
    )
)
EXCLUDED_CONTENT_FILES = {
    Path("scripts/validate_active_legacy_names.py"),
}
EXCLUDED_CONTENT_PREFIXES: tuple[Path, ...] = (
    Path("kag/indexes/index_family.manifest.json"),
    Path("kag/indexes/shards"),
    Path("kag/receipts/index_family_budget"),
)
TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


def relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    return path.relative_to(repo_root).as_posix()


def is_excluded(path: Path, repo_root: Path = REPO_ROOT) -> bool:
    rel = path.relative_to(repo_root)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return True
    return any(rel == prefix or prefix in rel.parents for prefix in EXCLUDED_PREFIXES)


def is_content_excluded(path: Path, repo_root: Path = REPO_ROOT) -> bool:
    rel = path.relative_to(repo_root)
    if is_excluded(path, repo_root):
        return True
    if rel in EXCLUDED_CONTENT_FILES:
        return True
    if any(rel == prefix or prefix in rel.parents for prefix in EXCLUDED_CONTENT_PREFIXES):
        return True
    return False


def validate(repo_root: Path = REPO_ROOT) -> list[str]:
    issues: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if is_excluded(path, repo_root):
            continue
        rel = relative(path, repo_root)
        for rule in LEGACY_PATH_RULES:
            if rule.pattern.search(rel):
                issues.append(f"{rel}: {rule.message}")
        if path.is_file() and path.suffix in TEXT_SUFFIXES and not is_content_excluded(path, repo_root):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for rule in LEGACY_CONTENT_RULES:
                if rule.pattern.search(text):
                    issues.append(f"{rel}: {rule.message}")
    return issues


def main() -> int:
    issues = validate()
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("active legacy-name topology OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
