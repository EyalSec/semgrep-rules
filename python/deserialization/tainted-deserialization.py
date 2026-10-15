import base64
import json
import marshal
import pickle

import jsonpickle
import yaml
from fastapi import FastAPI, Request
from flask import Flask, request
from itsdangerous import URLSafeSerializer

app = Flask(__name__)
api = FastAPI()
serializer = URLSafeSerializer("secret-key", salt="session")


@app.route("/session")
def load_session():
    raw = base64.b64decode(request.cookies["session"])
    # ruleid: tainted-deserialization
    data = pickle.loads(raw)
    # ok: tainted-deserialization
    data = serializer.loads(request.cookies["session"])
    # ok: tainted-deserialization
    data = json.loads(raw)
    return data


@app.post("/config")
def upload_config():
    body = request.get_data()
    # ruleid: tainted-deserialization
    cfg = yaml.load(body, Loader=yaml.Loader)
    # ruleid: tainted-deserialization
    cfg = yaml.unsafe_load(body)
    # ok: tainted-deserialization
    cfg = yaml.safe_load(body)
    # ok: tainted-deserialization
    cfg = yaml.load(body, Loader=yaml.SafeLoader)
    return cfg


def django_import(request):
    # ruleid: tainted-deserialization
    obj = jsonpickle.decode(request.body)
    # ruleid: tainted-deserialization
    code = marshal.loads(request.FILES["blob"].read())
    return obj, code


@api.post("/model")
async def upload_model(request: Request):
    blob = await request.body()
    # ruleid: tainted-deserialization
    model = pickle.loads(blob)
    return {"type": type(model).__name__}


def load_cache(path):
    with open(path, "rb") as f:
        # ok: tainted-deserialization
        return pickle.load(f)
