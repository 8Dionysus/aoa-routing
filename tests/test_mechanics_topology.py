from scripts.validate_mechanics_topology import validate


def test_mechanics_topology_validates() -> None:
    assert validate() == []
