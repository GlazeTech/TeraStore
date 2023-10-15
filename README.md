# TeraStore

Welcome to TeraStore: A storage solution for THz pulses. The project consists of a FastAPI backend (located in `./backend`), a React frontend (located at `./frontend`) and data storage using [postgreSQL with Docker](https://geshan.com.np/blog/2021/12/docker-postgres/). All containerized with [Docker](https://www.docker.com/).

To talk to the API, we recommend:

* [RapidAPI for Mac](https://paw.cloud)
* [xh](https://github.com/ducaale/xh)
* [httpie](https://httpie.io) seems like a nice alternative

Beware that many API tools have a bad reputation around turning into money-making machines, so be careful!

To interact with the Postgres DB, you may use Jetbrains' [DataGrip](https://www.jetbrains.com/datagrip/), which is free if you're a student like us!

## Develop

To run the application, you must first set the following environment variables:
* `POSTGRES_USER`: The PostgreSQL username to be used by the backend
* `POSTGRES_PASSWORD`: The PostgreSQL password for `POSTGRES_USER`
* `POSTGRES_DB`: The PostgreSQL database for storage

We suggest you create a `.env` file in the root of the project.
This will contain the above mentioned environment variables, and you can fill it out like so:

```bash
ENV=dev
POSTGRES_USER=terastore-user
POSTGRES_PASSWORD=terastore-password
POSTGRES_DB=terastore-db
```

The environment variable `ENV` will ensure that when you start the app a fresh database with mock data will be created,
and the API will reload upon save (when [PR SQLModel & FastAPI implementation](https://github.com/GlazeTech/TeraStore/pull/15) has been merged).

Further, if you wish to develop from the root of the workspace, instead of opening e.g. `./backend` to work on the API,
you may create a file `.vscode/settings.json`, and populate it like so:

```json
{
    "black-formatter.args": [
        "--config",
        "./backend/pyproject.toml"
    ],
    "black-formatter.importStrategy": "fromEnvironment",
    "ruff.format.args": [
        "--config",
        "./backend/pyproject.toml"
    ],
    "mypy.configFile": "./backend/pyproject.toml",
    "mypy.runUsingActiveInterpreter": true,
    "python.testing.pytestArgs": [
        "backend"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "biome.lspBin": "./frontend/node_modules/@biomejs/cli-darwin-arm64/biome",
    "[typescriptreact]": {
        "editor.defaultFormatter": "biomejs.biome",
        "editor.formatOnSave": true
    }
}
```

This _should_ ensure that the relevant services pick up binaries and configurations when you've installed all dependencies.

NB: the `biome.lspBin` is unfortunate, as it depends on version and platform. Not yet sure how to fix this.

Then, install the environments and dependencies.

First, make sure that you have Python 3.11.
You may have a look at [pyenv](https://github.com/pyenv/pyenv) to administer several Python versions on one machine.

Then, run
```bash
python -m venv .venv prompt terastore-backend
pip install ./backend[test]
```

This installs a virtual environment in the workspace root, and installs all dependencies required for development.

Next, install the frontend by running
```bash
cd ./frontend
npm install
```

For your sake, we recommend also install [direnv](https://direnv.net).
Do this, and make a file called `.envrc` in the workspace root, and populate it with
```bash
export VIRTUAL_ENV=.venv
layout python
dotenv
```

The terminal should give you a warning when you enter the workspace root, but if you run
```bash
direnv allow
```
it picks up the configuration from `direnv`, and will activate your virtual environment and load the environment variables you set in the `.env` file.

We have a list of recommended VS Code extensions in `.vscode/extensions.json`; VS Code will prompt you to install these, and you should agree.

You should now have access to all VS Code features when developing locally!

Then, run
```bash
docker-compose -f docker-compose.dev.yml up
```
which starts the services.

You can now talk to the API via `http://0.0.0.0:8000`, and see the frontend in a browser at the URL stated by Vite in the `docker-compose` log.
