#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

ID="${1:?Usage: $0 <id>}"

curl -s "$BASE_URL/products/$ID" | jq
