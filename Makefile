VERSION = 0.1
PYTHON  = python3.8

init:
	pip install -r requirements.txt

run_test:
	$(PYTHON) -m pytest $(TEST) --verbose -s

run_tests:
	$(PYTHON) -m pytest tests --verbose -s

run_experiment:
	$(PYTHON) -m pytest $(EXPERIMENT) --verbose -s

run_experiments:
	$(PYTHON) -m pytest experiments --verbose -s

.PHONY: init run_test
