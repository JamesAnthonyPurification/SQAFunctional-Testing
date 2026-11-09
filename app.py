"""Flask web interface and JSON API for executing and inspecting target.py functions."""

import ast
import inspect
import os

from flask import Flask, jsonify, render_template, request

import target

app = Flask(__name__)

COMMIT_SHA = os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("COMMIT_SHA", "local")

FUNCTIONS = {
    fn_name: fn_obj
    for fn_name, fn_obj in inspect.getmembers(target, inspect.isfunction)
    if fn_obj.__module__ == "target"
}


def parse_arg(raw_input):
    """Convert raw form input into a Python literal (int, float, None, list, set, dict) or str."""
    text = raw_input.strip()
    if text == "":
        return ""
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text


def signature_of(fn_obj):
    """Return parameter names for a target function."""
    return [param.name for param in inspect.signature(fn_obj).parameters.values()]


@app.get("/")
def index():
    function_cards = [
        {
            "name": fn_name,
            "params": signature_of(fn_obj),
            "doc": (inspect.getcomments(fn_obj) or "").strip("# \n"),
        }
        for fn_name, fn_obj in FUNCTIONS.items()
    ]
    return render_template("index.html", funcs=function_cards, sha=COMMIT_SHA)


@app.get("/health")
def health():
    return jsonify(status="ok", sha=COMMIT_SHA)


@app.post("/api/run/<name>")
def run(name):
    fn_obj = FUNCTIONS.get(name)
    if fn_obj is None:
        return jsonify(ok=False, error="UnknownFunction", message=name), 404
    payload = request.get_json(silent=True) or {}
    raw_args = payload.get("args", [])
    parsed_args = [parse_arg(item) if isinstance(item, str) else item for item in raw_args]
    try:
        output = fn_obj(*parsed_args)
    except Exception as exc:  # noqa: BLE001 - return exception details in API response
        return jsonify(ok=False, error=type(exc).__name__, message=str(exc))
    if isinstance(output, set):
        formatted = repr(output) if output else "set()"
    else:
        formatted = repr(output)
    return jsonify(ok=True, result=formatted, type=type(output).__name__)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
