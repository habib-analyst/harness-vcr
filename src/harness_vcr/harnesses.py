"""Two scripted harnesses: how tool results are delivered to the agent.

plain: tool output is exactly ``VALUE: <v>`` -- one line, one integer.
rich:  tool output is a JSON envelope carrying the result and an echo of
       the operands the tool received, in the order received, plus a
       next-op hint. The envelope is strictly more informative than
       plain, but its format is not ``VALUE: <v>``.

Neither harness knows which agent is attached, and neither hard-codes
any per-pairing outcome: a harness's behaviour is a function of the tool
result and the received instruction only.
"""
import json


class Harness:
    name = ""

    def format_result(self, result, instruction, next_op):
        raise NotImplementedError


class PlainHarness(Harness):
    name = "plain"

    def format_result(self, result, instruction, next_op):
        return "VALUE: %d" % result


class RichHarness(Harness):
    name = "rich"

    def format_result(self, result, instruction, next_op):
        op, a, b = instruction
        return json.dumps(
            {"result": result, "operands": [a, b],
             "hint": "next: %s" % (next_op or "done")}
        )


HARNESSES = {"plain": PlainHarness(), "rich": RichHarness()}
