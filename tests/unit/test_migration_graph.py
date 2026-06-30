from scripts.verify_migration_graph import main as verify_migration_graph


def test_migration_graph_is_linear_and_resolvable() -> None:
    assert verify_migration_graph() == 0
