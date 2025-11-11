#!/bin/bash
set -e

echo "========================================="
echo "TRF5 Scraper - Docker Container"
echo "========================================="
echo ""

if [ -z "$MONGO_URI" ]; then
    echo "Warning: MONGO_URI not set. Using default."
    export MONGO_URI="mongodb://admin:1234@mongodb:27017/"
fi

echo "Environment:"
echo "   MONGO_URI: $MONGO_URI"
echo "   MONGO_DATABASE: ${MONGO_DATABASE:-trf5_processos}"
echo ""

echo "Starting spider..."
echo "   Command: $@"
echo ""

exec "$@"
