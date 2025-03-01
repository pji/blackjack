.PHONY: build
build:
	# sphinx-build -b html docs/source/ docs/build/html
	python -m build
	# twine check dist/*

.PHONY: clean
clean:
	rm -rf docs/build/html
	rm -rf dist
	rm -rf src/blackjack.egg-info
	rm -rf tests/__pycache__
	rm -rf tests/*.pyc
	rm -rf src/blackjack/__pycache__
	rm -rf src/blackjack/*.pyc
	rm -f *.log
	rm -f *.json

.PHONY: docs
docs:
	rm -rf docs/build/html
	sphinx-build -b html docs/source/ docs/build/html

.PHONY: pre
pre:
	python precommit.py
	git status

.PHONY: test
test:
	python -m pytest --capture=sys


.PHONY: testv
testv:
	python -m pytest -vv  --capture=sys
