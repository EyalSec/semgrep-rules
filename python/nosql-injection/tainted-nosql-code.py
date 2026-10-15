from fastapi import FastAPI
from flask import Flask, request

app = Flask(__name__)
api = FastAPI()


@app.get("/active")
def active():
    days = request.args.get("days")
    # ruleid: tainted-nosql-code
    users = db.users.find({"$where": "this.last_login > Date.now() - " + days})
    # ok: tainted-nosql-code
    users = db.users.find({"last_login": {"$gt": int(days)}})
    return list(users)


@api.post("/script")
def script(lua: str, key: str):
    # ruleid: tainted-nosql-code
    r.eval(lua, 1, key)
    # ok: tainted-nosql-code
    r.eval("return redis.call('GET', KEYS[1])", 1, key)
    return {}


@app.get("/explain")
def explain():
    where = request.args.get("where")
    # ok: tainted-nosql-code
    return {"filter": {"$where": where}}
