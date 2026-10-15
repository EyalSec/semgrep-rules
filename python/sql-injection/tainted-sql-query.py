import sqlite3

import psycopg2
from django.db import connection
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from fastapi import Depends, FastAPI
from flask import Flask, request
from psycopg2 import sql
from sqlalchemy import select, text

app = Flask(__name__)
api = FastAPI()


# Flask
@app.route("/users")
def flask_users():
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    # ruleid: tainted-sql-query
    rows = conn.execute(f"SELECT id, email FROM users WHERE name = '{name}'").fetchall()
    # ok: tainted-sql-query
    rows = conn.execute("SELECT id, email FROM users WHERE name = ?", (name,)).fetchall()
    return {"rows": rows}


@app.route("/orders/<ref>")
def flask_order(ref):
    cur = psycopg2.connect("dbname=app").cursor()
    # ruleid: tainted-sql-query
    cur.execute("SELECT * FROM orders WHERE ref = '%s'" % ref)
    # ok: tainted-sql-query
    cur.execute("SELECT * FROM orders WHERE ref = %s", (ref,))
    return {"rows": cur.fetchall()}


@app.route("/sorted")
def flask_sorted():
    column = request.args.get("sort")
    cur = psycopg2.connect("dbname=app").cursor()
    # ruleid: tainted-sql-query
    cur.execute(sql.SQL("SELECT * FROM orders ORDER BY " + column))
    # ok: tainted-sql-query
    cur.execute(sql.SQL("SELECT * FROM orders ORDER BY {}").format(sql.Identifier(column)))
    SORTABLE = {"created": "created_at", "total": "amount"}
    safe = SORTABLE.get("created")
    # ok: tainted-sql-query
    cur.execute(f"SELECT * FROM orders ORDER BY {safe}")
    return {"rows": cur.fetchall()}


@app.route("/count")
def flask_count():
    limit = int(request.args["limit"])
    cur = psycopg2.connect("dbname=app").cursor()
    # ok: tainted-sql-query
    cur.execute(f"SELECT * FROM orders LIMIT {limit}")
    return {"rows": cur.fetchall()}


# Django
def django_search(request):
    username = request.GET["username"]
    # ruleid: tainted-sql-query
    users = User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{username}'")
    # ok: tainted-sql-query
    users = User.objects.raw("SELECT * FROM auth_user WHERE username = %s", [username])
    last = request.POST.get("last")
    # ruleid: tainted-sql-query
    people = User.objects.extra(where=[f"last_name = '{last}'"])
    # ok: tainted-sql-query
    people = User.objects.filter(last_name=last)
    return JsonResponse({"n": len(list(users)) + people.count()})


def django_report(request, year):
    with connection.cursor() as cursor:
        # ruleid: tainted-sql-query
        cursor.execute("SELECT * FROM sales WHERE year = " + year)
        # ok: tainted-sql-query
        cursor.execute("SELECT * FROM sales WHERE year = %s", [year])
        return JsonResponse({"rows": cursor.fetchall()})


def django_annotate(request):
    expr = request.GET.get("expr")
    # ruleid: tainted-sql-query
    qs = Order.objects.annotate(val=RawSQL("SELECT " + expr, ()))
    # ok: tainted-sql-query
    qs = Order.objects.annotate(val=RawSQL("SELECT price * %s", (expr,)))
    return JsonResponse({"n": qs.count()})


# FastAPI with SQLAlchemy
@api.get("/orders")
def fastapi_orders(ref: str, db: Session = Depends(get_db)):
    # ruleid: tainted-sql-query
    rows = db.execute(text(f"SELECT * FROM orders WHERE ref = '{ref}'")).all()
    # ok: tainted-sql-query
    rows = db.execute(text("SELECT * FROM orders WHERE ref = :ref"), {"ref": ref}).all()
    # ok: tainted-sql-query
    rows = db.execute(select(Order).where(Order.ref == ref)).all()
    # ok: tainted-sql-query
    rows = db.execute(text("SELECT * FROM orders WHERE ref = :ref").bindparams(ref=ref)).all()
    return rows


@api.post("/raw")
async def fastapi_raw(payload: dict, db=Depends(get_db)):
    query = "DELETE FROM sessions WHERE token = '" + payload["token"] + "'"
    # ruleid: tainted-sql-query
    await db.exec_driver_sql(query)
    # ok: tainted-sql-query
    await db.exec_driver_sql("DELETE FROM sessions WHERE token = %(t)s", {"t": payload["token"]})


# Not request data
def nightly_job(conn):
    table = "orders"
    # ok: tainted-sql-query
    conn.execute(f"VACUUM {table}")
