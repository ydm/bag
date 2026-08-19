#!/usr/bin/env bash
source "$(dirname "$0")/config.sh"

curl -s "$BASE_URL/products/" | jq
