import json
import os
import re
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from utils.stats_utils import parse_cpu_percent, parse_memory_kib_to_mib


def load_data(json_path: str) -> pd.DataFrame:
    with open(json_path) as f:
        data = json.load(f)

    rows = []
    for entry in data:
        for runtime in ("rust", "wasm"):
            for sample in entry[runtime]["resource_usage"]:
                process = sample.get("pid#process_name")
                if process is None or "#" not in process:
                    raise ValueError(
                        "Each resource sample must contain a 'pid#process_name' "
                        "value"
                    )

                pid, name = process.split("#", 1)
                rows.append(
                    {
                        "algorithm": entry["algorithm"],
                        "runtime": runtime,
                        "timestamp": sample["timestamp"],
                        "pid": pid,
                        "name": name,
                        "cpu": parse_cpu_percent(sample["cpu"]),
                        "memory": parse_memory_kib_to_mib(sample["memory"]),
                    }
                )

    if not rows:
        raise ValueError(f"JSON file contains no resource usage samples: {json_path}")

    df = pd.DataFrame(rows)

    # Group by pid+name so a reused PID with a different process
    # doesn't get merged into the same series.
    df["series"] = df["name"] + " (pid " + df["pid"].astype(str) + ")"

    return df


def plot_metric(df: pd.DataFrame, value_col: str, ylabel: str, title: str, out_path: str):
    fig, ax = plt.subplots(figsize=(12, 6))

    for series_name, group in df.groupby("series"):
        group = group.sort_values("t")
        # TOTAL (cgroup-wide) line gets a distinct style so it stands out
        # against individual process lines.
        is_total = (group["pid"].astype(str) == "TOTAL").any()
        if is_total:
            ax.plot(group["t"], group[value_col], label=series_name,
                    linewidth=2.5, linestyle="--", color="black", zorder=5)
        else:
            ax.plot(group["t"], group[value_col], label=series_name, linewidth=1.5)

    ax.set_xlabel("Seconds")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/format_process.py <input.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    file_stem = Path(json_path).stem
    output_dir = Path(f"charts/{file_stem}/process/")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(json_path)

    for (algorithm, runtime), group in df.groupby(["algorithm", "runtime"]):
        group = group.copy()
        # Normalize timestamps per algorithm/runtime so each chart starts at 0.
        group["t"] = group["timestamp"] - group["timestamp"].min()

        plot_metric(
            group,
            value_col="cpu",
            ylabel="CPU (%)",
            title=f"{algorithm} - CPU Usage per Process ({"Rust" if runtime == "rust" else "WASM"})",
            out_path=os.path.join(output_dir, f"{algorithm}_cpu_{runtime}.png"),
        )

        plot_metric(
            group,
            value_col="memory",
            ylabel="Memory (MiB)",
            title=f"{algorithm} - Memory Usage per Process ({"Rust" if runtime == "rust" else "WASM"})",
            out_path=os.path.join(output_dir, f"{algorithm}_memory_{runtime}.png"),
        )


if __name__ == "__main__":
    main()
