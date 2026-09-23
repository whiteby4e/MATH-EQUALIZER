import ast
import math
import numpy as np


_ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "log": np.log,
    "log10": np.log10,
    "floor": np.floor,
    "ceil": np.ceil,
}

_ALLOWED_FUNCTIONS = {
    "sin",
    "cos",
    "tan",
    "exp",
    "sqrt",
    "abs",
    "log",
    "log10",
    "floor",
    "ceil",
}

_ALLOWED_NODES = (
    ast.Expression,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.Call,
)


class FormulaError(ValueError):
    pass


class SafeFormula:
    def __init__(self, expression: str):
        self.expression = expression.strip()

        if not self.expression:
            raise FormulaError("Formula is empty.")

        try:
            self.tree = ast.parse(self.expression, mode="eval")
        except SyntaxError as exc:
            raise FormulaError(
                f"Syntax error: {exc.msg}"
            ) from exc

        self._validate(self.tree)

        try:
            self.code = compile(
                self.tree,
                "<math_formula>",
                "eval"
            )
        except Exception as exc:
            raise FormulaError(str(exc)) from exc

    def _validate(self, tree):
        for node in ast.walk(tree):

            if not isinstance(node, _ALLOWED_NODES):
                raise FormulaError(
                    f"Unsupported expression: "
                    f"{type(node).__name__}"
                )

            if isinstance(node, ast.Name):
                if node.id != "t" and node.id not in _ALLOWED_NAMES:
                    raise FormulaError(
                        f"Unknown name: {node.id}"
                    )

            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    raise FormulaError(
                        "Only simple math functions are allowed."
                    )

                if node.func.id not in _ALLOWED_FUNCTIONS:
                    raise FormulaError(
                        f"Function not allowed: {node.func.id}"
                    )

                if node.keywords:
                    raise FormulaError(
                        "Keyword arguments are not allowed."
                    )

            if isinstance(node, ast.Constant):
                if isinstance(node.value, bool):
                    raise FormulaError(
                        "Boolean values are not allowed."
                    )

                if not isinstance(
                    node.value,
                    (int, float)
                ):
                    raise FormulaError(
                        "Only numeric constants are allowed."
                    )

    def evaluate(self, t):
        t = np.asarray(t, dtype=np.float64)

        env = dict(_ALLOWED_NAMES)
        env["t"] = t

        try:
            value = eval(
                self.code,
                {
                    "__builtins__": {}
                },
                env
            )
        except Exception as exc:
            raise FormulaError(str(exc)) from exc

        value = np.asarray(
            value,
            dtype=np.float64
        )

        if value.ndim == 0:
            value = np.full_like(
                t,
                float(value)
            )

        if value.shape != t.shape:
            try:
                value = np.broadcast_to(
                    value,
                    t.shape
                ).copy()
            except Exception as exc:
                raise FormulaError(
                    "Formula result has an invalid shape."
                ) from exc

        if not np.all(np.isfinite(value)):
            raise FormulaError(
                "Formula produced NaN or infinity."
            )

        return value

    def scalar(self, t: float) -> float:
        value = self.evaluate(
            np.array([t], dtype=np.float64)
        )

        return float(value[0])