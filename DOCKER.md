# 🐳 Docker - TRF Scraper

## Arquitetura

O projeto está dockerizado com dois serviços:

- **mongodb**: Banco de dados MongoDB 8.2.1 com autenticação
- **spider**: Container Python 3.10 com Scrapy

## 📋 Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+

## 🚀 Uso Rápido

### 1. Iniciar toda a stack (MongoDB + Spider)

```bash
docker-compose up
```

Isso irá:
- Iniciar o MongoDB na porta 27017
- Aguardar o MongoDB ficar saudável
- Executar o spider com o processo de exemplo

### 2. Executar apenas o MongoDB

```bash
docker-compose up mongodb
```

### 3. Executar spider com processos customizados

```bash
docker-compose run --rm spider scrapy crawl processo -a processos="00156487819994050000,00234567890123456789"
```

### 4. Executar busca por CNPJ

```bash
docker-compose run --rm spider scrapy crawl processo -a cnpj="12.345.678/0001-90"
```

### 5. Ver logs do MongoDB

```bash
docker-compose logs -f mongodb
```

## 🔧 Comandos Úteis

### Build da imagem

```bash
docker-compose build
```

### Rebuild sem cache

```bash
docker-compose build --no-cache
```

### Parar todos os serviços

```bash
docker-compose down
```

### Parar e remover volumes (CUIDADO: apaga dados do MongoDB)

```bash
docker-compose down -v
```

### Executar comandos dentro do container

```bash
# Scrapy shell
docker-compose run --rm spider scrapy shell "http://www5.trf5.jus.br/cp/"

# Listar spiders
docker-compose run --rm spider scrapy list

# Bash interativo
docker-compose run --rm spider bash
```

## 📂 Volumes

### Volumes persistentes:

- `mongodb_data`: Dados do MongoDB
- `mongodb_config`: Configurações do MongoDB

### Volumes montados do host:

- `./output`: Arquivos JSON de saída
- `./logs`: Logs do spider

## 🔐 Credenciais MongoDB

**Default (docker-compose.yml):**
- Username: `admin`
- Password: `1234`
- Database: `trf5_processos`
- URI: `mongodb://admin:1234@mongodb:27017/`

Para alterar, edite as variáveis de ambiente no `docker-compose.yml`.

## 🌐 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MONGO_URI` | `mongodb://admin:1234@mongodb:27017/` | URI de conexão do MongoDB |
| `MONGO_DATABASE` | `trf5_processos` | Nome do banco de dados |

### Sobrescrever variáveis:

```bash
docker-compose run --rm \
  -e MONGO_URI="mongodb://user:pass@otherhost:27017/" \
  spider scrapy crawl processo -a processos="123"
```

## 🐛 Troubleshooting

### Erro: "Cannot connect to MongoDB"

```bash
# Verificar se MongoDB está rodando
docker-compose ps

# Ver logs do MongoDB
docker-compose logs mongodb

# Reiniciar MongoDB
docker-compose restart mongodb
```

### Erro: "Permission denied" no entrypoint

```bash
# Dar permissão de execução (Linux/Mac)
chmod +x docker-entrypoint.sh

# No Windows com Git Bash
git update-index --chmod=+x docker-entrypoint.sh
```

### Limpar tudo e começar do zero

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 📊 Monitoramento

### Ver estatísticas do container

```bash
docker stats trf_spider trf_mongodb
```

### Inspecionar o container

```bash
docker inspect trf_spider
```

### Acessar MongoDB com mongosh

```bash
docker exec -it trf_mongodb mongosh -u admin -p 1234 --authenticationDatabase admin
```

Comandos úteis no mongosh:
```javascript
use trf5_processos
db.processos.countDocuments()
db.processos.find().limit(1).pretty()
db.processos.find({numero_processo: "00156487819994050000"})
```

## 🚀 Deploy em Produção

### 1. Use variáveis de ambiente seguras

Crie um arquivo `.env`:
```env
MONGO_ROOT_USERNAME=production_user
MONGO_ROOT_PASSWORD=strong_password_here
MONGO_DATABASE=trf5_prod
```

Referencie no docker-compose.yml:
```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME}
  MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
```

### 2. Configure logs para arquivo

```yaml
spider:
  command: >
    scrapy crawl processo 
    -a processos="123" 
    --logfile=/app/logs/spider.log
```

### 3. Use restart policies

```yaml
restart: always
```

### 4. Limite recursos

```yaml
spider:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        memory: 512M
```

## 📝 Exemplo: Scraping Contínuo

Para executar o spider periodicamente, use cron dentro do container ou um orquestrador como Kubernetes CronJob.

**docker-compose.cron.yml:**
```yaml
version: '3.8'
services:
  spider-cron:
    build: .
    depends_on:
      - mongodb
    environment:
      MONGO_URI: mongodb://admin:1234@mongodb:27017/
    command: >
      bash -c "while true; do
        scrapy crawl processo -a processos='123,456,789';
        echo 'Aguardando 1 hora...';
        sleep 3600;
      done"
```

Execute: `docker-compose -f docker-compose.cron.yml up`

## 🔗 Links Úteis

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [Scrapy Documentation](https://docs.scrapy.org/)
