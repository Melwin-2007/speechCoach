.PHONY: setup test check smoke app app-prod dataset eval

setup:
	pip install -r requirements.txt
	cd app && npm install

test:
	pytest tests/

check:
	pytest tests/
	cd app && npm run lint:design
	bash scripts/smoke.sh

smoke:
	bash scripts/smoke.sh

dataset:
	python scripts/build_dataset.py

eval:
	python scripts/run_eval.py --split dev

app:
	@echo "Starting API on port 8000..."
	python -m uvicorn --app-dir src speechcoach.api.main:app --port 8000 --reload &
	@echo "Starting Vite dev server..."
	cd app && npm run dev

app-prod:
	cd app && npm run build
	python -m uvicorn --app-dir src speechcoach.api.main:app --host 0.0.0.0 --port 7860
