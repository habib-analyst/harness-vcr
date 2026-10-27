"""Synthetic task suite: chains of integer arithmetic operations.

A task is a starting value plus a list of ops (add, sub, mul, div, mod).
Division tasks are constructed so the correct result is always an exact
integer (divisor chosen as a divisor of the running value), so an exact
agent can always answer. Tasks are generated deterministically from a seed;
the generator never sees agent or harness code, so no pairing is favoured
by construction at the task level.
"""
import random

OPS = ("add", "sub", "mul", "div", "mod")


def apply_op(value, op, operand):
    if op == "add":
        return value + operand
    if op == "sub":
        return value - operand
    if op == "mul":
        return value * operand
    if op == "div":
        return value // operand  # exact by construction
    if op == "mod":
        return value % operand
    raise ValueError(op)


class Task:
    def __init__(self, task_id, start, ops):
        self.task_id = task_id
        self.start = start
        self.ops = ops  # list of (op, operand)

    def ground_truth(self):
        v = self.start
        for op, operand in self.ops:
            v = apply_op(v, op, operand)
        return v

    def has_op(self, op):
        return any(o == op for o, _ in self.ops)


def generate_tasks(n, seed):
    """Deterministic task generation.

    Mix (fixed by construction, independent of agents/harnesses):
    lengths 2..6; op mix weighted so ~40% of tasks contain div and
    ~30% contain mod (verified in tests, not assumed in analysis).
    """
    rng = random.Random(seed)
    tasks = []
    for i in range(n):
        length = rng.choice([2, 3, 4, 5, 6])
        start = rng.randint(2, 50)
        ops = []
        value = start
        for _ in range(length):
            op = rng.choices(
                ["add", "sub", "mul", "div", "mod"],
                weights=[3, 3, 2, 2, 2],
            )[0]
            if op == "div":
                # pick a divisor of the current value (nonzero, not 1-only)
                divisors = [d for d in range(2, 13) if value % d == 0]
                if not divisors:
                    op, operand = "add", rng.randint(1, 9)
                else:
                    operand = rng.choice(divisors)
            elif op == "mod":
                operand = rng.randint(2, 11)
            else:
                operand = rng.randint(1, 9)
            ops.append((op, operand))
            value = apply_op(value, op, operand)
        tasks.append(Task(i, start, ops))
    return tasks
