import csv
import json
import re
from datetime import datetime

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
    "description": "",
    "wasm": {
        "mean_ms": extract_mean_ms("stats/wasm-output.txt"),
        "resource_usage": load_csv("stats/wasm-stats.csv")
    },
    "rust": {
        "mean_ms": extract_mean_ms("stats/rust-output.txt"),
        "resource_usage": load_csv("stats/rust-stats.csv")
    }
}

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

output_path = f"stats/{timestamp}.json"

with open(output_path, "w") as f:
    json.dump(result, f, indent=4)