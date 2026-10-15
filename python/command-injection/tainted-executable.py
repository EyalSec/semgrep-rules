import os
import subprocess

from flask import Flask, request

app = Flask(__name__)

TOOLS = {"lint": "/usr/bin/ruff", "fmt": "/usr/bin/black"}


@app.post("/run")
def run_tool():
    tool = request.form["tool"]
    # ruleid: tainted-executable
    subprocess.run([tool, "--version"])
    # ruleid: tainted-executable
    subprocess.Popen(tool)
    # ruleid: tainted-executable
    os.execvp(tool, [tool])
    # ok: tainted-executable
    subprocess.run([TOOLS.get("lint"), "--version"])
    return "ok"


def django_spawn(request):
    prog = request.POST.get("prog")
    # ruleid: tainted-executable
    os.spawnl(os.P_WAIT, prog, prog)
    # ok: tainted-executable
    os.spawnl(os.P_WAIT, "/usr/bin/true", "true")
