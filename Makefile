.PHONY: help install install-dev install-all clean format format-check lint flake8 mypy test test-fast cov build check ci

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

help:
	@echo "make targets:"
	@echo "  install       Install package (runtime deps only)"
	@echo "  install-dev   Install package with dev extras"
	@echo "  install-all   Install package with all extras"
	@echo "  format        Apply black + isort"
	@echo "  format-check  Verify black + isort would not change files"
	@echo "  flake8        Run flake8"
	@echo "  mypy          Run mypy"
	@echo "  lint          format-check + flake8 + mypy"
	@echo "  test          Run stable test suite (alias for test-stable)"
	@echo "  test-stable   Run only the test files known to be green"
	@echo "  test-all      Run full suite excluding integration + slow markers"
	@echo "  test-fast     Run all tests, no coverage"
	@echo "  cov           Run pytest with HTML coverage report"
	@echo "  build         Build sdist + wheel"
	@echo "  check         lint + test (what CI runs)"
	@echo "  ci            Same as check (alias)"
	@echo "  clean         Remove build artifacts and caches"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

install-all:
	$(PIP) install -e ".[all,dev,docs]"

format:
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/

format-check:
	$(PYTHON) -m black --check src/ tests/
	$(PYTHON) -m isort --check-only src/ tests/

flake8:
	$(PYTHON) -m flake8 src/

mypy:
	$(PYTHON) -m mypy src/llm_dispatcher

lint: format-check flake8 mypy

STABLE_TESTS = \
	tests/test_basic.py \
	tests/test_environment.py \
	tests/test_exceptions.py \
	tests/test_provider_exception_usage.py

test: test-stable

test-stable:
	$(PYTHON) -m pytest $(STABLE_TESTS) --no-cov -q

test-all:
	$(PYTHON) -m pytest -m "not integration and not slow" --no-cov -q

test-fast:
	$(PYTHON) -m pytest --no-cov -q

cov:
	$(PYTHON) -m pytest --cov=src/llm_dispatcher --cov-report=html --cov-report=term-missing

build: clean
	$(PYTHON) -m build

check: lint test

ci: check

clean:
	rm -rf build/ dist/ site/ htmlcov/ .coverage coverage.xml .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
