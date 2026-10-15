import json

from bson import ObjectId
from fastapi import FastAPI
from flask import Flask, abort, request

app = Flask(__name__)
api = FastAPI()


@app.post("/login")
def login():
    body = request.get_json()
    # ruleid: tainted-mongodb-filter
    user = db.users.find_one({"username": body["username"], "password": body["password"]})
    username = body.get("username")
    password = body.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        abort(400)
    # ok: tainted-mongodb-filter
    user = db.users.find_one({"username": str(username), "password": str(password)})
    return {"ok": user is not None}


@app.get("/by-name")
def by_name():
    # ok: tainted-mongodb-filter
    return db.users.find_one({"name": request.args.get("name")})


@api.post("/search")
async def search(query: dict):
    # ruleid: tainted-mongodb-filter
    cursor = db.orders.find({"owner": query["owner"]})
    # ok: tainted-mongodb-filter
    doc = db.orders.find_one({"_id": ObjectId(query["id"])})
    return list(cursor)


def django_delete(request):
    payload = json.loads(request.body)
    # ruleid: tainted-mongodb-filter
    db.sessions.delete_many({"token": payload["token"]})


def text_search(request):
    # ok: tainted-mongodb-filter
    return "haystack".find(request.body)
