.PHONY: install test clean build publish lint

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

test-install:
	python tests/test_install.py

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

build: clean
	python -m build

publish: build
	twine upload dist/*

lint:
	python -m py_compile olapp/__init__.py
	python -m py_compile olapp/components.py
	python -m py_compile olapp/interface.py
	python -m py_compile olapp/blocks.py
	python -m py_compile olapp/server.py
	python -m py_compile olapp/routes.py
	python -m py_compile olapp/utils.py

run:
	python examples/hello.py
