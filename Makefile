PYTHON ?= python3

.PHONY: validate lint test report

validate:
	$(PYTHON) scripts/validate_repo.py validate

lint:
	$(PYTHON) scripts/validate_repo.py lint

test:
	$(PYTHON) scripts/validate_repo.py test

report:
	$(PYTHON) scripts/generate_report.py
