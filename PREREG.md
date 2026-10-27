# PREREG — harness-vcr (#85), locked BEFORE the head-to-head run

Locked: 2026-10-27 (PKT), after G0 green and a pilot run (seed 101,
300 tasks) used ONLY for calibration. Bars below are set below pilot
point estimates and are FROZEN: they will not move after the
head-to-head run, whatever it shows.

## Paper claim under test (scoped)
arXiv 2610.32483, "When Agents Fail: Model or Harness -- Who's to
Blame?" (Shao Zhang et al., submitted 23 Oct 2026). Five measures over
model x harness pairings; headline: harness rankings vary by model and
benchmark; task performance and valid completion can favour different
pairings; 4 harnesses x models on 6 benchmarks, 111 settings, 52,168
trajectories.

SCOPE (binding): the 52,168-trajectory evaluation is NOT replicated
and NOT claimed. This build tests the paper's core phenomenon at
small scale: 2 scripted agents x 2 scripted harnesses on a synthetic
integer-arithmetic task suite. Agents and harnesses are rule-based
simulators with documented, independent mechanisms (see
src/harness_vcr/agents.py); no LLM is run, and no claim about real
LLMs or real harnesses (OpenCode, Codex CLI, Pi CLI, DeepAgents) is
made. The question is whether the paper's measurement framework
(VCR, accuracy, interaction residuals) surfaces a pairing effect that
component-level summaries miss, in a setting where the mechanisms are
fully known.

## Design (frozen)
- Task suite: chains of integer ops (add/sub/mul/div/mod), lengths
  2..6, generated deterministically from the run seed. Division tasks
  are exact by construction.
- Agents: strict (exact-format parser, no mod support, exact
  otherwise) and loose (tolerant parser, div operands swapped when
  sending; on JSON renderings it recomputes from echoed operands
  applying the swap again, so the two swaps cancel on rich only).
- Harnesses: plain ("VALUE: <v>") and rich (JSON envelope with
  result + operand echo + next-op hint).
- Metrics: VCR = fraction of trajectories delivering an evaluable
  answer; accuracy = fraction of ALL tasks answered correctly
  (aborted trajectories count as incorrect); token load = mean
  whitespace-token count of tool outputs + final answer per
  trajectory (a proxy, stated as such -- no real tokenizer is run).
- Model-Harness Fit(m,h) is reported as VCR(m,h); Cross-Model
  Fit(h) as mean_m VCR(m,h). These are descriptive, not gated.
- Head-to-head run: seed 20261027 (FRESH -- never used in the
  pilot), 800 tasks, all four pairings on the same task list.
- Statistics: paired bootstrap over tasks (2000 reps, fixed seed
  12345); percentile 95% CIs. All contrasts are paired at task level.

## Pre-registered bars (PASS requires ALL)
- G2 (disease -- harness ranking by accuracy reverses across models):
  d_strict = acc(strict/plain) - acc(strict/rich) >= 0.20 AND its
  95% CI excludes 0; AND d_loose = acc(loose/rich) - acc(loose/plain)
  >= 0.15 AND its 95% CI excludes 0.
- G3 (load-bearing -- pairing VCR not predictable from marginals):
  |VCR interaction| = |(VCR_sp - VCR_sr) - (VCR_lp - VCR_lr)|
  >= 0.20 AND its 95% CI excludes 0; AND the marginal-only (additive)
  model's miss on the strict/rich cell has magnitude >= 0.05.
  The additive model is the naive baseline: if its miss is this
  large, component-level summaries do not determine pairing VCR.
- Determinism: rerunning the head-to-head command reproduces the
  digest exactly.

## Pilot calibration (for the record, NOT the result)
Pilot (seed 101, 300 tasks): strict/plain VCR 0.5000 acc 0.5000;
strict/rich VCR 0.0000 acc 0.0000; loose/plain VCR 1.0000 acc 0.6700;
loose/rich VCR 1.0000 acc 1.0000; d_strict 0.5000 CI [0.4433, 0.5567];
d_loose 0.3300 CI [0.2800, 0.3833]; VCR interaction 0.5000 CI
[0.4433, 0.5567]; naive miss -0.1250. Bars above sit below these
pilot values so the head-to-head is a genuine confirmation, not a
re-report of the pilot.

## Kill conditions
If any bar fails on the head-to-head run -> KILL with KILLED.md +
negative PAPER.md reporting the failed gate and the numbers. No bar
moves. If G1 (author-code recheck) had found author code, the build
would have stopped before this point; it did not (see KILLGATE.md).
