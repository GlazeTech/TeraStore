import pytest

from api.config import get_env_var


def test_missing_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOME_VAR", raising=False)

    with pytest.raises(ValueError, match="Environment variable SOME_VAR is not set"):
        get_env_var("SOME_VAR")
