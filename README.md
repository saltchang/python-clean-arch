# Python Clean Architecture

This project aims to provide a template for clean architecture in Python applications.

## Table of Contents

- [Python Clean Architecture](#python-clean-architecture)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Getting Started](#getting-started)
    - [Setup Environment Variables](#setup-environment-variables)
    - [Quick Start with Docker Compose](#quick-start-with-docker-compose)
    - [Database Setup](#database-setup)
    - [Start the Server](#start-the-server)
      - [With Poetry](#with-poetry)
      - [With VSCode Debugger](#with-vscode-debugger)
    - [Running Tests](#running-tests)
      - [With Poetry in Command Line](#with-poetry-in-command-line)
      - [With Docker](#with-docker)
    - [API Documentation](#api-documentation)
  - [Editor Integration](#editor-integration)

## Description

The main idea of [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) by [Robert C. Martin (Uncle Bob)](http://cleancoder.com) is to separate the concerns of the application into different layers, so that the application is more maintainable and scalable. Here are the main principles of clean architecture from the [original article](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html):

> - Independent of Frameworks. The architecture does not depend on the existence of some library of feature laden software. This allows you to use such frameworks as tools, rather than having to cram your system into their limited constraints.
> - Testable. The business rules can be tested without the UI, Database, Web Server, or any other external element.
> - Independent of UI. The UI can change easily, without changing the rest of the system. A Web UI could be replaced with a console UI, for example, without changing the business rules.
> - Independent of Database. You can swap out Oracle or SQL Server, for Mongo, BigTable, CouchDB, or something else. Your business rules are not bound to the database.
> - Independent of any external agency. In fact your business rules simply don’t know anything at all about the outside world.

The diagram from the article also shows the different layers of the clean architecture and the dependencies between them:

![Clean Architecture](https://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

There is another diagram from [go-clean-arch](https://github.com/bxcodec/go-clean-arch) by [bxcodec](https://github.com/bxcodec) which is more intuitive for me:

![Go Clean Architecture](https://raw.githubusercontent.com/bxcodec/go-clean-arch/master/clean-arch.png)

Based on the concept of clean architecture, this project contains the following layers:

- Core layer (`/core`): The entities layer, which contains the core business rules and logic
- Service layer (`/service`): The use cases layer, which contains the application of business rules and logic
- Repository layer (`/repository`): The infrastructure layer, which contains the data access logic
- API layer (`/api`): The presentation layer, which contains the HTTP API endpoints

## Getting Started

### Setup Environment Variables

First, setup the environment variables, please refer to the `.env.example` file. Ask your team for the values. You can create a new `.env` file by running the following command:

```bash
cp .env.example .env
```

### Quick Start with Docker Compose

You can quickly start the server with docker compose:

```bash
docker compose -f docker-compose.yml up --remove-orphans -d
```

### Database Setup

In this example, we use PostgreSQL as the database, please make sure you have it installed locally, you can set the `DATABASE_URL` in the `.env` file to connect to your local database:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/python_clean_arch
```

Or you can use docker compose file we provided to quickly setup one:

```bash
docker compose -f docker-compose.db.yml up --remove-orphans -d
```

You can change the `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` in the `.env` file to change the database info of docker container.

Please remember to align the `DATABASE_URL` with the `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` in the `.env` file.

After the database is running, you can initialize the database by running the following commands:

```bash
make init-db
```

### Start the Server

#### With Poetry

[Poetry](https://python-poetry.org/docs#installation) is used to manage the dependencies, make sure you have it installed before you start.

1. Install dependencies

    ```bash
    poetry env use 3.13
    poetry install
    ```

2. Activate the virtual environment

    ```bash
    eval $(poetry env activate)
    ```

3. Run the server

    ```bash
    make run-server
    ```

#### With VSCode Debugger

VSCode is recommended for development, before you start, make sure you have installed the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) extensions.

1. First, you need to install the dependencies, see [With Poetry](#with-poetry)

2. Then, select the correct python interpreter in VSCode by press `cmd + shift + p` and search `Python: Select Interpreter`. The python interpreter should be the one you installed in the first step, usually you can find the option with `(Poetry)` in the list.

3. Then, you need to set up the debugger configuration for VSCode:

    ```bash
    cp .vscode/launch.example.json .vscode/launch.json
    ```

4. Choose the "FastAPI" configuration from the VSCode and run it.

### Running Tests

#### With Poetry in Command Line

Make sure you have activated the virtual environment with [Poetry](#with-poetry):

```bash
eval $(poetry env activate)
```

Then, you can run the unit tests by the following command:

```bash
make run-unit-tests
```

#### With Docker

You can also run the unit tests with docker:

```bash
docker build -f Dockerfile.dev -t app-test --build-arg RUN_MODE=test . && docker run app-test
```

### API Documentation

Once the server is running, visit the Swagger UI at [http://localhost:7086/docs](http://localhost:7086/docs)

## Editor Integration

- Language Server - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), which depends on [Pyright](https://microsoft.github.io/pyright/#/).

- Linting and Formatting - [Ruff](https://github.com/astral-sh/ruff)

For VSCode, run the following command to setup the editor config:

```bash
cp .vscode/settings.example.json .vscode/settings.json
```
