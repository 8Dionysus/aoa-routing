from scripts.validate_source_home import validate


def test_source_home_topology_validates() -> None:
    assert validate() == []
