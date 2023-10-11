# TeraStore

Welcome to TeraStore: A storage solution for THz pulses. The project consists of a FastAPI backend (located in `./backend`), a React frontend (located at `./frontend`) and data storage using [postgreSQL with Docker](https://geshan.com.np/blog/2021/12/docker-postgres/). All containerized with [Docker](https://www.docker.com/).

To run the application, you must first set the following environment variables:
* `POSTGRES_USER`: The PostgreSQL username to be used by the backend
* `POSTGRES_PASSWORD`: The PostgreSQL password for `POSTGRES_USER``
* `POSTGRES_DB`: The PostgreSQL database for storage

Then,
`docker-compose up`