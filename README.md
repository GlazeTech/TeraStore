# TeraStore

Welcome to TeraStore: A storage solution for THz pulses. The project consists of a FastAPI backend (located in `./backend`), a React frontend (located at `./frontend`) and data storage using [postgreSQL with Docker](https://geshan.com.np/blog/2021/12/docker-postgres/). All containerized with [Docker](https://www.docker.com/).

To talk to the API, we recommend:

* [RapidAPI for Mac](https://paw.cloud)
* [xh](https://github.com/ducaale/xh)
* [httpie](https://httpie.io) seems like a nice alternative

Beware that many API tools have a bad reputation around turning into money-making machines, so be careful!

To interact with the Postgres DB, you may use Jetbrains' [DataGrip](https://www.jetbrains.com/datagrip/), which is free if you're a student like us!

## Deployment
Before deploying the applications the environment variables
* `VITE_BACKEND_URL`: The URL of the backend endpoint. A special environment variable (see [this](https://vitejs.dev/guide/env-and-mode.html)), which is loaded at build-time.
* `POSTGRES_USER`: The PostgreSQL username to be used by the backend
* `POSTGRES_PASSWORD`: The PostgreSQL password for `POSTGRES_USER`
* `POSTGRES_DB`: The PostgreSQL database for storage
* `DATABASE_URL`: The URL of the database containing connection information.
* `TERASTORE_ADMIN_USERNAME`: The username of a user with administrator righs to be created in the database
* `TERASTORE_ADMIN_PASSWORD`: The password of a user with administrator righs to be created in the database
* `SECRET_KEY`: A secret key for hashing passwords
* `ALLOWED_ORIGINS`: A comma-separated list of allowed origins to communicate with the backend
* 
For deployment of the app, run
`docker compose -f ./docker-compose-prod.yml up`

## Develop

To run the application, you must first set the environment variables listed above, except for `VITE_BACKEND_URL`, which is not strictly required for running a development environment. We suggest you create a `.env` file in the root of the project.
This will contain the above mentioned environment variables, and you can fill it out like so:

```bash
POSTGRES_USER="terastore-user"
POSTGRES_PASSWORD="terastore-password"
POSTGRES_DB="terastore-db"
DATABASE_URL="postgresql://username:password@host/database"
TERASTORE_ADMIN_USERNAME="admin@terastore"
TERASTORE_ADMIN_PASSWORD="administrator123"
SECRET_KEY="some-long-secret-123"
ALLOWED_ORIGINS="http://0.0.0.0:5173,http://localhost:3000"
```

A development environment can then be created by running
`docker compose -f ./docker-compose-dev.yml up`

The frontend can now be visited on [http://0.0.0.0:5173/](http://0.0.0.0:5173/). Log in using email `admin@admin` and password `admin`, which is a user created as part of spinning up the development environment. 

Hot-reloading on code changes is enabled, so both backend and frontend can now be developed. 

## Tests

All tests (unit- and integration tests) can be run (using bash) with
`./scripts/run_all_tests.sh`

Currently, a powershell script for running tests on Windows is not supplied.

## Development with VS Code
If you wish to develop from the root of the workspace, instead of opening e.g. `./backend` to work on the API,
you may create a file `.vscode/settings.json`, and populate it like so:

```json
{
    "python.analysis.extraPaths": ["./backend"],
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
    "mypy.runUsingActiveInterpreter": true
}
```

This ensures that the relevant services pick up binaries and configurations when you've installed all dependencies.
It also ensures that VS Code knows where the functions and classes of this module are located: in the `./backend` folder, not in the virtual environment.

>NB: Biome format does not work in this configuration.
>The extension output _says_ it picks up the configuration file in `./frontend`, but formatting does not work (Biome is said by VS Code to not be able to format e.g. Typescript files; which is a blatant lie).
>If one moves the `biome.json` file to the root of the workspace, it works fine.
>I have tried with a symlinked file, but that breaks other stuff.
>
>Do note: the VS Code Python test extension will not work.
>It does not integrate with Docker, other than if you run VS Code in a dev container.
>It would be nice to get it to work... I am currently looking at options.
>[This](https://github.com/kondratyev-nv/vscode-python-test-adapter) extension might prove useful.
>
>Do _also_ note: the VS Code Python debugger extension will not work.
>Again, Docker.
>However, I think there are actual solutions for this, which I at some point will look into.

Then, install the environments and dependencies.

First, make sure that you have Python 3.12.
You may have a look at [pyenv](https://github.com/pyenv/pyenv) to administer several Python versions on one machine.

Then, run
```bash
python3.12 -m venv .venv --prompt terastore-backend
pip install ./backend[dev]
```

This installs a virtual environment in the workspace root, and installs all dependencies required for development.

Next, install the frontend by running
```bash
cd ./frontend
npm install
```

For your sake, we recommend you also install [direnv](https://direnv.net).
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

Then, run
```bash
./scripts/dev_up.sh
```

You can now talk to the API via `http://0.0.0.0:8000`, and see the frontend in a browser at `http://0.0.0.0:5173/`.

When you're done developing, run
```bash
./scripts/dev_down.sh
```
This closes the dev services again.

~~Be aware: while it seems to work to have the dev and test services running simultaneously, I have seen some weird behaviour once in a while.
Thus, I tend to take the dev services down before I run the test suite.~~
Running all the services (PROD, DEV, TEST) concurrently should be fixed now.

## Testing

You can also easily test the backend!
In the `./scripts` folder, we have some useful stuff.
If you run
```bash
./scripts/run_all_tests.sh
```
a Docker Compose instance will spin up, and do all the tests for you!

Nifty!

## Password handling

We hash and salt user passwords.
We use [PassLib](https://passlib.readthedocs.io/en/stable/) with an Argon2 hash.

The hashed password that we save in the database has the following format:

```
$argon2X$v=V$m=M,t=T,p=P$salt$digest
```

See a detailed explanation [here](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html#format-algorithm).
