#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

curl -s -X POST "$BASE_URL/products/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "title": "A very nice product",
    "description": "Buy it. You won'\''t regret this. 🥰",
    "image": "https://d.ibtimes.co.uk/en/full/1399243/antikythera-mechanism.jpg",
    "price": "1.23",
    "category_id": 1
  }' | jq
