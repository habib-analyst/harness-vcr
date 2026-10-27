# harness-vcr

A small-scale, CPU-only study of the paper **"When Agents Fail: Model or
Harness — Who's to Blame?"** (arXiv 2610.32483): does the paper's
measurement framework — Valid Completion Rate (VCR), task accuracy, and
Interaction Residuals — surface a pairing effect that component-level
summaries miss?

**Headline (held-out seed 20261027, 800 synthetic tasks, all pairings on
the same task list):**

| pairing | VCR | accuracy | mean token load |
|---|---|---|---|
| strict / plain | 0.486 | 0.486 | 6.0 |
| strict / rich | 0.000 | 0.000 | 6.6 |
| loose / plain | 1.000 | 0.731 | 10.1 |
| loose / rich | 1.000 | 1.000 | 34.3 |

- **Harness ranking by accuracy reverses across agents.** For strict,
  plain beats rich by +48.6pp (95% CI [45.1, 52.1]); for loose, rich
  beats plain by +26.9pp (95% CI [23.9, 30.1]).
- **Pairing VCR is not predictable from marginals.** VCR interaction
  +48.6pp (95% CI [45.1, 52.1]); the marginal-only additive model
  misses the strict/rich cell by −12.2pp.
- **VCR alone cannot pick the best pairing.** VCR ties loose/plain and
  loose/rich at 1.000, but accuracy separates them (0.731 vs 1.000).
  Picking by Cross-Model Fit (mean VCR: plain 0.743 > rich 0.500) would
  miss rich, the accuracy-best harness for loose.

## What this is — and is not

This is a **mechanism demo with scripted agents**, not a measurement of
real LLMs or real harnesses. Two rule-based agents (strict: exact-format
parser, no `mod` support; loose: tolerant parser with a div-operand
swap bug) meet two scripted harnesses (plain: `VALUE: <v>`; rich: JSON
envelope with an operand echo). No pairing outcome is hard-coded: the
reversal emerges from independent component rules — parser strictness ×
envelope format, op support, and a double-swap cancellation that makes
loose correct on div steps under rich only. The paper's 52,168
trajectories are **not** reproduced; nothing here claims anything about
OpenCode, Codex CLI, Pi CLI, DeepAgents, or any real model.

## Run it

```bash
python3 run_experiment.py --seed 20261027 --n-tasks 800 --out results.json
python3 -m pytest tests/ -q   # 10/10
```

Deterministic: rerunning the head-to-head command reproduces digest
`a37af8dd6eb7e159` exactly. CPU only, $0, no network, no LLM judge
anywhere (rule-based coding only).

## Layout

- `src/harness_vcr/tasks.py` — synthetic integer-arithmetic task suite
- `src/harness_vcr/agents.py` — scripted agents + tool semantics
- `src/harness_vcr/harnesses.py` — plain / rich renderings
- `src/harness_vcr/stats.py` — paired bootstrap over tasks
- `src/harness_vcr/run.py` — head-to-head + contrasts
- `PREREG.md` — bars locked before the head-to-head run
- `KILLGATE.md` — gate record with numbers

## License

MIT. See `LICENSE`.
