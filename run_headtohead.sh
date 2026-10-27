#!/bin/bash
# PREREG-locked head-to-head run (seed 20261027, 800 tasks) + determinism rerun.
set -e
cd "$(dirname "$0")"
python3 run_experiment.py --seed 20261027 --n-tasks 800 --out results.json
python3 run_experiment.py --seed 20261027 --n-tasks 800 --out results_rerun.json | tail -1
python3 -c "
import json
a = json.load(open('results.json')); b = json.load(open('results_rerun.json'))
assert a['digest'] == b['digest'], 'NON-DETERMINISTIC'
print('determinism OK:', a['digest'])"
