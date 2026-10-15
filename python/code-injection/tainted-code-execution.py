import ast
import json

from django.http import JsonResponse
from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.post("/saved-filters")
def save_filters():
    # ruleid: tainted-code-execution
    filters = eval(request.form["filters"])
    # ok: tainted-code-execution
    filters = json.loads(request.form["filters"])
    # ok: tainted-code-execution
    filters = ast.literal_eval(request.form["filters"])
    return "saved"


def django_calc(request):
    expr = request.GET.get("expr")
    # ruleid: tainted-code-execution
    code = compile(expr, "<calc>", "eval")
    # ok: tainted-code-execution
    code = compile("1 + 1", "<calc>", "eval")
    return JsonResponse({"ok": True})


@api.post("/hook")
async def hook(body: str):
    scope = {}
    # ruleid: tainted-code-execution
    exec(body, scope)
    # ok: tainted-code-execution
    exec("x = 1", scope)
    return scope
