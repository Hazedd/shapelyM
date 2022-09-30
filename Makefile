install:
	python -m pip install --upgrade pip
	pip install flit
	flit install --deps develop

test:
	pytest --cov=shapelyM/ --cov-report=term-missing --cov-fail-under=70

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

build-wheel:
	flit build


# isort-src:
# 	isort ./pyImx ./tests
#
# isort-docs:
# 	isort ./docs/src -o pyImxs
#
# isort-examples:
# 	isort ./examples -o pyImx -p app
#
# format: isort-src isort-docs isort-examples
# 	black .
#
# isort-src-check:
# 	isort --check-only ./pyImx ./tests
#
# isort-docs-check:
# 	isort --check-only ./docs/src -o pyImx
#
# isort-examples-check:
# 	isort --check-only ./examples -o pyImx -p app
#
# format-check: isort-src-check isort-docs-check isort-examples-check
# 	black --check .
#
# lint:
# 	flake8 ./pyImx ./tests
#
# typecheck:
# 	mypy pyImx/
#


# check-all:
# 	make test
# 	make lint
# 	make typecheck
# 	mkdocs build
