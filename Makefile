.PHONY: help install install-test test test-cov test-fast lint clean docker-up docker-down docker-test

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instalar dependências do projeto"
	@echo "  make install-test  - Instalar dependências de teste"
	@echo "  make test          - Executar todos os testes"
	@echo "  make test-cov      - Executar testes com cobertura"
	@echo "  make test-fast     - Executar testes rapidamente"
	@echo "  make lint          - Verificar código com linters"
	@echo "  make clean         - Limpar arquivos temporários"
	@echo "  make docker-up     - Iniciar containers Docker"
	@echo "  make docker-down   - Parar containers Docker"
	@echo "  make docker-test   - Executar testes no Docker"

install:
	pip install -r requirements.txt

install-test:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=trf_scraper --cov-report=html --cov-report=term

test-fast:
	python -m pytest tests/ -x -v

lint:
	flake8 trf_scraper --max-line-length=127
	pylint trf_scraper || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose run --rm spider python -m pytest tests/ -v
