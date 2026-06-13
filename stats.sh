#!/bin/bash

set -e

source "./script-utils.sh"

CONFIG_FILE="config.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: $CONFIG_FILE not found"
    exit 1
fi

set -a
source .env
set +a

OUTPUT_FILE="stats/$(date +%Y-%m-%d_%H-%M).json"

docker compose build

jq -c '.[]' "$CONFIG_FILE" | while read -r item; do
    algorithm=$(echo "$item" | jq -r '.algorithm')
    iterations=$(echo "$item" | jq -r '.iterations')
    wasm_jit=$(echo "$item" | jq -r '.wasm_jit')
    parameter=$(echo "$item" | jq -r '.parameter')

    echo_color "Running: $algorithm" --yellow

    ./collect-stats.sh "$algorithm" "$iterations" "$wasm_jit" "$parameter"

    python3 format-stats.py "$algorithm" "$iterations" "$wasm_jit" "$parameter" "$OUTPUT_FILE" "$RUNNER"
done