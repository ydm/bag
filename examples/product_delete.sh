#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

ID="${1:?Usage: $0 <id>}"

curl -s                                \
    -o /dev/null                       \
    -w "%{http_code}\n"                \
    -X DELETE "$BASE_URL/products/$ID" \
    -H "X-API-Key: $API_KEY"
