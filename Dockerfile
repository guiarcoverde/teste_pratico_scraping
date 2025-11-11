FROM python:3.10-slim

LABEL maintainer="TRF Scraper"
LABEL description="Scrapy spider for TRF5 judicial processes"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app

USER scraper

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["scrapy", "list"]
