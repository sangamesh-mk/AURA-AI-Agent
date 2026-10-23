
import ast
import operator
from datetime import datetime

# Only these arithmetic operations are permitted.
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str):
    """Safely evaluate a basic arithmetic expression."""
    print(f"\n[TOOL EXECUTED] calculate(expression={expression!r})")

    try:
        tree = ast.parse(expression, mode="eval")

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if (
                isinstance(node, ast.Constant)
                and type(node.value) in (int, float)
            ):
                return node.value

            if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
                left = evaluate(node.left)
                right = evaluate(node.right)

                if isinstance(node.op, ast.Pow) and abs(right) > 10:
                    raise ValueError("Exponent is too large.")

                result = _OPERATORS[type(node.op)](left, right)

                if isinstance(result, (int, float)) and abs(result) > 1e100:
                    raise ValueError("Result is too large.")

                return result

            if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
                return _OPERATORS[type(node.op)](evaluate(node.operand))

            raise ValueError("Only basic arithmetic is allowed.")

        return evaluate(tree)

    except (
        SyntaxError,
        ValueError,
        TypeError,
        ZeroDivisionError,
        OverflowError,
    ) as error:
        return f"Calculation error: {error}"


def get_current_datetime():
    """Return the computer's current local date and time."""
    now = datetime.now().astimezone()
    result = now.strftime("%A, %d %B %Y, %I:%M:%S %p %Z")

    print(f"\n[TOOL EXECUTED] get_current_datetime()")
    return result
