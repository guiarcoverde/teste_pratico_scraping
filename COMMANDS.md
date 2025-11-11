# TRF5 Scraper - Comandos Rápidos

## Comandos PowerShell (Windows)

```powershell
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt

# Executar testes
python -m pytest tests/ -v

# Testes com cobertura
python -m pytest tests/ --cov=trf_scraper --cov-report=html

# Limpar arquivos temporários
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory .pytest_cache | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force htmlcov, .coverage -ErrorAction SilentlyContinue

# Docker
docker-compose up -d
docker-compose down
docker-compose run --rm spider python -m pytest tests/ -v
```

## Comandos Bash (Linux/Mac)

```bash
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-test.txt

# Executar testes
python -m pytest tests/ -v

# Testes com cobertura
python -m pytest tests/ --cov=trf_scraper --cov-report=html

# Limpar arquivos temporários
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
rm -rf htmlcov/ .coverage

# Docker
docker-compose up -d
docker-compose down
docker-compose run --rm spider python -m pytest tests/ -v

# Usando Makefile
make install-test
make test
make test-cov
make clean
```
