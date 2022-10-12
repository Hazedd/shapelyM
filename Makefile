install:
	python -m pip install --upgrade pip
	pip install flit
	flit install --deps develop

test:
	pytest --cov=shapelyM/ --cov-report=term-missing --cov-fail-under=90

lint:
	flake8 ./shapelyM ./tests

typecheck:
	mypy shapelyM/ --show-traceback

format-check: isort-src-check
	black --check .

format: isort-src
	black .

isort-src-check:
	isort --check-only ./shapelyM ./tests

isort-src:
	isort ./shapelyM ./tests

bumpversion-release:
	bumpversion release

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

bumpversion-build:
	bumpversion build

build-wheel:
	flit build

check-all:
	make test
# 	make typecheck
	make format
	make lint
# 	mkdocs build
