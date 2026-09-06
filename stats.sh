#!/bin/bash

set -e

source "./script-utils.sh"

CONFIG_FILE="config.json"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo_color "Error: $CONFIG_FILE not found" --red
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
    warm_up=$(echo "$item" | jq -r '.warm_up')
    parameter=$(echo "$item" | jq -r '.parameter')

    echo_color "Running: $algorithm" --yellow

    ./collect-stats.sh "$algorithm" "$iterations" "$warm_up" "$parameter"

    python3 scripts/format_stats.py "$algorithm" "$iterations" "$warm_up" "$parameter" "$OUTPUT_FILE" "$RUNNER"
done