"""Head-to-head runner: every agent x harness pairing on one task list.

Outputs a JSON digest with per-pairing VCR, accuracy (over ALL tasks,
so aborted trajectories count as incorrect -- matching the paper's
separation of valid completion from task performance), mean token
load, and the paired-bootstrap contrasts. Deterministic given
(seed, n_tasks): task generation, agents, and bootstrap all use fixed
seeds, so a rerun reproduces the digest byte-for-byte (modulo key
ordering, which json.dumps with sort_keys fixes).
"""
import hashlib
import json

from .agents import AGENTS
from .harnesses import HARNESSES
from .stats import paired_bootstrap, wilson
from .tasks import generate_tasks

PAIRINGS = [("strict", "plain"), ("strict", "rich"),
            ("loose", "plain"), ("loose", "rich")]


def run(seed, n_tasks):
    tasks = generate_tasks(n_tasks, seed)
    per_task = []  # one record per task, all four pairings
    for task in tasks:
        truth = task.ground_truth()
        rec = {"task_id": task.task_id, "truth": truth,
               "has_div": task.has_op("div"), "has_mod": task.has_op("mod")}
        for agent_name, harness_name in PAIRINGS:
            out = AGENTS[agent_name].run(task, HARNESSES[harness_name])
            key = "%s/%s" % (agent_name, harness_name)
            rec[key] = {
                "valid": out["valid"],
                "correct": bool(out["valid"] and out["answer"] == truth),
                "tokens": out["tool_tokens"] + out["agent_tokens"],
            }
        per_task.append(rec)

    def cell(recs, key, field):
        return sum(1 for r in recs if r[key][field]) / len(recs)

    def mean_tokens(recs, key):
        return sum(r[key]["tokens"] for r in recs) / len(recs)

    cells = {}
    for agent_name, harness_name in PAIRINGS:
        key = "%s/%s" % (agent_name, harness_name)
        k_valid = sum(1 for r in per_task if r[key]["valid"])
        cells[key] = {
            "vcr": k_valid / len(per_task),
            "vcr_wilson95": wilson(k_valid, len(per_task)),
            "accuracy": cell(per_task, key, "correct"),
            "mean_token_load": mean_tokens(per_task, key),
        }

    # G2 contrast: accuracy rank reversal across models.
    #   d_strict = acc(strict/plain) - acc(strict/rich)   (expect > 0)
    #   d_loose  = acc(loose/rich) - acc(loose/plain)     (expect > 0)
    d_strict, ci_strict = paired_bootstrap(
        per_task,
        lambda rs: cell(rs, "strict/plain", "correct")
        - cell(rs, "strict/rich", "correct"))
    d_loose, ci_loose = paired_bootstrap(
        per_task,
        lambda rs: cell(rs, "loose/rich", "correct")
        - cell(rs, "loose/plain", "correct"))

    # G3 contrast: VCR interaction (marginal/additive model residual).
    #   I = (VCR_sp - VCR_sr) - (VCR_lp - VCR_lr)
    # Under a marginal-only (additive) model I = 0; a CI excluding 0
    # means pairing VCR is NOT predictable from model + harness
    # marginals -- the naive baseline fails.
    inter, ci_inter = paired_bootstrap(
        per_task,
        lambda rs: (cell(rs, "strict/plain", "valid")
                    - cell(rs, "strict/rich", "valid"))
        - (cell(rs, "loose/plain", "valid")
           - cell(rs, "loose/rich", "valid")))

    # Additive-model prediction error on the same cells (naive baseline,
    # reported descriptively): additive prediction of VCR(strict/rich)
    # from marginals = mean_row(strict) + mean_col(rich) - grand_mean.
    # In the 2x2 case its residual equals -I/4 exactly (algebra in
    # PAPER.md), so a nonzero interaction IS the naive model's miss.
    grand = sum(cells[k]["vcr"] for k in cells) / 4
    row_strict = (cells["strict/plain"]["vcr"] + cells["strict/rich"]["vcr"]) / 2
    col_rich = (cells["strict/rich"]["vcr"] + cells["loose/rich"]["vcr"]) / 2
    additive_pred_sr = row_strict + col_rich - grand
    naive_miss = cells["strict/rich"]["vcr"] - additive_pred_sr

    digest_obj = {"seed": seed, "n_tasks": n_tasks, "cells": cells,
                  "d_strict_acc": d_strict, "ci_strict_acc": ci_strict,
                  "d_loose_acc": d_loose, "ci_loose_acc": ci_loose,
                  "vcr_interaction": inter, "ci_vcr_interaction": ci_inter,
                  "additive_pred_strict_rich_vcr": additive_pred_sr,
                  "naive_miss_strict_rich_vcr": naive_miss}
    digest = hashlib.sha256(
        json.dumps(digest_obj, sort_keys=True).encode()).hexdigest()[:16]
    digest_obj["digest"] = digest
    return digest_obj
