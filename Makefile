format:
	poetry run isort .
	poetry run black .

check:
	poetry run isort . --check
	poetry run flake8 .
	poetry run black . --check

tests: tests_python

tests_python:
	poetry run pytest