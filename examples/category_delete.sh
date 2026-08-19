#!/usr/bin/env bash

ID="${1:?Usage: $0 <id>}"

curl -s                                  \
    -o /dev/null                         \
    -w "%{http_code}\n"                  \
    -X DELETE "$BASE_URL/categories/$ID" \
    -H "X-API-Key: $API_KEY"
