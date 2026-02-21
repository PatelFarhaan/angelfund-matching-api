.PHONY: install run test clean docker-build docker-run

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python app.py

test:
	. venv/bin/activate && python -m pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf venv

docker-build:
	docker build -t angelfund-api .

docker-run:
	docker run -p 5000:5000 --env-file .env angelfund-api
