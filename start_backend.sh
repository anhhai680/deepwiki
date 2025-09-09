#!/bin/bash

# Load environment variables from .env file and start the backend
cd "$(dirname "$0")"

if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

echo "Starting backend with environment variables loaded..."
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}..."
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..."

python -m backend.main
