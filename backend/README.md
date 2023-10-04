# TeraStore API
This is the TeraStore API.

This project uses [`FastAPI`](https://fastapi.tiangolo.com) and `Python 3.11`.
It is typed using [`mypy`](https://www.mypy-lang.org), linted with [`Ruff`](https://docs.astral.sh/ruff/), formatted with [`Black`](https://black.readthedocs.io/en/stable/) and tested with [`pytest`](https://docs.pytest.org/).

We use [`Poetry`](https://python-poetry.org) to install the project and manage dependencies.

Install the project with `Poetry` by ensuring you have `Python 3.11` installed and running

```
poetry install
```

This will install all dependencies, including test and dev.

The app can be started via a `Poetry` script by running the command `poetry run start`.

You can use [`Postman`](https://www.postman.com/) to test against the API.