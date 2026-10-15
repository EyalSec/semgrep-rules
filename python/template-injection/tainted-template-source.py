import jinja2
from django.http import HttpResponse
from django.template import Context, Template
from fastapi import FastAPI
from flask import Flask, render_template_string, request

app = Flask(__name__)
api = FastAPI()
env = jinja2.Environment()


@app.get("/hello")
def hello():
    name = request.args.get("name", "there")
    # ruleid: tainted-template-source
    html = render_template_string(f"<h1>Hello {name}</h1>")
    # ok: tainted-template-source
    html = render_template_string("<h1>Hello {{ name }}</h1>", name=name)
    return html


def django_greeting(request):
    greeting = request.GET.get("greeting")
    # ruleid: tainted-template-source
    tpl = Template("<p>" + greeting + "</p>")
    # ok: tainted-template-source
    tpl = Template("<p>{{ greeting }}</p>")
    return HttpResponse(tpl.render(Context({"greeting": greeting})))


@api.post("/render")
def render(body: str):
    # ruleid: tainted-template-source
    out = env.from_string(body).render()
    # ruleid: tainted-template-source
    out = jinja2.Template(body).render()
    # ok: tainted-template-source
    out = env.from_string("Hi {{ body }}").render(body=body)
    return out


def version_parse(request):
    # ok: tainted-template-source
    return Version.from_string(request.GET["v"])
