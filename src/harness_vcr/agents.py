"""Two scripted agents and the tool they drive.

Setting: at each step the agent sends the tool an instruction
``(op, a, b)``; the tool faithfully computes ``a op b`` (division by
zero yields 0, a documented degenerate case) and the harness renders
the result. The agent's running value is whatever it adopts from the
rendered output.

strict: sends instructions exactly as specified; adopts the result only
        if the rendering matches ``^VALUE: (-?\\d+)$`` exactly, else
        aborts with no evaluable answer; does not support ``mod`` and
        aborts on it. Otherwise exact.
loose:  sends ``div`` instructions with operands SWAPPED (a documented
        systematic sending bug); on plain renderings it adopts the
        scalar, so the swapped computation stands and div steps go
        wrong; on JSON renderings it recomputes the step from the
        echoed operands, applying its div-swap again -- so on div
        steps the two swaps cancel and the result is correct, while
        non-div steps recompute exactly from the echo.

No rule in either agent or either harness mentions a pairing, and no
cell outcome is hard-coded. The pairing effects measured in the
experiment EMERGE from these independent component rules:
parser strictness x envelope format (strict/rich aborts),
op support (strict/mod aborts), and the double-swap cancellation
(loose/rich correct on div, loose/plain wrong on div). This is
precisely the class of effect the paper's Interaction Residuals
measure is designed to surface -- and precisely why the writeup must
state that this is a constructed mechanism demo with scripted agents,
not a measurement of real LLMs.
"""
import json
import re

from .tasks import apply_op

_STRICT_RE = re.compile(r"^VALUE: (-?\d+)$")


def tool_compute(instruction):
    op, a, b = instruction
    if op == "div" and b == 0:
        return 0
    return apply_op(a, op, b)


def _tokens(text):
    return len(text.split())


class Agent:
    name = ""

    def run(self, task, harness):
        """Returns dict(valid, answer, steps, tool_tokens, agent_tokens).

        valid=False means no evaluable result was delivered (VCR failure).
        """
        raise NotImplementedError


class StrictAgent(Agent):
    name = "strict"

    def run(self, task, harness):
        value = task.start
        tool_tokens = 0
        steps = 0
        for j, (op, operand) in enumerate(task.ops):
            if op == "mod":
                return {"valid": False, "answer": None, "steps": steps,
                        "tool_tokens": tool_tokens, "agent_tokens": 0}
            instruction = (op, value, operand)
            result = tool_compute(instruction)
            nxt = task.ops[j + 1][0] if j + 1 < len(task.ops) else None
            out = harness.format_result(result, instruction, nxt)
            tool_tokens += _tokens(out)
            steps += 1
            m = _STRICT_RE.match(out.strip())
            if not m:
                return {"valid": False, "answer": None, "steps": steps,
                        "tool_tokens": tool_tokens, "agent_tokens": 0}
            value = int(m.group(1))
        answer = "ANSWER: %d" % value
        return {"valid": True, "answer": value, "steps": steps,
                "tool_tokens": tool_tokens,
                "agent_tokens": _tokens(answer)}


class LooseAgent(Agent):
    name = "loose"

    def run(self, task, harness):
        value = task.start
        tool_tokens = 0
        steps = 0
        for j, (op, operand) in enumerate(task.ops):
            if op == "div":
                instruction = (op, operand, value)  # sending bug: swapped
            else:
                instruction = (op, value, operand)
            result = tool_compute(instruction)
            nxt = task.ops[j + 1][0] if j + 1 < len(task.ops) else None
            out = harness.format_result(result, instruction, nxt)
            tool_tokens += _tokens(out)
            steps += 1
            try:
                parsed = json.loads(out)
                a, b = parsed["operands"]
                if op == "div":
                    value = tool_compute((op, b, a))  # swap again: cancels
                else:
                    value = tool_compute((op, a, b))
            except (ValueError, KeyError, TypeError):
                m = re.search(r"-?\d+", out)
                if not m:
                    return {"valid": False, "answer": None, "steps": steps,
                            "tool_tokens": tool_tokens, "agent_tokens": 0}
                value = int(m.group(0))
        answer = "ANSWER: %d" % value
        return {"valid": True, "answer": value, "steps": steps,
                "tool_tokens": tool_tokens,
                "agent_tokens": _tokens(answer)}


AGENTS = {"strict": StrictAgent(), "loose": LooseAgent()}
