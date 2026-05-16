#!/bin/bash

set -e

CONFIG_FILE="config.json"
OUTPUT_FILE="stats/$(date +%Y-%m-%d_%H-%M).json"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: $CONFIG_FILE not found"
    exit 1
fi

docker compose build

jq -c '.[]' "$CONFIG_FILE" | while read -r item; do
    algorithm=$(echo "$item" | jq -r '.algorithm')
    iterations=$(echo "$item" | jq -r '.iterations')
    wasm_jit=$(echo "$item" | jq -r '.wasm_jit')

    ./collect-stats.sh "$algorithm" "$iterations" "$wasm_jit"

    python3 format-stats.py "$algorithm" "$iterations" "$wasm_jit" "$OUTPUT_FILE"
done