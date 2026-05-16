#!/bin/bash

set -e

ALGORITHM=$1
ITERATIONS=$2
WASM_JIT=$3

if [ -z "$ALGORITHM" ] || [ -z "$ITERATIONS" ] || [ -z "$WASM_JIT" ]; then
  echo "Usage: ./collect-stats.sh <algorithm> <iterations> <wasm_jit>"
  exit 1
fi

docker compose up -d

CONTAINER_ID=$(docker compose ps -q bench)

collect_stats() {
  FILE=$1

  echo "timestamp,cpu,memory" >"$FILE"

  (
    while true; do
      DOCKER_STATS=$(
        docker stats "$CONTAINER_ID" --no-stream --format "{{.CPUPerc}},{{.MemPerc}}"
      )
      TIMESTAMP=$(date +%s)

      echo "$TIMESTAMP,$DOCKER_STATS"

      sleep 1
    done
  ) >>"$FILE" &

  echo $!
}

RUST_STATS_PID=$(collect_stats stats/rust-stats.csv)

RUST_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/rust && cargo bench --bench benchmarks -- $ALGORITHM $ITERATIONS"
)

kill "$RUST_STATS_PID"

echo "$RUST_OUTPUT" >stats/rust-output.txt

sleep 3

WASM_STATS_PID=$(collect_stats stats/wasm-stats.csv)

WASM_OUTPUT=$(
  docker exec "$CONTAINER_ID" sh -c "cd /app/javascript && npm run bench -- ${ALGORITHM} ${ITERATIONS} ${WASM_JIT}"
)

kill "$WASM_STATS_PID"

echo "$WASM_OUTPUT" >stats/wasm-output.txt

docker compose down
