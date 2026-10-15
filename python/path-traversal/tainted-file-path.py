import os
import shutil
from pathlib import Path

from django.http import HttpResponse
from fastapi import FastAPI
from fastapi.responses import FileResponse
from flask import Flask, request, send_file, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = FastAPI()

DOCS = "/srv/app/user-docs"
BASE = Path("/srv/app/user-docs").resolve()


@app.get("/download")
def download():
    name = request.args["file"]
    # ruleid: tainted-file-path
    with open(os.path.join(DOCS, name), "rb") as f:
        data = f.read()
    # ok: tainted-file-path
    with open(os.path.join(DOCS, os.path.basename(name)), "rb") as f:
        data = f.read()
    # ok: tainted-file-path
    return send_from_directory(DOCS, name)


@app.get("/raw/<path:name>")
def raw(name):
    # ruleid: tainted-file-path
    return send_file(DOCS + "/" + name)


@app.post("/upload")
def upload():
    f = request.files["doc"]
    # ruleid: tainted-file-path
    f.save(open(os.path.join(DOCS, f.filename), "wb"))
    # ok: tainted-file-path
    f.save(open(os.path.join(DOCS, secure_filename(f.filename)), "wb"))
    return "ok"


@app.get("/fixed")
def fixed():
    name = request.args["file"]
    target = (BASE / name).resolve()
    if not target.is_relative_to(BASE) or not target.is_file():
        return "not found", 404
    # ok: tainted-file-path
    return target.read_bytes()


def django_delete(request, filename):
    # ruleid: tainted-file-path
    os.remove(os.path.join("/srv/uploads", filename))
    # ruleid: tainted-file-path
    shutil.rmtree("/srv/uploads/" + request.POST["folder"])
    return HttpResponse("deleted")


@api.get("/files/{name}")
def fastapi_file(name: str):
    # ruleid: tainted-file-path
    text = (BASE / name).read_text()
    # ruleid: tainted-file-path
    return FileResponse(f"/srv/app/user-docs/{name}")


def rotate_logs(directory):
    # ok: tainted-file-path
    os.remove(os.path.join(directory, "app.log.1"))
