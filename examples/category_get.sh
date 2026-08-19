#!/usr/bin/env bash

ID="${1:?Usage: $0 <id>}"

curl -s "$BASE_URL/categories/$ID" | jq
