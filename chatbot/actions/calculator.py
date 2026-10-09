"""A small arithmetic action that evaluates no arbitrary Python code."""

import ast
import operator
import re
from typing import Union


Number = Union[int, float]
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> Number:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent must be between -10 and 10")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Only basic arithmetic expressions are supported")


def calculate(message: str, context=None) -> str:
    """Evaluate a short arithmetic expression using a restricted AST."""
    expression = message.casefold().replace("calculate", "", 1).replace("compute", "", 1)
    expression = re.sub(r"^\s*what is\s+", "", expression).strip().rstrip("? ")
    if len(expression) > 100:
        raise ValueError("Expression is too long")
    try:
        result = _evaluate(ast.parse(expression, mode="eval").body)
    except (SyntaxError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("Please provide a valid arithmetic expression") from error
    return str(result)