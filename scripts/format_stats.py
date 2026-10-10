import csv
import json
import re
import sys
from pathlib import Path
from statistics import mean, median

algorithm = sys.argv[1]
iterations = int(sys.argv[2])
warm_up = int(sys.argv[3])
parameter = int(sys.argv[4])
output_file = sys.argv[5]
runner = sys.argv[6]

def load_csv(path):
    result = []

    with open(path) as f:
        reader = csv.DictReader(f)

        for row in reader:
            result.append({
                "timestamp": int(row["timestamp"]),
                "memory": row["memory"],
                "cpu": row["cpu"],
                "pid#process_name": f"{row['pid']}#{row['name']}"
            })

    return result

def extract_times(path):
    with open(path) as f:
        content = f.read()

    match = re.search(r'\{\s*"times"\s*:', content)

    if not match:
        return []

    result, _ = json.JSONDecoder().raw_decode(content[match.start():])
    times = result.get("times")

    if not isinstance(times, list):
        raise ValueError(f'Expected "times" to be an array in {path}')

    return [float(time) for time in times]

def summarize_times(times):
    if not times:
        return {
            "mean_ms": None,
            "median_ms": None,
            "times": [],
        }

    return {
        "mean_ms": mean(times),
        "median_ms": median(times),
        "times": times,
    }

def load_benchmark_output(path):
    return summarize_times(extract_times(path))

result = {
    "algorithm": algorithm,
    "description": "",
    "iterations": iterations,
    "warm_up": warm_up,
    "runner": runner,
    "parameter": parameter,
    "rust": {
        **load_benchmark_output("stats/rust-output.txt"),
        "resource_usage": load_csv("stats/rust-stats.csv")
    },
    "wasm": {
        **load_benchmark_output("stats/wasm-output.txt"),
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
