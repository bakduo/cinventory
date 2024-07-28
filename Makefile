build:
	pipenv run python setup.py sdist
	pipenv run twine check dist/*
build2:
	rm -f dist/*
	pipenv check
	pipenv run pytest tests --cov
	pipenv run black tests/ src/
	pipenv run flake8
	pipenv requirements > requirements-prod.txt
	pipenv requirements --dev> requirements-dev.txt
	pandoc --from=markdown --to=rst --output=README.rst README.md
	pandoc --from=markdown --to=rst --output=CHANGES.rst CHANGES.md
	python -m build
	pipenv run twine check dist/*
test:
	pytest
testinstall:
	pipenv install -e .
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
all-requeriments-env:
	pipenv run pip freeze > all-env-requeriments.txt
convertorst:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	pandoc --from=markdown --to=rst --output=CHANGES.rst CHANGES.md
uploadtestrepo:
	pipenv run twine upload --repository testpypi --verbose dist/*

uploadprodrepo:
	pipenv run twine upload --repository pypi --verbose dist/*
security:
	bandit -r src/ --format custom