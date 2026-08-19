#!/usr/bin/env bash

ID="${1:?Usage: $0 <id>}"

curl -s -X PATCH "$BASE_URL/products/$ID" \
  -H "Content-Type: application/json"     \
  -H "X-API-Key: $API_KEY"                \
  -d '{
    "price": "19.99"
  }' | jq
