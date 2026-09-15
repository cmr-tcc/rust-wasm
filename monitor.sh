#!/bin/bash

OUTPUT="/tmp/resource_usage.csv"
PID_FILE="/tmp/resource_monitor.pid"

get_total_cpu() {
    awk '$1 == "usage_usec" {print $2}' /sys/fs/cgroup/cpu.stat
}

echo "timestamp,pid,name,cpu,memory" > "$OUTPUT"
echo $$ > "$PID_FILE"

CLOCKS_PER_SECOND=$(getconf CLK_TCK)
declare -A previous_cpu

previous_time=$(date +%s%N)
previous_total_cpu=$(get_total_cpu)

while true; do
    sleep 0.25 # Each iteration will take approximately 0.04 seconds

    current_time=$(date +%s%N)
    time_delta=$((current_time - previous_time))
    current_total_cpu=$(get_total_cpu)
    cpu_total_delta=$((current_total_cpu - previous_total_cpu))
    cpu_total=$(awk -v d="$cpu_total_delta" -v t="$time_delta" 'BEGIN { printf "%.2f", (d * 100000) / t }')

    current_memory=$(cat /sys/fs/cgroup/memory.current)
    current_inactive_memory=$(awk '$1 == "inactive_file" {print $2}' /sys/fs/cgroup/memory.stat)
    memory_kilobytes=$(( (current_memory - current_inactive_memory) / 1024 ))

    timestamp=$(date +%s)
    echo "$timestamp,TOTAL,total,$cpu_total,$memory_kilobytes" >> "$OUTPUT"

    for pid_path in /proc/[0-9]*; do
        pid="${pid_path#/proc/}"
        [ -r "$pid_path/stat" ] || continue

        process_stat=$(cat "$pid_path/stat" 2>/dev/null) || continue

        process_info=$(awk -v tck="$CLOCKS_PER_SECOND" '{
            s=$0
            open_paren = index(s, "(")
            close_paren = match(s, /\)[^)]*$/)
            name = substr(s, open_paren+1, close_paren-open_paren-1)
            rest = substr(s, close_paren+1)
            split(rest, arr, " ")
            utime = arr[12]
            stime = arr[13]
            usec = ((utime+stime)/tck)*1000000
            printf "%s\t%.0f", name, usec
        }' <<< "$process_stat")

        process_name="${process_info%%$'\t'*}"
        process_cpu="${process_info##*$'\t'}"

        current_cpu="${previous_cpu[$pid]:-$process_cpu}"
        process_cpu_delta=$((process_cpu - current_cpu))
        previous_cpu[$pid]=$process_cpu

        process_cpu_formatted=$(awk -v d="$process_cpu_delta" -v t="$time_delta" 'BEGIN { v=(d*100000)/t; if (v<0) v=0; printf "%.2f", v }')

        process_memory=$(awk '/^Pss:/ {sum+=$2} END {print sum+0}' "$pid_path/smaps_rollup" 2>/dev/null)
        [ -z "$process_memory" ] && process_memory=0

        echo "$timestamp,$pid,$process_name,$process_cpu_formatted,$process_memory" >> "$OUTPUT"
    done

    previous_total_cpu=$current_total_cpu
    previous_time=$current_time
done