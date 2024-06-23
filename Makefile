build:
	pipenv run python setup.py sdist
test:
	pytest
coverage:
	pipenv run pytest tests --cov
checkcode:
	pipenv run flake8
cleancode:
	pipenv run black tests/ src/
check:
	pipenv check
requeriments:
	pipenv requirements > requirements-prod.txt
	pipenv requirements --dev> requirements-dev.txt