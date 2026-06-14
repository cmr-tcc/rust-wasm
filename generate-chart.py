import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt


def parse_memory(mem_str):
    """
    Convert:
    121.8MiB -> 121.8
    1.5GiB -> 1536
    """
    match = re.match(r"([\d.]+)([KMG]iB)", mem_str)

    if not match:
        return 0

    value = float(match.group(1))
    unit = match.group(2)

    factors = {
        "KiB": 1 / 1024,
        "MiB": 1,
        "GiB": 1024,
    }

    return value * factors[unit]


def parse_cpu(cpu_str):
    return float(cpu_str.replace("%", ""))


if len(sys.argv) < 2:
    print("Usage: python3 generate-chart.py <json_file>")
    sys.exit(1)

json_file = sys.argv[1]

with open(json_file, "r") as f:
    data = json.load(f)

file_stem = Path(json_file).stem
output_dir = Path(f"charts/{file_stem}")
output_dir.mkdir(exist_ok=True)

# =====================================================
# Execution Time Comparison
# =====================================================

algorithms = [item["algorithm"] for item in data]
rust_times = [item["rust"]["mean_ms"] for item in data]
wasm_times = [item["wasm"]["mean_ms"] for item in data]

plt.figure(figsize=(10, 5))

x = range(len(algorithms))
width = 0.4

plt.bar(
    [i - width / 2 for i in x],
    rust_times,
    width=width,
    label="Rust",
)

plt.bar(
    [i + width / 2 for i in x],
    wasm_times,
    width=width,
    label="WASM",
)

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

for item in data:
    algorithm = item["algorithm"]

    rust_usage = item["rust"]["resource_usage"]
    wasm_usage = item["wasm"]["resource_usage"]

    # Skip algorithms without samples
    if not rust_usage and not wasm_usage:
        continue

    # -------------------------------------------------
    # Memory Graph - Rust
    # -------------------------------------------------

    if rust_usage:
        plt.figure(figsize=(12, 5))

        rust_t0 = rust_usage[0]["timestamp"]

        rust_x = [
            sample["timestamp"] - rust_t0
            for sample in rust_usage
        ]

        rust_mem = [
            parse_memory(sample["memory"])
            for sample in rust_usage
        ]

        plt.plot(
            rust_x,
            rust_mem,
            marker="o",
            label="Rust",
            color="tab:blue",
        )

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
        plt.figure(figsize=(12, 5))

        wasm_t0 = wasm_usage[0]["timestamp"]

        wasm_x = [
            sample["timestamp"] - wasm_t0
            for sample in wasm_usage
        ]

        wasm_mem = [
            parse_memory(sample["memory"])
            for sample in wasm_usage
        ]

        plt.plot(
            wasm_x,
            wasm_mem,
            marker="o",
            label="WASM",
            color="tab:orange",
        )

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
        plt.figure(figsize=(12, 5))

        rust_t0 = rust_usage[0]["timestamp"]

        rust_x = [
            sample["timestamp"] - rust_t0
            for sample in rust_usage
        ]

        rust_cpu = [
            parse_cpu(sample["cpu"])
            for sample in rust_usage
        ]

        plt.plot(
            rust_x,
            rust_cpu,
            marker="o",
            label="Rust",
            color="tab:blue",
        )

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
        plt.figure(figsize=(12, 5))

        wasm_t0 = wasm_usage[0]["timestamp"]

        wasm_x = [
            sample["timestamp"] - wasm_t0
            for sample in wasm_usage
        ]

        wasm_cpu = [
            parse_cpu(sample["cpu"])
            for sample in wasm_usage
        ]

        plt.plot(
            wasm_x,
            wasm_cpu,
            marker="o",
            label="WASM",
            color="tab:orange",
        )

        plt.title(f"{algorithm} - CPU Usage (WASM)")
        plt.xlabel("Seconds")
        plt.ylabel("CPU (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(output_dir / f"{algorithm}_cpu_wasm.png")
        plt.close()

print(f"Charts saved to: {output_dir.resolve()}")