PY ?= python3
IN ?= models/baseline.json
OUT ?= results/baseline.result.json
MARGIN ?= 0.30

.PHONY: run example check dirs test install build wheel show clean

dirs:
	mkdir -p models results

check: dirs
	@test -f epc_model.py || (echo "Missing epc_model.py"; exit 1)
	@test -f $(IN) || (echo "Missing $(IN). Create it under models/"; exit 1)

run: check
	$(PY) epc_model.py --in $(IN) --out $(OUT) --margin $(MARGIN) --strict
	@echo "Wrote $(OUT)"

example: dirs
	$(PY) epc_model.py --in model_example.json --out results/example.result.json --margin $(MARGIN) --strict
	@echo "Wrote results/example.result.json"

test:
	$(PY) -m unittest -v

install:
	$(PY) -m pip install -e .

build:
	$(PY) -m build

wheel:
	$(PY) -m pip install build
	$(PY) -m build

show:
	@test -f $(OUT) || (echo "Nothing to show; run 'make run' first." && exit 1)
	cat $(OUT)

clean:
	rm -rf __pycache__ *.egg-info build dist results/*.json
