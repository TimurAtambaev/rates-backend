format:
	poetry run isort api/
	poetry run black api/
	poetry run isort rates/
	poetry run black rates/
	poetry run isort tests/
	poetry run black tests/

check:
	poetry run isort api --check
	poetry run flake8 api
	poetry run black api --check
	poetry run isort rates --check
	poetry run flake8 rates
	poetry run black rates --check
	poetry run isort tests --check
	poetry run flake8 tests
	poetry run black tests --check

tests: tests_python

tests_python:
	poetry run pytest