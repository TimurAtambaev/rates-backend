format:
	poetry run isort rates/
	poetry run black rates/

check:
	poetry run isort rates --check
	poetry run flake8 rates
	poetry run black rates --check