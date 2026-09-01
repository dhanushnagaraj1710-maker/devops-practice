# DevOps Demo API

A containerized Flask REST API that provides health-check endpoints and a simple application interface. It demonstrates practical DevOps capabilities including Docker containerization, automated testing, and CI/CD using GitHub Actions to validate changes automatically. The project goes beyond a basic API by enforcing quality gates through automated checks and protected branches before code can be merged.

## Problem Statement

Shipping code safely requires more than "it works on my machine." This project demonstrates a complete, automated verification pipeline — every change is tested and containerized automatically before it can reach the main branch, with no manual steps required and no way to bypass a failing check through a pull request.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Flask
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest
- **CI/CD:** GitHub Actions
- **Version Control:** Git, GitHub

## Prerequisites

- Python 3.12
- Docker Desktop
- Git
- A GitHub account (only needed to fork/clone and use the CI/CD pipeline)

## Local Setup & How to Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd devops-practice
```

### 2. Set up the Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run locally without Docker

```bash
python3 app.py
```

The API will be available at `http://localhost:5000`.

### 4. Run with Docker

```bash
docker build -t devops-demo-api .
docker run -p 5001:5000 devops-demo-api
```

> **Note:** if port 5000 is already in use on your machine (common on macOS due to AirPlay Receiver), map to a different host port as shown above (`-p 5001:5000`), or disable AirPlay Receiver in System Settings.

The API will be available at `http://localhost:5001`.

### 5. Run with Docker Compose (recommended for local development)

```bash
docker compose up --build
```

This mounts the project directory into the container, so code changes are picked up live without rebuilding.

To stop:
```bash
docker compose down
```

## API Endpoints

| Method | Path       | Description                              |
|--------|------------|-------------------------------------------|
| GET    | `/health`  | Returns service health status             |
| GET    | `/version` | Returns app version (env-var configurable)|
| GET    | `/ping`    | Simple liveness check                     |
| GET    | `/status`  | Returns service status                    |

Example:
```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

## Architecture & CI/CD Pipeline

```
Developer
   │
   │ git push
   ▼
GitHub Repository
   │
   │ Push / Pull Request
   ▼
GitHub Actions
   │
   ├── Checkout Code
   │
   ├── Set up Python
   │
   ├── Install Dependencies
   │
   ├── Run pytest
   │       │
   │       └── ❌ Tests fail → CI fails
   │
   ├── Build Docker Image
   │       │
   │       └── ❌ Build fails → CI fails
   │
   └── ✅ Tests + Docker Build Pass
              │
              ▼
          CI Success
```

Every push and pull request to `main` triggers this pipeline automatically. The workflow first installs dependencies and runs the full `pytest` suite, then builds the Docker image using the project's Dockerfile — verifying both the application logic and the deployment artifact independently, since a passing test suite does not guarantee the Docker build itself is still valid. If either step fails, the pipeline stops immediately and the failure is reported directly on the pull request.

`main` is protected by a branch rule requiring the CI status check to pass before any pull request can be merged — broken code is blocked at the platform level, not just flagged for a human to notice.

## Infrastructure Explanation

- **Dockerfile** builds a `python:3.12-slim` image, installs dependencies from `requirements.txt` (cached as a separate layer for faster rebuilds), then copies in the application code.
- **Docker Compose** wires up local development: builds the image, maps ports, injects environment variables, and mounts the source directory for live reload during development.
- **GitHub Actions** runs on GitHub-hosted `ubuntu-latest` runners — fresh, disposable VMs created per run, with no persistent state between runs.

## Security Considerations

- The application binds to `0.0.0.0` inside the container (required for the host to reach it through Docker's port mapping) — this is safe specifically because the container's network exposure is still controlled entirely by the `-p` mapping and any firewall/Security Group in front of it, not by the bind address itself.
- Sensitive configuration (e.g. `APP_VERSION`) is read from environment variables rather than hardcoded, following the same pattern used for GitHub Actions secrets — real secrets are never printed, logged, or committed. A `.env.example` file documents expected variables without exposing real values.
- `.gitignore` and `.dockerignore` both exclude `venv/`, `__pycache__/`, and other local artifacts from version control and the Docker build context respectively.

## Troubleshooting

**Port 5000 already in use:**
Check what's using it with `lsof -i :5000` (often AirPlay Receiver on macOS), then either free the port or map to a different host port (`-p 5001:5000`).

**Container starts but `curl` gives "Connection reset by peer":**
Confirm the Flask app is bound to `0.0.0.0`, not `127.0.0.1`, inside the container — `127.0.0.1` is only reachable from inside that exact container, not from the host via port mapping.

**Container exits immediately / crashes:**
```bash
docker ps -a          # confirm the exit code
docker logs <name>    # view the container's stored output to find the actual error
```

**CI fails on a pull request:**
Click into the failed check on the PR page to see exactly which step (tests or Docker build) failed and why — the pipeline is designed to fail fast and report the specific cause.

## Lessons Learned

- A passing test suite does not guarantee a working Docker build — the two need independent verification in CI.
- Branch protection only meaningfully enforces quality on pull requests; direct pushes by a repo owner can bypass required checks unless "include administrators" is also enabled.
- Secret masking in CI logs only catches exact matches of the full secret value — printing even a slice or transformation of a secret can leak it in plain text.

## Future Improvements

- Deploy this application to AWS EC2 via Terraform, extending the pipeline with a CD stage (Project 2).
- Push built Docker images to a container registry (e.g. Docker Hub or Amazon ECR) as part of CI, tagged by commit SHA.
- Add a production-grade WSGI server (e.g. Gunicorn) instead of Flask's built-in development server.
- Add code coverage reporting to the test step.
