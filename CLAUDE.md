# CLAUDE.md

## Development guidelines

### API

- Run `just gen-api` if there have been API changes.

### Web

- Use HeroUI components whenever possible.
- Prefer defining single-file components.
- Make use of tailwindcss, tailwind-merge, tailwind-variants.
- Use openapi-fetch with the generated schemas from FastAPI.

### General
- Lint and format after finishing modifying source code.
  - Use the justfile commands.
  - If only typescript has been modified, run only the format and lintingn for typescript
  - If only backend has been modified, run only the format and linting for python
  - If both are modified. Format and lint everything


## justfile commands
```bash
Available recipes:
    build            # Build both apps
    build-api        # Build Python package
    build-web        # Build frontend for production
    check            # Run all checks (lint + format)
    clean            # Clean build artifacts
    default          # List available commands
    dev              # Run API + frontend dev servers
    dev-api          # Run FastAPI backend with reload
    dev-web          # Run Vite frontend
    format           # Format both apps
    format-api       # Format Python with ruff
    format-check     # Check formatting without changes
    format-check-api # Check Python formatting
    format-check-web # Check frontend formatting
    format-web       # Format frontend with prettier
    gen-api          # Generate TypeScript types from OpenAPI
    install          # Install all dependencies
    install-api      # Install Python dependencies
    install-web      # Install frontend dependencies
    lint             # Lint both apps
    lint-api         # Lint Python with ruff
    lint-web         # Lint frontend with eslint
```
