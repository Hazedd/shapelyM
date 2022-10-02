install:
	python -m pip install --upgrade pip
	pip install flit
	flit install --deps develop

test:
	pytest --cov=shapelyM/ --cov-report=term-missing --cov-fail-under=88

lint:
	flake8 ./shapelyM ./tests

typecheck:
	mypy shapelyM/

format-check: isort-src-check
	black --check .

format: isort-src
	black .

isort-src-check:
	isort --check-only ./shapelyM ./tests

isort-src:
	isort ./shapelyM ./tests

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

build-wheel:
	flit build

check-all:
	make test
	make typecheck
	make format
	make lint
	mkdocs build
