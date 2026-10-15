import urllib.request

import httpx
import requests
from django.http import JsonResponse
from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.post("/preview")
def preview():
    url = request.form["url"]
    # ruleid: tainted-outbound-url
    resp = requests.get(url, timeout=5)
    # ok: tainted-outbound-url
    resp = requests.get(f"https://api.example.com/preview/{url}", timeout=5)
    # ok: tainted-outbound-url
    resp = requests.get("https://api.example.com/users/%s" % url, timeout=5)
    return {"status": resp.status_code}


@app.get("/proxy")
def proxy():
    host = request.args.get("host")
    # ruleid: tainted-outbound-url
    resp = requests.get(f"http://{host}/status")
    with requests.Session() as session:
        # ruleid: tainted-outbound-url
        resp = session.post("https://" + host + "/hook", json={})
    return resp.text


def django_fetch(request):
    target = request.GET["target"]
    # ruleid: tainted-outbound-url
    body = urllib.request.urlopen(target).read()
    return JsonResponse({"len": len(body)})


@api.get("/webhook-test")
async def webhook_test(callback: str):
    async with httpx.AsyncClient() as client:
        # ruleid: tainted-outbound-url
        r = await client.get(callback)
        # ok: tainted-outbound-url
        r = await client.get("https://hooks.example.com/ping", params={"cb": callback})
    return {"status": r.status_code}


@api.get("/fetch")
def fetch(url: str):
    # ruleid: tainted-outbound-url
    return httpx.get(url).text


def health(url):
    # ok: tainted-outbound-url
    return requests.get(url).ok
