#!/usr/bin/env bash

set -o errexit  # when a command fails, exist
set -o nounset  # fail when accessing an unset variable
set -o pipefail # fail pipeline if any command errors

ARRAY=(16 128 256 1024 2048 4096 8192)
CORE=5

run_experiment() {
    local executable=$1
    local output_file=$2
    local option=$3

    rm -f "$output_file"
    touch "$output_file"
    echo "size;allocation;duration_allocation;duration_deallocation" >> "$output_file"
    
    for size in "${ARRAY[@]}"; do
       MEMTAG_OPTIONS="$option" taskset -c "$CORE" "$executable" 9 "$size" | tee -a "$output_file"
    done
}

rm -rf results
mkdir results

run_experiment "./malloc" "results/malloc.csv" "off"
run_experiment "./malloc_mte" "results/malloc_mte.csv" "sync"
