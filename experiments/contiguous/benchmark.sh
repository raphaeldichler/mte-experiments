#!/usr/bin/env bash

set -o errexit  # when a command fails, exist
set -o nounset  # fail when accessing an unset variable
set -o pipefail # fail pipeline if any command errors

CORE=5

for ((i = 0; i <= 19; i++)); do
    ARRAY_SIZES16+=($(( (2**i) * 1024 / 64 )))
done

run_experiment() {
    local executable=$1
    local output_file=$2

    rm -f "$output_file"
    touch "$output_file"
    echo "len;duration;runs" >> "$output_file"
    
    for size in "${ARRAY_SIZES16[@]}"; do
      taskset -c "$CORE" "$executable" 10 "$size" 1 | tee -a "$output_file"
      sleep 5s
    done
}

rm -rf results
mkdir results

run_experiment "./load16" "results/load16.csv"
run_experiment "./load16_mte" "results/load16_mte.csv"

