import pytest

from api.config import get_env_var


def test_missing_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a missing env var raises an exception.

    Args:
    ----
        monkeypatch (pytest.MonkeyPatch): The monkeypatch fixture.

    Returns:
    -------
        None
    """
    monkeypatch.delenv("SOME_VAR", raising=False)

    # Now test that calling your function without the env var set raises the exception
    with pytest.raises(ValueError, match="Environment variable SOME_VAR is not set"):
        get_env_var("SOME_VAR")
