from pathlib import Path

from scripts.validate_active_legacy_names import validate


def test_active_paths_do_not_use_legacy_names() -> None:
    assert validate() == []


def test_repository_kag_family_is_outside_authored_content_checks(tmp_path: Path) -> None:
    for relative_path in (
        "kag/indexes/index_family.manifest.json",
        "kag/indexes/shards/source/00.jsonl",
        "kag/indexes/shards/event/0.jsonl",
        "kag/receipts/index_family_budget/digest.json",
    ):
        index_path = tmp_path / relative_path
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text("historical " + ("wa" + "ve") + " route\n", encoding="utf-8")

    assert validate(tmp_path) == []


def test_top_level_sibling_checkouts_are_not_active_local_content(tmp_path: Path) -> None:
    for checkout_name in ("aoa-techniques", "abyss-machine"):
        sibling_doc = tmp_path / checkout_name / "TECHNIQUE.md"
        sibling_doc.parent.mkdir()
        sibling_doc.write_text(
            "legacy "
            + ("wa" + "ve")
            + " "
            + ("se" + "ed")
            + " language in sibling checkout\n",
            encoding="utf-8",
        )

    fixture_doc = tmp_path / "tests" / "fixtures" / "aoa-techniques" / "TECHNIQUE.md"
    fixture_doc.parent.mkdir(parents=True)
    fixture_doc.write_text("ordinary fixture content\n", encoding="utf-8")

    assert validate(tmp_path) == []
