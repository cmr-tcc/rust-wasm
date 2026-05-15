#!/bin/bash
set -e

# Run Rust benchmark
cd /app/rust/
cargo bench --bench benchmarks

# Run Wasm benchmark
cd /app/javascript/
npm run bench