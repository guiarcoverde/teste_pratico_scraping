# 🧪 Guia de Testes - TRF5 Scraper

Este guia explica como executar e criar testes para o projeto.

## 📋 Índice

- [Estrutura de Testes](#estrutura-de-testes)
- [Instalação](#instalação)
- [Executando os Testes](#executando-os-testes)
- [Cobertura de Código](#cobertura-de-código)
- [Tipos de Testes](#tipos-de-testes)
- [Criando Novos Testes](#criando-novos-testes)

## 📁 Estrutura de Testes

```
tests/
├── __init__.py
├── test_items.py           # Testes dos Items e processadores
├── test_spider.py          # Testes do spider
├── test_pipelines.py       # Testes do pipeline MongoDB
├── test_middlewares.py     # Testes dos middlewares
├── test_integration.py     # Testes de integração
└── run_tests.py           # Script para executar testes
```

## 📦 Instalação

### 1. Instale as dependências de teste

```bash
# Ative o ambiente virtual primeiro
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instale dependências de teste
pip install -r requirements-test.txt
```

### 2. Verifique a instalação

```bash
pytest --version
coverage --version
```

## ▶️ Executando os Testes

### Usando unittest (built-in Python)

```bash
# Executar todos os testes
python -m unittest discover tests

# Executar um arquivo específico
python -m unittest tests.test_items

# Executar uma classe específica
python -m unittest tests.test_items.TestCleanFunctions

# Executar um teste específico
python -m unittest tests.test_items.TestCleanFunctions.test_clean_numero_processo_with_prefix

# Com verbose
python -m unittest discover tests -v
```

### Usando pytest (recomendado)

```bash
# Executar todos os testes
pytest

# Com verbose
pytest -v

# Executar arquivo específico
pytest tests/test_items.py

# Executar classe específica
pytest tests/test_items.py::TestCleanFunctions

# Executar teste específico
pytest tests/test_items.py::TestCleanFunctions::test_clean_numero_processo_with_prefix

# Executar com output detalhado
pytest -vv

# Parar no primeiro erro
pytest -x

# Executar último teste falhado
pytest --lf

# Modo quiet (menos verbose)
pytest -q
```

### Usando o script personalizado

```bash
# Todos os testes
python tests/run_tests.py

# Arquivo específico
python tests/run_tests.py test_items.py
```

### Com Docker

```bash
# Executar testes dentro do container
docker-compose run --rm spider python -m pytest

# Com coverage
docker-compose run --rm spider python -m pytest --cov=trf_scraper
```

## 📊 Cobertura de Código

### Gerar relatório de cobertura

```bash
# Executar testes com cobertura
pytest --cov=trf_scraper --cov-report=html

# Abrir relatório HTML (Windows)
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Relatório no terminal

```bash
# Relatório simples
pytest --cov=trf_scraper

# Relatório com linhas faltantes
pytest --cov=trf_scraper --cov-report=term-missing

# Apenas relatório (sem output de testes)
pytest --cov=trf_scraper --cov-report=term --quiet
```

### Cobertura mínima

```bash
# Falhar se cobertura for menor que 80%
pytest --cov=trf_scraper --cov-fail-under=80
```

## 🧪 Tipos de Testes

### 1. Testes Unitários (test_items.py)

Testam funções individuais e processadores de dados:

```python
def test_clean_numero_processo_with_prefix(self):
    result = clean_numero_processo("PROCESSO Nº 0015648-78.1999.4.05.0000")
    self.assertEqual(result, "0015648-78.1999.4.05.0000")
```

**Executar**:
```bash
pytest tests/test_items.py -v
```

### 2. Testes do Spider (test_spider.py)

Testam o spider e suas funções:

```python
def test_validate_numero_processo_valid(self):
    result = self.spider._validate_numero_processo("0015648-78.1999.4.05.0000")
    self.assertTrue(result)
```

**Executar**:
```bash
pytest tests/test_spider.py -v
```

### 3. Testes do Pipeline (test_pipelines.py)

Testam salvamento no MongoDB:

```python
def test_process_item_insert(self, mock_mongo_client):
    # Testa inserção de novo item no MongoDB
    ...
```

**Executar**:
```bash
pytest tests/test_pipelines.py -v
```

### 4. Testes de Middlewares (test_middlewares.py)

Testam middlewares customizados:

```python
def test_process_response_logs_time(self):
    # Testa que tempo de resposta é logado
    ...
```

**Executar**:
```bash
pytest tests/test_middlewares.py -v
```

### 5. Testes de Integração (test_integration.py)

Testam fluxo completo do sistema:

```python
def test_spider_parse_processo_integration(self):
    # Testa parsing completo de um processo
    ...
```

**Executar**:
```bash
pytest tests/test_integration.py -v
```

## ✍️ Criando Novos Testes

### Template básico

```python
import unittest
from unittest.mock import Mock, patch

from trf_scraper.items import ProcessoItem


class TestMinhaFuncionalidade(unittest.TestCase):
    """Descrição dos testes"""
    
    def setUp(self):
        """Executado antes de cada teste"""
        self.spider = Mock()
        self.spider.logger = Mock()
    
    def tearDown(self):
        """Executado após cada teste"""
        pass
    
    def test_algo_especifico(self):
        """Testa algo específico"""
        # Arrange (preparar)
        valor_entrada = "teste"
        
        # Act (executar)
        resultado = funcao_testada(valor_entrada)
        
        # Assert (verificar)
        self.assertEqual(resultado, "esperado")
```

### Usando Mocks

```python
from unittest.mock import Mock, patch, MagicMock

# Mock simples
mock_obj = Mock()
mock_obj.metodo.return_value = "valor"

# Mock com side_effect (exceção)
mock_obj.metodo.side_effect = Exception("Erro")

# Patch de função
@patch('modulo.funcao')
def test_com_patch(self, mock_funcao):
    mock_funcao.return_value = "mockado"
    # ...

# Context manager
with patch('modulo.funcao') as mock_funcao:
    mock_funcao.return_value = "mockado"
    # ...
```

### Testando com Scrapy

```python
from scrapy.http import HtmlResponse

# Criar response mock
html = '<html><body>Test</body></html>'
response = HtmlResponse(
    url='http://example.com',
    body=html.encode('utf-8')
)

# Testar seletores
resultado = response.xpath('//body/text()').get()
self.assertEqual(resultado, 'Test')
```

## 🎯 Boas Práticas

### 1. Nomenclatura

- **Arquivos**: `test_*.py`
- **Classes**: `Test*`
- **Métodos**: `test_*`

```python
# test_spider.py
class TestProcessoSpider:
    def test_validate_numero_processo(self):
        ...
```

### 2. Organize por funcionalidade

```python
class TestCleanFunctions:
    """Testa funções de limpeza"""
    
    def test_clean_numero_processo_with_prefix(self):
        ...
    
    def test_clean_numero_processo_without_prefix(self):
        ...
```

### 3. Use subTest para múltiplos casos

```python
def test_clean_cnpj(self):
    test_cases = [
        ("12.345.678/0001-90", "12345678000190"),
        ("12345678000190", "12345678000190"),
    ]
    for input_val, expected in test_cases:
        with self.subTest(input_val=input_val):
            result = clean_cnpj(input_val)
            self.assertEqual(result, expected)
```

### 4. Documente seus testes

```python
def test_processo_item_loader(self):
    """
    Testa que o ItemLoader processa corretamente
    os campos do ProcessoItem, aplicando os
    processadores de entrada e saída.
    """
    ...
```

### 5. Teste casos extremos

```python
def test_clean_numero_processo_none(self):
    """Testa valor None"""
    result = clean_numero_processo(None)
    self.assertIsNone(result)

def test_clean_numero_processo_empty(self):
    """Testa string vazia"""
    result = clean_numero_processo("")
    self.assertEqual(result, "")
```

## 🐛 Debugging de Testes

### Print debugging

```bash
# pytest captura prints por padrão, use -s para ver
pytest tests/test_items.py -s
```

### Breakpoint

```python
def test_algo(self):
    valor = funcao()
    breakpoint()  # Python 3.7+
    # ou
    import pdb; pdb.set_trace()  # Python < 3.7
    self.assertEqual(valor, esperado)
```

### Verbose output

```bash
# Muito verbose
pytest -vv

# Com traceback completo
pytest --tb=long
```

### Ver warnings

```bash
pytest -v --tb=short -W all
```

## 📈 Métricas de Qualidade

### Cobertura desejada

- **Mínimo**: 70%
- **Bom**: 80%
- **Excelente**: 90%+

### Verificar cobertura

```bash
pytest --cov=trf_scraper --cov-report=term-missing
```

### Arquivos com baixa cobertura

```bash
coverage report --show-missing
```

## 🔄 CI/CD

### GitHub Actions (exemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=trf_scraper --cov-fail-under=70
```

## 📚 Recursos

- [pytest documentation](https://docs.pytest.org/)
- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [Mock documentation](https://docs.python.org/3/library/unittest.mock.html)

## 🆘 Troubleshooting

### Erro: ModuleNotFoundError

```bash
# Adicione o diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH="$(pwd)"  # Windows PowerShell

# Ou execute com -m
python -m pytest tests/
```

### Testes lentos

```bash
# Ver duração dos testes
pytest --durations=10

# Executar em paralelo (requer pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

### Limpar cache

```bash
# Limpar cache do pytest
pytest --cache-clear

# Limpar __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +  # Linux/Mac
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force  # PowerShell
```

---

**Desenvolvido com 🧪 usando pytest e unittest**
