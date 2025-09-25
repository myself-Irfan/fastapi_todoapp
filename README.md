## Todo-App
A lightweight **FastAPI**-based Todo application

---

## Features
- User registration & login with **JWT authentication**
- Create, Read, Update and Delete tasks (CRUD)
- **Rate-limiting** for registration
- Structured logging with auto request response logging and sensitive data sanitization
- Dockerized for local development & deployment
- CI with automated tests

---

## Tech Stack
- **Backend**: FastAPI, Python 3.11+
- **Frontend**: VanillaJS
- **Database**: Postgres
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Testing**: Pytest
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

---

## Getting started

### 1. Clone the repository
```commandline
git clone https://github.com/myself-Irfan/fastapi_todoapp.git
cd fastapi_todoapp
```

### 2. Set up environment variables
copy the variables from sample.env into a .env file
- **local**: DB_HOST=localhost
- **docker**: DB_HOST=host.docker.internal

### 3. Run the application
- **local**: uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
- **docker**: docker compose up --build -d

### 4. Run tests
- **local**: pytest -v
- **docker**: docker compose run --rm web pytest -v

---

## CI/CD
- GitHub Actions run tests on push & pull requests to master.
- Postgres service is spun up for CI testing
- Dummy environment variables are hardcoded in CI

---

## Log
All logs are stored in the directory **LOG_DIR**

---

## License
Copyright (c) 2025 Irfan Ahmed