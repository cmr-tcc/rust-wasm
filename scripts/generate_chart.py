import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from utils.stats_utils import parse_cpu_percent, parse_memory_mib

if len(sys.argv) < 2:
    print("Usage: python3 scripts/generate_chart.py <json_file>")
    sys.exit(1)

json_file = sys.argv[1]

with open(json_file, "r") as f:
    data = json.load(f)

file_stem = Path(json_file).stem
output_dir = Path(f"charts/{file_stem}/total/")
output_dir.mkdir(parents=True, exist_ok=True)


def filter_total_usage(resource_usage):
    return [
        sample
        for sample in resource_usage
        if sample.get("pid#process_name") == "TOTAL#total"
    ]

# =====================================================
# Execution Time Comparison
# =====================================================

algorithms = [entry["algorithm"] for entry in data]
rust_times = [entry["rust"]["mean_ms"] for entry in data]
wasm_times = [entry["wasm"]["mean_ms"] for entry in data]

plt.figure(figsize=(10, 5))

x = range(len(algorithms))
width = 0.4

plt.bar([i - width / 2 for i in x], rust_times, width=width, label="Rust")
plt.bar([i + width / 2 for i in x], wasm_times, width=width, label="WASM")

plt.xticks(list(x), algorithms, rotation=45)
plt.ylabel("Mean Time (ms)")
plt.title("Rust vs WASM Performance")
plt.legend()
plt.tight_layout()

plt.savefig(output_dir / "execution_times.png")
plt.close()

# =====================================================
# Per Algorithm Resource Usage
# =====================================================

for entry in data:
    algorithm = entry["algorithm"]
    rust_usage = filter_total_usage(entry["rust"]["resource_usage"])
    wasm_usage = filter_total_usage(entry["wasm"]["resource_usage"])

    if not rust_usage and not wasm_usage:
        continue

    # -------------------------------------------------
    # Memory Graph - Rust
    # -------------------------------------------------

    if rust_usage:
        start_timestamp = rust_usage[0]["timestamp"]
        seconds = [sample["timestamp"] - start_timestamp for sample in rust_usage]
        memory = [parse_memory_mib(sample["memory"]) for sample in rust_usage]

        plt.figure(figsize=(12, 5))
        plt.plot(seconds, memory, marker="o", label="Rust", color="tab:blue")
        plt.title(f"{algorithm} - Memory Usage (Rust)")
        plt.xlabel("Seconds")
        plt.ylabel("Memory (MiB)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / f"{algorithm}_memory_rust.png")
        plt.close()

    # -------------------------------------------------
    # Memory Graph - WASM
    # -------------------------------------------------

    if wasm_usage:
        start_timestamp = wasm_usage[0]["timestamp"]
        seconds = [sample["timestamp"] - start_timestamp for sample in wasm_usage]
        memory = [parse_memory_mib(sample["memory"]) for sample in wasm_usage]

        plt.figure(figsize=(12, 5))
        plt.plot(seconds, memory, marker="o", label="WASM", color="tab:orange")
        plt.title(f"{algorithm} - Memory Usage (WASM)")
        plt.xlabel("Seconds")
        plt.ylabel("Memory (MiB)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / f"{algorithm}_memory_wasm.png")
        plt.close()

    # -------------------------------------------------
    # CPU Graph - Rust
    # -------------------------------------------------

    if rust_usage:
        start_timestamp = rust_usage[0]["timestamp"]
        seconds = [sample["timestamp"] - start_timestamp for sample in rust_usage]
        cpu = [parse_cpu_percent(sample["cpu"]) for sample in rust_usage]

        plt.figure(figsize=(12, 5))
        plt.plot(seconds, cpu, marker="o", label="Rust", color="tab:blue")
        plt.title(f"{algorithm} - CPU Usage (Rust)")
        plt.xlabel("Seconds")
        plt.ylabel("CPU (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / f"{algorithm}_cpu_rust.png")
        plt.close()

    # -------------------------------------------------
    # CPU Graph - WASM
    # -------------------------------------------------

    if wasm_usage:
        start_timestamp = wasm_usage[0]["timestamp"]
        seconds = [sample["timestamp"] - start_timestamp for sample in wasm_usage]
        cpu = [parse_cpu_percent(sample["cpu"]) for sample in wasm_usage]

        plt.figure(figsize=(12, 5))
        plt.plot(seconds, cpu, marker="o", label="WASM", color="tab:orange")
        plt.title(f"{algorithm} - CPU Usage (WASM)")
        plt.xlabel("Seconds")
        plt.ylabel("CPU (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / f"{algorithm}_cpu_wasm.png")
        plt.close()

print(f"Charts saved to: {output_dir.resolve()}")
