import tomllib
from pathlib import Path

from api.utils.paths import get_project_root

with Path(get_project_root() / "pyproject.toml").open("rb") as f:
    pyproject = tomllib.load(f)
__version__ = pyproject["tool"]["poetry"]["version"]
