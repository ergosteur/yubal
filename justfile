# Run `just` to see available commands

set dotenv-load

default:
    @just --list

dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    just dev-api &
    just dev-web &
    wait

dev-api:
    uv run yubal serve --reload

dev-web:
    cd web && bun run dev

## build

build: build-api build-web

build-api:
    uv build

build-web:
    cd web && bun run build

## lint

lint: lint-api lint-web

lint-api:
    uv run ruff check .

lint-web:
    cd web && bun run lint

## format

format: format-api format-web

format-api:
    uv run ruff check . --fix
    uv run ruff format .

format-web:
    cd web && bun run lint:fix
    cd web && bun run format

format-check: format-check-api format-check-web

format-check-api:
    uv run ruff format --check .

format-check-web:
    cd web && bun run format:check

## generate api

gen-api:
    cd web && bun run generate-api

# Run all checks

check: lint format-check

## install

# Install all dependencies
install: install-api install-web

# Install Python dependencies
install-api:
    uv sync

# Install web dependencies
install-web:
    cd web && bun install

# Clean build artifacts
clean:
    rm -rf dist/ .pytest_cache/ .ruff_cache/
    rm -rf web/dist/ web/node_modules/.vite/
