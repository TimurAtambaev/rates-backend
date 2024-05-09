format:
	poetry run isort api/
	poetry run black api/

check:
	poetry run isort api --check
	poetry run flake8 api
	poetry run black api --check

tests: tests_python

tests_python:
	poetry run pytest