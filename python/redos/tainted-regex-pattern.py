import re

from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.get("/search")
def search():
    term = request.args["q"]
    # ruleid: tainted-regex-pattern
    hits = [line for line in LINES if re.search(term, line)]
    # ok: tainted-regex-pattern
    hits = [line for line in LINES if re.search(re.escape(term), line)]
    # ok: tainted-regex-pattern
    hits = [line for line in LINES if re.search(r"^[a-z]+$", term)]
    return {"hits": hits}


@api.get("/filter")
def filter_names(pattern: str):
    # ruleid: tainted-regex-pattern
    rx = re.compile(pattern)
    return [n for n in NAMES if rx.match(n)]


def django_validate(request):
    # ruleid: tainted-regex-pattern
    return bool(re.fullmatch(request.GET["rule"], request.GET["value"]))
