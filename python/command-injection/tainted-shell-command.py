import asyncio
import os
import shlex
import subprocess

from django.http import HttpResponse
from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.post("/thumbnail")
def thumbnail():
    name = request.form["name"]
    # ruleid: tainted-shell-command
    subprocess.run(f"convert uploads/{name} -resize 200x200 thumbs/{name}", shell=True, check=True)
    # ok: tainted-shell-command
    subprocess.run(["convert", "--", f"uploads/{name}", "-resize", "200x200", f"thumbs/{name}"], check=True)
    # ok: tainted-shell-command
    subprocess.run("convert uploads/" + shlex.quote(name) + " out.png", shell=True)
    return "ok"


@app.route("/ping/<host>")
def ping(host):
    # ruleid: tainted-shell-command
    os.system("ping -c 1 " + host)
    # ruleid: tainted-shell-command
    out = subprocess.check_output("nslookup %s" % host, shell=True)
    # ruleid: tainted-shell-command
    status, text = subprocess.getstatusoutput("dig " + host)
    # ok: tainted-shell-command
    os.system("uptime")
    return out


def django_archive(request):
    target = request.GET.get("dir")
    # ruleid: tainted-shell-command
    pipe = os.popen("tar czf /tmp/out.tgz " + target)
    return HttpResponse(pipe.read())


@api.get("/lookup")
async def lookup(domain: str):
    # ruleid: tainted-shell-command
    proc = await asyncio.create_subprocess_shell(f"whois {domain}")
    # ok: tainted-shell-command
    proc = await asyncio.create_subprocess_exec("whois", "--", domain)
    return {"pid": proc.pid}


@api.post("/remote")
def remote(cmd: str):
    client = paramiko.SSHClient()
    # ruleid: tainted-shell-command
    client.exec_command("ls " + cmd)
    return {}


def cron_task(path):
    # ok: tainted-shell-command
    os.system("gzip " + path)
