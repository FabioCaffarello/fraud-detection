# Use bash for shell commands
SHELL := /bin/bash

# Directories
VENV_DIR := .venv
VENV_BIN_DIR := $(VENV_DIR)/bin
SCRIPTS_DIR := scripts
SETUP_SCRIPT := $(SCRIPTS_DIR)/setup.sh

# Commands (allow PYTHON to be overridden if needed)
PYTHON ?= uv
SHELL_CMD := source
PRE_COMMIT := pre-commit
DOCKER_COMPOSE := docker compose

.PHONY: help setup install precommit clean lint lint-docstrings run stop build-docs serve-docs deploy-docs

help:
	@echo "Available targets:"
	@echo "  setup            - Run project setup script"
	@echo "  install          - Create virtual environment (if needed), install dependencies, and set up pre-commit hooks"
	@echo "  precommit        - Run pre-commit checks on all files"
	@echo "  clean            - Remove Python caches and temporary files"
	@echo "  lint             - Lint code using Ruff"
	@echo "  lint-docstrings  - Lint docstrings using pydocstyle"
	@echo "  build-docs       - Build documentation and start PlantUML server"
	@echo "  run 			  - Run the application"
	@echo "  stop 			  - Stop the application"
	@echo "  serve-docs       - Serve documentation locally"
	@echo "  deploy-docs      - Deploy documentation to GitHub Pages"

setup:
	@chmod +x $(SCRIPTS_DIR)/init-multiple-dbs.sh
	@chmod +x $(SCRIPTS_DIR)/wait-for-it.sh
	@chmod +x $(SETUP_SCRIPT)
	@$(SETUP_SCRIPT)

install:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating virtual environment..."; \
		$(PYTHON) venv $(VENV_DIR); \
	fi
	$(SHELL_CMD) $(VENV_BIN_DIR)/activate && \
	$(PYTHON) sync --all-groups --all-extras && \
	$(PRE_COMMIT) install --hook-type commit-msg && \
	$(PRE_COMMIT) install --hook-type pre-commit

precommit:
	$(PRE_COMMIT) run --all-files

clean:
	@echo "Cleaning up cache directories and temporary files..."
	@find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" \) -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete."

## Lint code using Ruff
lint:
	$(PYTHON) run ruff check $(SRC_DIR) $(PACKAGES_DIR) $(TEST_DIR)

lint-docstrings:
	$(PYTHON) run pydoclint --style=google --check-return-types=false --exclude=.venv .

build-docs:
	@echo "Building documentation..."
	@npx nx graph --file=docs/dependency-graph/index.html
	@docker run -d -p 8080:8080 plantuml/plantuml-server:jetty

lint:
	npx nx run-many --target=lint --all

serve-docs: build-docs
	@echo "Serving documentation..."
	$(PYTHON) run -- python -m mkdocs serve

deploy-docs: build-docs
	$(PYTHON) run -- python -m mkdocs gh-deploy

run:
	$(DOCKER_COMPOSE) --profile flower up -d --build

stop:
	$(DOCKER_COMPOSE) --profile flower down --remove-orphans -v
