set dotenv-load

# Project root directory (can be overridden via .env or env var)
export YUBAL_ROOT := justfile_directory()

default:
    @just --list

# Install
install: install-py install-web
install-py:
    uv sync --all-packages

install-web:
    cd web && bun install

# Dev servers
dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    just dev-api & just dev-web & wait
dev-api:
    uv run uvicorn yubal_api.api.app:app --reload
dev-web:
    cd web && bun run dev

# Lint
lint: lint-py lint-web
lint-py:
    uv run ruff check packages
lint-web:
    cd web && bun run lint

# Lint fix
lint-fix: lint-fix-py lint-fix-web
lint-fix-py:
    uv run ruff check packages --fix
lint-fix-web:
    cd web && bun run lint --fix

# Format
format: format-py format-web
format-py:
    uv run ruff format packages
format-web:
    cd web && bun run format

# Format check
format-check: format-check-py format-check-web
format-check-py:
    uv run ruff format --check packages
format-check-web:
    cd web && bun run format:check

# Typecheck
typecheck: typecheck-py typecheck-web
typecheck-py:
    uv run ty check packages
typecheck-web:
    cd web && bun run typecheck

# Tests
test: test-py test-web
test-py:
    uv run pytest packages
test-web:
    cd web && bun run test

# Utils
gen-api:
    cd web && bun run generate-api

# CI
check: format-check lint typecheck test

# Docker
docker-build:
    docker build --no-cache -t yubal:local .

docker-check-size:
    docker build --no-cache -t yubal:check-size .
    docker images yubal:check-size | awk 'NR==2 {print "📦 Image size: " $7}'
    docker rmi yubal:check-size
    @echo '✅ Docker build successful!'

# yubal CLI
cli *args:
    uv run yubal {{ args }}
