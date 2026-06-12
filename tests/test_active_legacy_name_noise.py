from pathlib import Path

from scripts.validate_active_legacy_names import validate


def test_active_paths_do_not_use_legacy_names() -> None:
    assert validate() == []


def test_top_level_sibling_checkouts_are_not_active_local_content(tmp_path: Path) -> None:
    sibling_doc = tmp_path / "aoa-techniques" / "TECHNIQUE.md"
    sibling_doc.parent.mkdir()
    sibling_doc.write_text(
        "legacy " + ("wa" + "ve") + " " + ("se" + "ed") + " language in sibling checkout\n",
        encoding="utf-8",
    )

    fixture_doc = tmp_path / "tests" / "fixtures" / "aoa-techniques" / "TECHNIQUE.md"
    fixture_doc.parent.mkdir(parents=True)
    fixture_doc.write_text("ordinary fixture content\n", encoding="utf-8")

    assert validate(tmp_path) == []
