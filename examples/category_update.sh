#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

ID="${1:?Usage: $0 <id>}"

curl -s -X PATCH "$BASE_URL/categories/$ID" \
  -H "Content-Type: application/json"       \
  -H "X-API-Key: $API_KEY"                  \
  -d '{
    "name": "Updated Name"
  }' | jq
