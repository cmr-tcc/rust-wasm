#!/bin/bash

set -e

source "./script-utils.sh"

ALGORITHM=$1
ITERATIONS=$2
WARM_UP=$3
PARAMETER=$4

if [ -z "$ALGORITHM" ] || [ -z "$ITERATIONS" ] || [ -z "$WARM_UP" ] || [ -z "$PARAMETER" ]; then
  echo_color "Usage: ./collect-stats.sh <algorithm> <iterations> <warm_up> <parameter>" --red
  exit 1
fi

docker compose up -d

CONTAINER_ID=$(docker compose ps -q bench)

echo_color "Executing Rust" --yellow

docker exec -d "$CONTAINER_ID" /app/monitor.sh

RUST_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/rust && RAYON_NUM_THREADS=1 cargo bench --bench benchmarks -- $ALGORITHM $ITERATIONS $WARM_UP $PARAMETER"
)

docker exec "$CONTAINER_ID" kill "$(docker exec "$CONTAINER_ID" cat /tmp/resource_monitor.pid)"

docker cp "$CONTAINER_ID":/tmp/resource_usage.csv ./stats/rust-stats.csv

echo "$RUST_OUTPUT" >stats/rust-output.txt

echo_color "Sleeping..." --yellow

sleep 3

echo_color "Executing Wasm" --yellow

docker exec -d "$CONTAINER_ID" /app/monitor.sh

WASM_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/javascript && npm run bench -- ${ALGORITHM} ${ITERATIONS} ${WARM_UP} ${PARAMETER}"
)

docker exec "$CONTAINER_ID" kill "$(docker exec "$CONTAINER_ID" cat /tmp/resource_monitor.pid)"

docker cp "$CONTAINER_ID":/tmp/resource_usage.csv ./stats/wasm-stats.csv

echo "$WASM_OUTPUT" >stats/wasm-output.txt

docker compose down
