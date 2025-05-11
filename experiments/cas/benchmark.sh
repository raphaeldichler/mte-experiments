#!/usr/bin/env bash

set -o errexit  # when a command fails, exist
set -o nounset  # fail when accessing an unset variable
set -o pipefail # fail pipeline if any command errors

ARRAY_SIZES=(1 2 3 4)

run_experiment() {
    local executable=$1
    local output_file=$2

    rm -f "$output_file"
    touch "$output_file"
    echo "cores;duration" >> "$output_file"
    for size in "${ARRAY_SIZES[@]}"; do
        taskset -c 4,5,6,7 "$executable" 10 "$size" | tee -a "$output_file"
        sleep 5s
    done
}

rm -rf results
mkdir results

run_experiment "./run" "results/run.csv"
run_experiment "./run_mte" "results/run_mte.csv"
