import subprocess

from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.post("/clone")
def clone():
    url = request.form["url"]
    # ruleid: tainted-subprocess-argument
    subprocess.run(["git", "clone", url, "/srv/repos/new"], check=True)
    # ok: tainted-subprocess-argument
    subprocess.run(["git", "clone", "--", url, "/srv/repos/new"], check=True)
    return "ok"


@api.get("/fetch")
def fetch(target: str):
    # ruleid: tainted-subprocess-argument
    out = subprocess.check_output(["curl", "-s", target])
    # ok: tainted-subprocess-argument
    out = subprocess.check_output(["curl", "-s", "--", target])
    return {"body": out}


def django_view(request):
    rev = request.GET["rev"]
    # ruleid: tainted-subprocess-argument
    subprocess.run(["git", "show", rev])
    # ok: tainted-subprocess-argument
    subprocess.run(["git", "show", "HEAD"])
