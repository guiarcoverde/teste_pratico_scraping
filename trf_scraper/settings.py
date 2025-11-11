BOT_NAME = "trf_scraper"

SPIDER_MODULES = ["trf_scraper.spiders"]
NEWSPIDER_MODULE = "trf_scraper.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 1

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1

AUTOTHROTTLE_MAX_DELAY = 10

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    "trf_scraper.pipelines.MongoDBPipeline": 400,
}

import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:1234@localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "trf5_processos")

DOWNLOADER_MIDDLEWARES = {
    'trf_scraper.middlewares.ResponseTimeMiddleware': 543,
    'trf_scraper.middlewares.ErrorLoggingMiddleware': 544,
}

LOG_LEVEL = 'INFO'

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Cria diretório de logs se não existir
import os
from datetime import datetime
os.makedirs('logs', exist_ok=True)

# Nome do arquivo de log com timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = f'logs/scrapy_{timestamp}.log'
