PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: bootstrap check preview assets test

bootstrap:
	./scripts/bootstrap.sh

check:
	PYTHON_BIN=$(PYTHON) ./scripts/check.sh

preview:
	./scripts/preview.sh

assets:
	$(PYTHON) plugins/ocean-robot-wechat/skills/ocean-robot-wechat/scripts/assets.py list

test:
	$(PYTHON) -m unittest discover -s plugins/ocean-robot-wechat/skills/ocean-robot-wechat/tests -v
