#!/bin/bash

set -e

source "./script-utils.sh"

ALGORITHM=$1
ITERATIONS=$2
WASM_JIT=$3
PARAMETER=$4

if [ -z "$ALGORITHM" ] || [ -z "$ITERATIONS" ] || [ -z "$WASM_JIT" ] || [ -z "$PARAMETER" ]; then
  echo_color "Usage: ./collect-stats.sh <algorithm> <iterations> <wasm_jit> <parameter>" --red
  exit 1
fi

docker compose up -d

CONTAINER_ID=$(docker compose ps -q bench)

collect_stats() {
  FILE=$1

  # Define the CSV header
  echo "timestamp,cpu,memory" > "$FILE"

  # (): starts a sub-shell
  # >>: redirect the output to a file
  # &: run in background
  (
    while true; do
      DOCKER_STATS=$(
        docker stats "$CONTAINER_ID" --no-stream --format "{{.CPUPerc}},{{.MemUsage}}"
      )

      TIMESTAMP=$(date +%s)
      CPU=$(echo "$DOCKER_STATS" | cut -d',' -f1)
      MEMORY=$(echo "$DOCKER_STATS" | cut -d',' -f2 | cut -d'/' -f1 | xargs)

      echo "$TIMESTAMP,$CPU,$MEMORY"

      sleep 1
    done
  ) >>"$FILE" &

  # Return the PID of the background process
  echo $!
}

echo_color "Executing Rust" --yellow

RUST_STATS_PID=$(collect_stats stats/rust-stats.csv)

echo_color "Rust stats PID: $RUST_STATS_PID" --red

RUST_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/rust && RAYON_NUM_THREADS=1 cargo bench --bench benchmarks -- $ALGORITHM $ITERATIONS $PARAMETER"
)

kill "$RUST_STATS_PID"

echo "$RUST_OUTPUT" >stats/rust-output.txt

echo_color "Sleeping..." --yellow

sleep 3

echo_color "Executing Wasm" --yellow

WASM_STATS_PID=$(collect_stats stats/wasm-stats.csv)

echo_color "Wasm stats PID: $WASM_STATS_PID" --red

WASM_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/javascript && npm run bench -- ${ALGORITHM} ${ITERATIONS} ${WASM_JIT} ${PARAMETER}"
)

kill "$WASM_STATS_PID"

echo "$WASM_OUTPUT" >stats/wasm-output.txt

docker compose down
