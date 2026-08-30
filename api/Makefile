lint:
	ruff check . --fix

format:
	ruff format .

check: lint format

test:
	pytest -s -v app/test/unit -m unit

test-e2e:
	pytest -s -v app/test/e2e -m e2e
