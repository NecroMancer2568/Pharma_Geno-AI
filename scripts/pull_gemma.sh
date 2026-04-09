#!/bin/bash
set -e

MODEL_NAME=${GEMMA_MODEL:-"gemma4:e2b"}
OLLAMA_HOST=${OLLAMA_URL:-"http://localhost:11434"}

echo "Pulling $MODEL_NAME from Ollama at $OLLAMA_HOST..."
curl -X POST $OLLAMA_HOST/api/pull -d "{\"name\": \"$MODEL_NAME\"}"
echo -e "\nModel $MODEL_NAME pulled successfully."