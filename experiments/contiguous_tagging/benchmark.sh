#!/usr/bin/env bash

set -o errexit  # when a command fails, exist
set -o nounset  # fail when accessing an unset variable
set -o pipefail # fail pipeline if any command errors

ARRAY=(536870912)
CORE=5

run_experiment() {
    local executable=$1
    local output_file=$2

    rm -f "$output_file"
    touch "$output_file"
    echo "size;duration;ops;processed" >> "$output_file"
    for size in "${ARRAY[@]}"; do
       taskset -c "$CORE" "$executable" 10 "$size" | tee -a "$output_file"
    done
}

rm -rf results
mkdir results

run_experiment "./tag_stg" "results/tag_stg.csv"
run_experiment "./tag_st2g" "results/tag_st2g.csv"
run_experiment "./tag_malloc" "results/tag_malloc.csv"
run_experiment "./load" "results/load.csv"
run_experiment "./store" "results/store.csv"
run_experiment "./ldg" "results/ldg.csv"
run_experiment "./irg" "results/irg.csv"
