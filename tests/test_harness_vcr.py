import sys

sys.path.insert(0, "src")

from harness_vcr.agents import AGENTS, tool_compute
from harness_vcr.harnesses import HARNESSES
from harness_vcr.run import run
from harness_vcr.tasks import Task, apply_op, generate_tasks


def _task(ops, start=12):
    return Task(0, start, ops)


def test_strict_plain_exact():
    t = _task([("add", 3), ("mul", 2)])  # 12+3=15, *2=30
    out = AGENTS["strict"].run(t, HARNESSES["plain"])
    assert out["valid"] and out["answer"] == 30


def test_strict_rich_aborts():
    t = _task([("add", 3)])
    out = AGENTS["strict"].run(t, HARNESSES["rich"])
    assert not out["valid"] and out["answer"] is None


def test_strict_mod_aborts():
    t = _task([("mod", 5)])
    out = AGENTS["strict"].run(t, HARNESSES["plain"])
    assert not out["valid"]


def test_loose_plain_div_wrong():
    # 12 div 3 = 4 correct; loose sends swapped (3 div 12 = 0) -> wrong
    t = _task([("div", 3)])
    out = AGENTS["loose"].run(t, HARNESSES["plain"])
    assert out["valid"] and out["answer"] != 4


def test_loose_rich_div_correct_via_double_swap():
    t = _task([("div", 3)])
    out = AGENTS["loose"].run(t, HARNESSES["rich"])
    assert out["valid"] and out["answer"] == 4


def test_loose_rich_sub_correct():
    # non-div ops must survive the JSON path exactly: 12-5=7
    t = _task([("sub", 5)])
    out = AGENTS["loose"].run(t, HARNESSES["rich"])
    assert out["valid"] and out["answer"] == 7


def test_loose_plain_sub_correct():
    t = _task([("sub", 5)])
    out = AGENTS["loose"].run(t, HARNESSES["plain"])
    assert out["valid"] and out["answer"] == 7


def test_tool_div_zero_degenerate():
    assert tool_compute(("div", 5, 0)) == 0


def test_task_generation_deterministic_and_mixed():
    a = generate_tasks(200, 7)
    b = generate_tasks(200, 7)
    assert [(t.start, t.ops) for t in a] == [(t.start, t.ops) for t in b]
    assert all(t.ground_truth() == _recompute(t) for t in a)
    div_share = sum(t.has_op("div") for t in a) / 200
    mod_share = sum(t.has_op("mod") for t in a) / 200
    assert 0.25 < div_share < 0.65, div_share
    assert 0.15 < mod_share < 0.55, mod_share


def _recompute(t):
    v = t.start
    for op, operand in t.ops:
        v = apply_op(v, op, operand)
    return v


def test_run_deterministic_small():
    r1 = run(999, 60)
    r2 = run(999, 60)
    assert r1["digest"] == r2["digest"]
    assert r1["cells"]["strict/rich"]["vcr"] == 0.0
    assert r1["cells"]["loose/plain"]["vcr"] == 1.0
    assert r1["cells"]["loose/rich"]["vcr"] == 1.0
