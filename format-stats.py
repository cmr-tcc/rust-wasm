import csv
import json
import re
import sys
from pathlib import Path

algorithm = sys.argv[1]
iterations = int(sys.argv[2])
wasm_jit = int(sys.argv[3])
output_file = sys.argv[4]
runner = sys.argv[5]

def load_csv(path):
    result = []

    with open(path) as f:
        reader = csv.DictReader(f)

        for row in reader:
            result.append({
                "timestamp": int(row["timestamp"]),
                "memory": row["memory"],
                "cpu": row["cpu"]
            })

    return result

def extract_mean_ms(path):
    with open(path) as f:
        content = f.read()

    match = re.search(r'"mean_ms"\s*:\s*([0-9.]+)', content)

    if not match:
        return None

    return float(match.group(1))

result = {
    "algorithm": algorithm,
    "iterations": iterations,
    "wasm_jit": wasm_jit,
    "runner": runner,
    "rust": {
        "mean_ms": extract_mean_ms("stats/rust-output.txt"),
        "resource_usage": load_csv("stats/rust-stats.csv")
    },
    "wasm": {
        "mean_ms": extract_mean_ms("stats/wasm-output.txt"),
        "resource_usage": load_csv("stats/wasm-stats.csv")
    },
}

results = []

if Path(output_file).exists():
    with open(output_file) as f:
        results = json.load(f)

results.append(result)

with open(output_file, "w") as f:
    json.dump(results, f, indent=4)