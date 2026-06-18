"""Deterministic-first answer verification for Grade 4 Mathematics."""
from __future__ import annotations

import ast
import hashlib
import operator
from dataclasses import dataclass


class AnswerVerificationError(ValueError):
    pass


@dataclass(frozen=True)
class AnswerVerificationOutcome:
    status: str
    question_hash: str
    answer_hash: str
    expected_answer: str | None
    observed_answer: str | None
    checker_type: str = "deterministic_arithmetic"
    checker_version: str = "phase02r.v1"


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _eval_arithmetic(expression: str) -> float:
    node = ast.parse(expression, mode="eval")

    def visit(current: ast.AST) -> float:
        if isinstance(current, ast.Expression):
            return visit(current.body)
        if isinstance(current, ast.Constant) and isinstance(current.value, (int, float)):
            return float(current.value)
        if isinstance(current, ast.UnaryOp) and isinstance(current.op, ast.USub):
            return -visit(current.operand)
        if isinstance(current, ast.BinOp) and type(current.op) in _ALLOWED_OPERATORS:
            return float(_ALLOWED_OPERATORS[type(current.op)](visit(current.left), visit(current.right)))
        raise AnswerVerificationError("unsupported arithmetic expression")

    return visit(node)


class DeterministicMathAnswerVerifier:
    def verify_arithmetic_expression(self, *, question_expression: str, proposed_answer: str) -> AnswerVerificationOutcome:
        expected = _eval_arithmetic(question_expression)
        expected_text = str(int(expected)) if expected.is_integer() else str(expected)
        observed = proposed_answer.strip()
        status = "passed" if observed == expected_text else "failed"
        return AnswerVerificationOutcome(
            status=status,
            question_hash=_sha(question_expression),
            answer_hash=_sha(proposed_answer),
            expected_answer=expected_text,
            observed_answer=observed,
        )
