# Kill-gate record — project #85 harness-vcr (arXiv 2610.32483)

## G0 — harness + unit tests: PASS
10/10 pytest tests green: strict-plain exactness, strict-rich abort,
strict-mod abort, loose-plain div error, loose-rich div correction
via double swap, loose-rich/plain sub exactness, div-by-zero
degenerate case, task-generation determinism + mix, head-to-head
determinism on a small run.

## G1 — author-code recheck: PASS (shelf empty of author code)
- arXiv abs page 2610.32483 (fetched 2026-10-27): NO code links; only
  generic arXivLabs toggles (alphaXiv, CatalyzeX, etc.), no author repo.
  Authors: Shao Zhang, Hangfan Zhang, Yuanyuan Shi, Hao Li, Min-Le Su,
  Kangcong Li, Jingping Wang, Chunjiang Mu, Chen Zhang, Yang Chen,
  Bo Zhang, Shuyue Hu. Submitted 23 Oct 2026.
- GitHub repo search "When Agents Fail" (API, 2026-10-27): 2 hits --
  NifulIslam/WhenAgentsFail (ISSRE-2026 Paper 226, created 11 Aug 2026,
  BEFORE this paper's submission -- a different paper sharing title
  words, not this paper's code) and no author-code repo.
- GitHub repo search "Model or Harness": 3 hits, all unrelated
  (game-gym adapter, numerical-solver bench, agent-skills collection).
- GitHub repo search "Valid Completion Rate": 2 hits, both unrelated.
- Web search for the paper title + code, and for the distinctive
  phrases "Valid Completion Rate" / "Model-Harness Fit" /
  "Interaction Residuals": no author code; only generic
  harness-engineering blog posts and unrelated material.
- NOTE (not a kill, per brief): the isomoes.github.io blog post about
  "model-harness fit" is a blog post, NOT author code -- not confused
  with the paper's code. NOTE 2: the paper's four evaluated harnesses
  (OpenCode, Codex CLI, Pi CLI, DeepAgents) are public third-party
  tools, not the authors' evaluation code; their existence does not
  fill the shelf for the paper's VCR/interaction framework.
- Repo-slug note for the parent: unauthenticated API lookup of
  habib-analyst/harness-vcr returns 404 (slug appears free), but the
  parent must verify at creation time; this build creates nothing.

## G2 — disease (harness ranking by accuracy reverses across models): PASS
Head-to-head (seed 20261027, FRESH, 800 tasks, all pairings on the
same task list):
- strict: acc plain 0.4863 vs rich 0.0000; d_strict = +0.4863,
  95% CI [0.4513, 0.5213] -- excludes 0. Bar: >= 0.20. PASS.
- loose: acc rich 1.0000 vs plain 0.7313; d_loose = +0.2688,
  95% CI [0.2388, 0.3013] -- excludes 0. Bar: >= 0.15. PASS.
The same harness (rich) is the worst pairing for one agent and the
best pairing for the other -- the paper's core phenomenon (harness
rankings vary by model) reproduced at small scale.

## G3 — load-bearing (pairing VCR not predictable from marginals): PASS
- VCR interaction I = (0.4863 - 0.0000) - (1.0000 - 1.0000) = +0.4863,
  95% CI [0.4513, 0.5213] -- excludes 0. Bar: >= 0.20. PASS.
- Naive baseline (marginal-only additive model) miss on the
  strict/rich cell: -0.1216 (predicted VCR 0.1216 vs actual 0.0000);
  magnitude 0.1216 >= 0.05 bar. PASS. In the 2x2 case the residual
  equals -I/4 exactly, so the interaction IS the naive model's miss:
  component-level summaries (model marginals + harness marginals) do
  not determine pairing VCR.
- Descriptive: Cross-Model Fit (mean VCR) favours plain (0.743) over
  rich (0.500), yet rich is the accuracy-best harness for loose --
  picking by cross-model VCR alone would miss the best pairing.

## Determinism: PASS
Seed rerun reproduces digest a37af8dd6eb7e159 exactly.

## Scope honesty (binding)
- The paper's 52,168-trajectory evaluation is NOT reproduced and NOT
  claimed. This is a 2x2 scripted-agent study on 800 synthetic tasks.
- No real LLM run; no claim about OpenCode/Codex/Pi/DeepAgents or
  any real model. The result demonstrates that the paper's
  measurement framework surfaces a real pairing effect when the
  mechanisms are fully known -- it does not measure real
  model-harness fit.
- Ceiling effect stated: loose/rich accuracy is exactly 1.0000
  because the double-swap cancellation is exact by mechanism, not
  because a real agent is perfect. Token load is a whitespace-token
  proxy, not a real tokenizer count.
- Token Load (descriptive): rich costs loose 34.3 vs plain 10.1
  tokens/trajectory (~3.4x) for +26.9pp accuracy -- the paper's
  fifth measure, showing the accuracy gain is not free.

## Verdict: PASS -- REPO NEEDED (parent creates repo via browser flow)
Suggested slug: habib-analyst/harness-vcr (404 at check time; verify
at creation). No push made by this builder. LinkedIn draft is DRAFT
ONLY (lanes stopped per 2026-10-25 order).
