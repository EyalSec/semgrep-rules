import ctypes
import importlib

from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()

EXPORTERS = {"csv": "exporters.csv_export", "xlsx": "exporters.xlsx_export"}
ACTIONS = {"archive": handlers.archive, "restore": handlers.restore}


@app.get("/export")
def export():
    fmt = request.args["format"]
    # ruleid: tainted-import-or-attribute
    exporter = importlib.import_module(fmt).export
    # ok: tainted-import-or-attribute
    exporter = importlib.import_module(EXPORTERS["csv"]).export
    if fmt not in EXPORTERS:
        raise ValueError(f"unknown format {fmt!r}")
    # ok: tainted-import-or-attribute
    exporter = importlib.import_module(EXPORTERS[fmt]).export
    return exporter()


@app.get("/export2")
def export2():
    fmt = request.args["format"]
    # ok: tainted-import-or-attribute
    exporter = importlib.import_module(EXPORTERS.get(fmt, "exporters.csv_export")).export
    # ruleid: tainted-import-or-attribute
    exporter = importlib.import_module(exporters_by_name.get(fmt)).export
    return exporter()


@api.post("/action/{action}")
def act(action: str, payload: dict):
    # ruleid: tainted-import-or-attribute
    result = getattr(handlers, action)(payload)
    # ok: tainted-import-or-attribute
    result = ACTIONS["archive"](payload)
    # ok: tainted-import-or-attribute
    result = getattr(handlers, "archive")(payload)
    return result


def django_profile(request):
    user = request.user
    for field, value in request.POST.items():
        # ruleid: tainted-import-or-attribute
        setattr(user, field, value)
    # ok: tainted-import-or-attribute
    setattr(user, "first_name", request.POST.get("first_name"))
    user.save()


def django_plugin(request):
    # ruleid: tainted-import-or-attribute
    lib = ctypes.CDLL(request.GET["lib"])
    # ruleid: tainted-import-or-attribute
    mod = __import__(request.GET["mod"])
    return lib, mod
