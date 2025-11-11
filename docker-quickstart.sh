#!/bin/bash

# Quick start script for Docker

echo "TRF Scraper - Docker Quick Start"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Docker is running"
echo ""

# Build images
echo "Building Docker images..."
docker-compose build

echo ""
echo "Build complete!"
echo ""

# Start MongoDB
echo "Starting MongoDB..."
docker-compose up -d mongodb

echo ""
echo "Waiting for MongoDB to be healthy..."
sleep 10

echo ""
echo "MongoDB is ready!"
echo ""

# Run spider with example
echo "Running spider with example process..."
docker-compose run --rm spider scrapy crawl processo -a processos="00156487819994050000"

echo ""
echo "Done! Check the results:"
echo "   - MongoDB: docker exec -it trf_mongodb mongosh -u admin -p 1234"
echo "   - Logs: docker-compose logs spider"
echo ""
