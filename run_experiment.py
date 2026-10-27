#!/usr/bin/env python3
"""Run the harness-vcr head-to-head. Usage:
python3 run_experiment.py --seed 20261027 --n-tasks 800 --out results.json
"""
import argparse
import json
import sys

sys.path.insert(0, "src")

from harness_vcr.run import run  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n-tasks", type=int, default=800)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run(args.seed, args.n_tasks)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    for key, c in sorted(result["cells"].items()):
        print("%-14s VCR %.4f  acc %.4f  tokens %.1f"
              % (key, c["vcr"], c["accuracy"], c["mean_token_load"]))
    print("d_strict_acc %.4f CI %s" % (result["d_strict_acc"], result["ci_strict_acc"]))
    print("d_loose_acc  %.4f CI %s" % (result["d_loose_acc"], result["ci_loose_acc"]))
    print("VCR interaction %.4f CI %s" % (result["vcr_interaction"], result["ci_vcr_interaction"]))
    print("naive miss (strict/rich VCR) %.4f" % result["naive_miss_strict_rich_vcr"])
    print("digest", result["digest"])


if __name__ == "__main__":
    main()
