#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

curl -s -X POST "$BASE_URL/categories/" \
  -H "Content-Type: application/json"   \
  -H "X-API-Key: $API_KEY"              \
  -d '{
    "name": "Electronics",
    "parent_id": null
  }' | jq
