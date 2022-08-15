.DEFAULT_GOAL := help
.PHONY: coverage deps help lint test

coverage:  ## Run tests with coverage
	python -m coverage erase
	python -m coverage run --include=goifer/* -m pytest -ra
	python -m coverage report -m

deps:  ## Install dependencies
	python -m pip install --upgrade pip
	python -m pip install flit
	python -m flit install -s

lint:  ## Linting of source code
	python -m flake8 --statistics --show-source .
	python -m black . --check

format: ## Format code using the code formatter
	python -m black .

test:  ## Run tests
	python -m pytest --cov=goifer tests/

ci: lint test  # Validate package with CI/CD

help: SHELL := /bin/bash
help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
