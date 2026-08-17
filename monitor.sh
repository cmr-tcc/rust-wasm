#!/bin/bash

OUTPUT="/tmp/resource_usage.csv"
PIDFILE="/tmp/resource_monitor.pid"

echo "timestamp,cpu,memory" > "$OUTPUT"

echo $$ > "$PIDFILE"

previous_cpu=$(awk '$1 == "usage_usec" {print $2}' /sys/fs/cgroup/cpu.stat)
previous_time=$(date +%s%N)

while true; do
    sleep 1

    # CPU
    current_cpu=$(awk '$1 == "usage_usec" {print $2}' /sys/fs/cgroup/cpu.stat)
    current_time=$(date +%s%N)

    cpu_delta=$((current_cpu - previous_cpu))
    time_delta=$((current_time - previous_time))

    cpu=$(awk \
        -v cpu="$cpu_delta" \
        -v time="$time_delta" \
        'BEGIN { printf "%.2f", (cpu * 100000) / time }')

    # Memory
    memory_current=$(cat /sys/fs/cgroup/memory.current)

    inactive_file=$(awk '$1 == "inactive_file" {print $2}' \
    /sys/fs/cgroup/memory.stat)

    docker_style_memory=$((memory_current - inactive_file))

    memory=$(awk -v bytes="$docker_style_memory" 'BEGIN { printf "%.2fMiB", bytes / 1048576 }')

    echo "$(date +%s),$cpu%,$memory" >> "$OUTPUT"

    previous_cpu=$current_cpu
    previous_time=$current_time
done