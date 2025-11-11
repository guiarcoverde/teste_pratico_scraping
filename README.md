# TRF5 Scraper - Sistema de Extração de Processos Judiciais

Sistema profissional de web scraping desenvolvido com Scrapy para extrair dados de processos judiciais do Tribunal Regional Federal da 5ª Região (TRF5). O sistema coleta informações detalhadas de processos, incluindo dados principais, partes envolvidas e histórico de movimentações, armazenando tudo de forma estruturada no MongoDB.

## 📋 Índice

- [Características](#características)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
  - [Instalação com Docker (Recomendado)](#instalação-com-docker-recomendado)
  - [Instalação Local](#instalação-local)
- [Configuração](#configuração)
- [Uso](#uso)
  - [Exemplos Práticos](#exemplos-práticos)
- [Arquitetura](#arquitetura)
- [Estrutura dos Dados](#estrutura-dos-dados)
- [Monitoramento e Logs](#monitoramento-e-logs)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)
- [Boas Práticas](#boas-práticas)

## ✨ Características

### Funcionalidades Principais

- ✅ **Busca por Número de Processo**: Suporta um ou múltiplos processos (separados por vírgula)
- ✅ **Busca por CNPJ**: Extrai automaticamente todos os processos relacionados a um CNPJ
- ✅ **Extração Completa de Dados**:
  - Informações básicas do processo (número, número legado, data de autuação)
  - Partes envolvidas (advogados, procuradores, apelantes, etc.)
  - Histórico completo de movimentações com datas
- ✅ **Persistência MongoDB**: 
  - Pipeline otimizado com operação upsert (insert ou update automático)
  - Índice único por número de processo
  - Timestamps de criação e atualização
- ✅ **Exportação JSON**: Salva dados localmente em formato JSON
- ✅ **Monitoramento Avançado**:
  - Middleware de tracking de tempo de resposta
  - Log detalhado de erros com salvamento de HTML para debug
  - Estatísticas de execução (itens processados, tempo decorrido, etc.)
- ✅ **Resiliência e Confiabilidade**:
  - AutoThrottle para ajuste automático de velocidade
  - Sistema de retry configurável para requisições falhadas
  - Validação de números de processo
  - Tratamento robusto de erros
- ✅ **Ambiente Dockerizado**: Stack completa com MongoDB e spider pré-configurados

## 🛠 Tecnologias Utilizadas

- **Python 3.10+**: Linguagem principal
- **Scrapy 2.11+**: Framework de web scraping
- **MongoDB 8.2.1**: Banco de dados NoSQL para armazenamento
- **PyMongo 4.6+**: Driver Python para MongoDB
- **Docker & Docker Compose**: Containerização e orquestração
- **ItemLoaders**: Processamento e limpeza de dados
- **python-dateutil**: Parsing de datas

## 🔧 Requisitos

### Sistema Operacional
- Windows 10/11, Linux ou macOS

### Software Necessário

#### Para execução com Docker (Recomendado)
- **Docker Engine**: 20.10 ou superior
- **Docker Compose**: 2.0 ou superior

#### Para execução local
- **Python**: 3.8 ou superior (recomendado 3.10+)
- **MongoDB**: 4.0 ou superior (ou usar MongoDB via Docker)
- **pip**: Gerenciador de pacotes Python

### Dependências Python

Todas as dependências estão listadas em `requirements.txt`:
```
scrapy>=2.11.0
pymongo>=4.6.0
w3lib>=2.1.2
python-dateutil>=2.8.2
itemloaders>=1.1.0
```

## 📦 Instalação

### Instalação com Docker (Recomendado)

A forma mais rápida e fácil de executar o projeto! O Docker gerencia automaticamente o MongoDB e todas as dependências.

#### Opção 1: Início Rápido

```bash
# Clone o repositório
git clone <repository-url>
cd teste_pratico_scraping

# Inicie toda a stack (MongoDB + Spider)
docker-compose up
```

Isso irá:
1. Baixar as imagens necessárias (MongoDB 8.2.1 e Python 3.10)
2. Criar os containers
3. Configurar o MongoDB com autenticação
4. Aguardar o MongoDB ficar saudável
5. Deixar o spider pronto para execução

#### Opção 2: Usando o Script de Quick Start

```bash
# Linux/Mac
chmod +x docker-quickstart.sh
./docker-quickstart.sh

# Windows (PowerShell)
.\docker-quickstart.sh
```

#### Executar o Spider com Docker

```bash
# Buscar por número de processo
docker-compose run --rm spider scrapy crawl processo -a processos="00156487819994050000"

# Buscar por CNPJ
docker-compose run --rm spider scrapy crawl processo -a cnpj="12.345.678/0001-90"

# Múltiplos processos
docker-compose run --rm spider scrapy crawl processo -a processos="00156487819994050000,00234567890123456789"
```

**📖 Consulte a [Documentação completa do Docker](DOCKER.md) para mais detalhes e comandos avançados.**

### Instalação Local

Para desenvolvedores que preferem executar diretamente no sistema operacional.

#### 1. Clone o Repositório

```bash
git clone <repository-url>
cd teste_pratico_scraping
```

#### 2. Crie e Ative o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar no Windows (CMD)
.\venv\Scripts\activate.bat

# Ativar no Linux/Mac
source venv/bin/activate
```

#### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure o MongoDB

**Opção A: MongoDB via Docker (Recomendado para desenvolvimento local)**

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=1234 \
  mongo:8.2.1

# Windows PowerShell
docker run -d `
  --name mongodb `
  -p 27017:27017 `
  -e MONGO_INITDB_ROOT_USERNAME=admin `
  -e MONGO_INITDB_ROOT_PASSWORD=1234 `
  mongo:8.2.1
```

**Opção B: Instalação Local do MongoDB**

1. Baixe o MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Siga as instruções de instalação para seu sistema operacional
3. Inicie o serviço MongoDB

#### 5. Verifique a Instalação

```bash
# Teste a conexão com MongoDB
python verify_mongodb.py

# Liste os spiders disponíveis
scrapy list

# Deve mostrar: processo
```

## ⚙️ Configuração

### Configurações Principais

As configurações do projeto estão em `trf_scraper/settings.py`.

#### MongoDB

```python
# Conexão com MongoDB
MONGO_URI = "mongodb://admin:1234@localhost:27017/"
MONGO_DATABASE = "trf5_processos"

# Para MongoDB sem autenticação
MONGO_URI = "mongodb://localhost:27017/"
```

#### Rate Limiting e Performance

```python
# Requisições simultâneas
CONCURRENT_REQUESTS = 8

# Delay entre requisições (em segundos)
DOWNLOAD_DELAY = 1

# AutoThrottle - ajuste automático de velocidade
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10

# Tentativas de retry em caso de erro
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
```

#### Middlewares

```python
DOWNLOADER_MIDDLEWARES = {
    'trf_scraper.middlewares.ResponseTimeMiddleware': 543,
    'trf_scraper.middlewares.ErrorLoggingMiddleware': 544,
}
```

#### Pipelines

```python
ITEM_PIPELINES = {
    'trf_scraper.pipelines.MongoDBPipeline': 300,
}
```

### Variáveis de Ambiente (Docker)

Ao usar Docker, você pode sobrescrever configurações via variáveis de ambiente:

```bash
docker-compose run --rm \
  -e MONGO_URI="mongodb://user:pass@host:27017/" \
  -e MONGO_DATABASE="outro_banco" \
  spider scrapy crawl processo -a processos="123"
```

## 🚀 Uso

### Comandos Básicos

#### Busca por Número de Processo

```bash
# Executar localmente
scrapy crawl processo -a processos="00156487819994050000"

# Executar com Docker
docker-compose run --rm spider scrapy crawl processo -a processos="00156487819994050000"
```

#### Busca por CNPJ

```bash
# Executar localmente
scrapy crawl processo -a cnpj="12.345.678/0001-90"

# Executar com Docker
docker-compose run --rm spider scrapy crawl processo -a cnpj="12345678000190"
```

> **Nota**: O CNPJ pode ser informado com ou sem formatação (pontos, barras e traços).

#### Múltiplos Processos

```bash
# Separar processos por vírgula
scrapy crawl processo -a processos="00156487819994050000,00234567890123456789,00987654321098765432"
```

#### Busca Combinada

```bash
# Processos específicos + todos os processos de um CNPJ
scrapy crawl processo \
  -a processos="00156487819994050000,00234567890123456789" \
  -a cnpj="12.345.678/0001-90"
```

#### Exportar para JSON

```bash
# Salva no MongoDB E em arquivo JSON
scrapy crawl processo -a processos="00156487819994050000" -o output.json

# JSON formatado (pretty print)
scrapy crawl processo -a processos="00156487819994050000" -o output.json:json -s FEED_EXPORT_INDENT=2
```

### Níveis de Log

```bash
# INFO - Apenas informações importantes (padrão)
scrapy crawl processo -a processos="..." -L INFO

# DEBUG - Máximo detalhe para debugging
scrapy crawl processo -a processos="..." -L DEBUG

# WARNING - Apenas avisos e erros
scrapy crawl processo -a processos="..." -L WARNING

# ERROR - Apenas erros
scrapy crawl processo -a processos="..." -L ERROR
```

### Salvar Logs em Arquivo

```bash
# Executar localmente com log em arquivo
scrapy crawl processo -a processos="..." --logfile=logs/scraping.log

# Com Docker (logs salvos em ./logs/)
docker-compose run --rm spider \
  scrapy crawl processo -a processos="..." --logfile=/app/logs/scraping.log
```

### Exemplos Práticos

#### Exemplo 1: Extrair um único processo

```bash
scrapy crawl processo -a processos="00156487819994050000" -L INFO
```

**Saída esperada**:
```
[processo] INFO: Spider inicializado - Processos: 1, CNPJ: False
[processo] INFO: Criando request para processo: 00156487819994050000
[processo] INFO: Processando página do processo: https://cp.trf5.jus.br/cp/cp.do
[processo] INFO: Processo inserido: PROCESSO Nº 0015648-78.1999.4.05.0000
[scrapy.core.engine] INFO: Spider closed (finished)
```

#### Exemplo 2: Extrair todos os processos de um CNPJ

```bash
scrapy crawl processo -a cnpj="12.345.678/0001-90" -o processos_empresa.json
```

#### Exemplo 3: Busca combinada com log detalhado

```bash
scrapy crawl processo \
  -a processos="00156487819994050000" \
  -a cnpj="12.345.678/0001-90" \
  -L DEBUG \
  --logfile=logs/busca_completa.log
```

#### Exemplo 4: Verificar dados no MongoDB

```bash
# Use o script Python fornecido
python verify_mongodb.py

# Ou conecte diretamente com mongosh
mongosh "mongodb://admin:1234@localhost:27017/" --authenticationDatabase admin
```

No mongosh:
```javascript
use trf5_processos

// Contar total de processos
db.processos.countDocuments()

// Buscar um processo específico
db.processos.findOne({numero_processo: /0015648/})

// Listar últimos 5 processos inseridos
db.processos.find().sort({created_at: -1}).limit(5)

// Buscar processos por data de extração
db.processos.find({data_extracao: {$gte: "2025-11-01"}})
```

## 🏗️ Arquitetura

### Visão Geral

```
┌─────────────┐
│   Spider    │ Inicia requisições HTTP
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ ResponseTimeMiddleware  │ Monitora tempo de resposta
└──────┬──────────────────┘
       │
       ▼
┌─────────────┐
│  TRF5 Site  │ Responde com HTML
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │ Extrai dados com XPath/CSS
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Items     │ Estrutura e valida dados
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ MongoDBPipeline     │ Salva no banco (upsert)
└─────────────────────┘
       │
       ▼
┌─────────────┐
│  MongoDB    │ Armazenamento persistente
└─────────────┘
```

### Estrutura do Projeto

```
teste_pratico_scraping/
├── trf_scraper/
│   ├── __init__.py
│   ├── items.py              # Definição dos Items (ProcessoItem, EnvolvidoItem, MovimentacaoItem)
│   ├── middlewares.py        # Middlewares customizados
│   │                         # - ResponseTimeMiddleware: monitora tempo de resposta
│   │                         # - ErrorLoggingMiddleware: registra erros
│   ├── pipelines.py          # MongoDBPipeline com lógica de upsert
│   ├── settings.py           # Configurações do Scrapy
│   └── spiders/
│       ├── __init__.py
│       └── processo_spider.py # Spider principal
│
├── logs/                     # Diretório para logs de execução
├── output/                   # Arquivos JSON e HTML de debug
├── docker-compose.yml        # Orquestração Docker
├── Dockerfile                # Imagem do spider
├── docker-entrypoint.sh      # Script de inicialização do container
├── docker-quickstart.sh      # Script de quick start
├── requirements.txt          # Dependências Python
├── scrapy.cfg                # Configuração do projeto Scrapy
├── verify_mongodb.py         # Script para verificar dados no MongoDB
├── DOCKER.md                 # Documentação completa do Docker
└── README.md                 # Este arquivo
```

### Componentes Principais

#### 1. Spider (`processo_spider.py`)

Responsável por:
- Navegar pelo site do TRF5
- Fazer requisições HTTP (GET e POST)
- Extrair dados das páginas HTML
- Gerenciar busca por processo e por CNPJ
- Validar números de processo
- Salvar HTML de debug em caso de erro

**Principais métodos**:
- `start_requests()`: Inicia o processo de scraping
- `parse_form_cnpj()`: Processa o formulário para busca por CNPJ
- `parse_processo()`: Extrai dados de um processo
- `parse_lista_processos()`: Processa lista de processos (busca por CNPJ)
- `_extract_envolvidos()`: Extrai partes envolvidas
- `_extract_movimentacoes()`: Extrai histórico de movimentações

#### 2. Items (`items.py`)

Define a estrutura dos dados extraídos:

```python
ProcessoItem:
    - numero_processo: str
    - numero_legado: str
    - data_autuacao: str
    - url: str
    - data_extracao: datetime
    - envolvidos: List[EnvolvidoItem]
    - movimentacoes: List[MovimentacaoItem]

EnvolvidoItem:
    - papel: str  # Ex: "APTE", "Advogado/Procurador"
    - nome: str

MovimentacaoItem:
    - data: str
    - texto: str
```

#### 3. Middlewares (`middlewares.py`)

- **ResponseTimeMiddleware**: Monitora e loga o tempo de resposta de cada requisição
- **ErrorLoggingMiddleware**: Captura e registra URLs com falha para retry posterior

#### 4. Pipeline (`pipelines.py`)

**MongoDBPipeline** implementa:
- Conexão com MongoDB com autenticação
- Operação **upsert** (insert ou update) baseada em `numero_processo`
- Criação automática de índice único
- Timestamps automáticos (`created_at`, `updated_at`)
- Serialização de datetime e nested items
- Tratamento robusto de erros
- Estatísticas de operações (inseridos, atualizados, erros)

### Fluxo de Execução Detalhado

1. **Inicialização**
   - Spider recebe parâmetros (processos e/ou cnpj)
   - Valida que pelo menos um parâmetro foi fornecido
   - Loga informações de inicialização

2. **Requisições**
   - **Para processos individuais**: Acessa diretamente via GET em `https://cp.trf5.jus.br/processo/{numero}` (mais rápido)
   - **Para CNPJ**: Acessa página inicial do TRF5 e cria FormRequest para buscar lista de processos

3. **Parsing**
   - Extrai dados usando seletores XPath e CSS
   - Usa ItemLoader para processar e limpar dados
   - Valida números de processo (deve ter 20 dígitos)
   - Extrai envolvidos e movimentações como sub-items

4. **Pipeline**
   - Recebe item processado
   - Serializa datetime e nested objects
   - Executa upsert no MongoDB
   - Atualiza estatísticas

5. **Finalização**
   - Fecha conexão com MongoDB
   - Exibe estatísticas finais
   - Salva arquivos JSON (se configurado)

## � Estrutura dos Dados

### Documento MongoDB

Cada processo é armazenado como um documento no MongoDB com a seguinte estrutura:

```json
{
  "_id": ObjectId("..."),
  "numero_processo": "0015648-78.1999.4.05.0000",
  "numero_legado": "(99.05.15648-8)",
  "data_autuacao": "15/04/1999",
  "url": "https://cp.trf5.jus.br/processo/00156487819994050000",
  "data_extracao": "2025-11-11 14:35:54",
  "envolvidos": [
    {
      "papel": "APTE",
      "nome": "MARIA MARLENE GOMES MARQUES(e outros)"
    },
    {
      "papel": "Advogado/Procurador",
      "nome": "JALES DE SENA RIBEIRO - CE006397"
    }
  ],
  "movimentacoes": [
    {
      "data": "15/04/1999 00:00:00",
      "texto": "Processo distribuído."
    },
    {
      "data": "11/09/2021 16:50:00",
      "texto": "Baixa Definitiva - Processo Migrado para o PJe ."
    }
  ],
  "created_at": ISODate("2025-11-11T14:35:54.123Z"),
  "updated_at": ISODate("2025-11-11T14:35:54.123Z")
}
```

### Descrição dos Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `numero_processo` | String | Número completo do processo (limpo, sem prefixos) |
| `numero_legado` | String | Número no formato antigo |
| `data_autuacao` | String | Data de autuação do processo (formato: DD/MM/YYYY ou datetime) |
| `url` | String | URL da página do processo |
| `data_extracao` | String | Data/hora da extração |
| `envolvidos` | Array | Partes envolvidas |
| `envolvidos[].papel` | String | Papel da parte (APTE, APDO, Advogado/Procurador, RELATOR, etc.) |
| `envolvidos[].nome` | String | Nome da parte |
| `movimentacoes` | Array | Histórico de movimentações |
| `movimentacoes[].data` | String | Data da movimentação (formato: DD/MM/YYYY HH:MM:SS ou datetime) |
| `movimentacoes[].texto` | String | Descrição da movimentação |
| `created_at` | ISODate | Data de criação no MongoDB |
| `updated_at` | ISODate | Data da última atualização |

### Índices MongoDB

Índice único criado automaticamente:

```javascript
db.processos.createIndex({ "numero_processo": 1 }, { unique: true })
```

## 📈 Monitoramento e Logs

### Estatísticas de Execução

```
2025-11-11 14:35:54 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{
 'downloader/request_count': 15,
 'item_scraped_count': 10,
 'mongodb/items_inserted': 8,
 'mongodb/items_updated': 2,
 'elapsed_time_seconds': 45.3
}
```

### Logs do Pipeline

```
[processo] INFO: Conexão com MongoDB estabelecida com sucesso.
[processo] INFO: Processo inserido: PROCESSO Nº 0015648-78.1999.4.05.0000
[processo] INFO: Processo atualizado: PROCESSO Nº 0015648-78.1999.4.05.0000
```

### Debug HTML

Salvamento automático de HTML para análise de erros em `output/`:
- `erro_processo_*.html`: Páginas de erro
- `lista_cnpj_vazia_*.html`: Buscas sem resultados
- `processo_sem_numero_*.html`: Processos sem número

## 🧪 Testes

O projeto possui uma suíte completa de testes automatizados cobrindo todas as funcionalidades principais.

### Instalação das Dependências de Teste

```bash
# Ative o ambiente virtual
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instale dependências de teste
pip install -r requirements-test.txt
```

### Executar os Testes

```bash
# Executar todos os testes (unittest)
python -m unittest discover tests -v

# Executar todos os testes (pytest - recomendado)
pytest

# Executar com cobertura de código
pytest --cov=trf_scraper --cov-report=html

# Executar apenas um arquivo de testes
pytest tests/test_items.py -v

# Executar teste específico
pytest tests/test_items.py::TestCleanFunctions::test_clean_numero_processo_with_prefix
```

### Estrutura dos Testes

```
tests/
├── test_items.py          # Testes dos Items e processadores (17 testes)
├── test_spider.py         # Testes do spider (15 testes)
├── test_pipelines.py      # Testes do pipeline MongoDB (8 testes)
├── test_middlewares.py    # Testes dos middlewares (14 testes)
└── test_integration.py    # Testes de integração (3 testes)
```

### Cobertura de Código

```bash
# Gerar relatório de cobertura
pytest --cov=trf_scraper --cov-report=html

# Abrir relatório no navegador
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Testes com Docker

```bash
# Executar testes dentro do container
docker-compose run --rm spider python -m pytest

# Com cobertura
docker-compose run --rm spider pytest --cov=trf_scraper
```

**� Consulte a [Documentação completa de Testes](TESTING.md) para mais detalhes.**

## �📝 Exemplos

### Verificar Dados no MongoDB

```python
from pymongo import MongoClient

client = MongoClient("mongodb://admin:1234@localhost:27017/")
db = client['trf5_processos']

# Contar processos
print(f"Total: {db.processos.count_documents({})}")

# Buscar um processo
processo = db.processos.find_one({"numero_processo": {"$regex": "0015648"}})
print(processo)
```

Ou use o script pronto:

```bash
python verify_mongodb.py
```

### Exportar para JSON

```bash
# Durante a execução do scraping
scrapy crawl processo -a processos="..." -o output.json

# Exportar do MongoDB para JSON usando mongoexport
mongoexport \
  --uri="mongodb://admin:1234@localhost:27017/" \
  --db=trf5_processos \
  --collection=processos \
  --out=processos_export.json \
  --pretty

# Windows PowerShell
mongoexport `
  --uri="mongodb://admin:1234@localhost:27017/" `
  --db=trf5_processos `
  --collection=processos `
  --out=processos_export.json `
  --pretty
```

### Backup e Restore

```bash
# Backup completo do banco
mongodump \
  --uri="mongodb://admin:1234@localhost:27017/" \
  --db=trf5_processos \
  --out=backup_$(date +%Y%m%d)

# Restore do backup
mongorestore \
  --uri="mongodb://admin:1234@localhost:27017/" \
  --db=trf5_processos \
  backup_20251111/trf5_processos
```
