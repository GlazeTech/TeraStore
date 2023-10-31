from api.utils.paths import get_project_root


def test_get_project_root() -> None:
    root = get_project_root()
    assert root.name in ["app", "api"]
