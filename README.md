# EyalSec Semgrep rules for Python

Semgrep rules that find request data reaching a SQL query, a shell command, a
deserializer, a file path or an outbound URL in Django, Flask and FastAPI code.
Each rule has a test file, CWE and OWASP metadata, and a link to a page that
explains the vulnerability class and its fix.

[Semgrep](https://semgrep.dev) and its community registry already cover a lot
of Python. These rules sit next to them and add a few things we kept wanting:
FastAPI route parameters as sources, Django ORM field names and aliases (the
shape behind CVE-2024-42005 and CVE-2025-57833), MongoDB operator injection
from JSON bodies, and tar extraction without a filter.

## Quick start

```bash
pip install semgrep

# every rule, from one file
semgrep --config https://raw.githubusercontent.com/EyalSec/semgrep-rules/main/eyalsec-python.yaml .

# or from a clone
git clone https://github.com/EyalSec/semgrep-rules
semgrep --config semgrep-rules/python /path/to/your/app
```

In GitHub Actions:

```yaml
- run: pip install semgrep
- run: semgrep --error --config https://raw.githubusercontent.com/EyalSec/semgrep-rules/main/eyalsec-python.yaml .
```

## The rules

| Rule | Finds | CWE | Read more |
|---|---|---|---|
| `tainted-sql-query` | request data in the text of a SQL statement (`execute()`, `raw()`, `extra()`, `RawSQL`, SQLAlchemy `text()`, psycopg `sql.SQL`) | 89 | [SQL injection](https://eyalsec.com/vulnerabilities/sql-injection) |
| `django-tainted-orm-alias` | request data as a field name or alias in `values()`, `values_list()`, `order_by()`, or `**kwargs` to `annotate()` / `alias()` / `aggregate()` | 89 | [the two Django CVEs](https://eyalsec.com/research/django-column-alias-sql-injection-cve-2024-42005-cve-2025-57833) |
| `tainted-shell-command` | request data in a command a shell runs (`os.system`, `shell=True`, `os.popen`, paramiko `exec_command`) | 78 | [Command injection](https://eyalsec.com/vulnerabilities/command-injection) |
| `tainted-executable` | request data choosing which program runs | 78 | [Command injection](https://eyalsec.com/vulnerabilities/command-injection) |
| `tainted-subprocess-argument` | request data as a program argument with no `--` before it | 88 | [Command injection](https://eyalsec.com/vulnerabilities/command-injection) |
| `tainted-code-execution` | request data passed to `eval()`, `exec()` or `compile()` | 95 | [Code injection](https://eyalsec.com/vulnerabilities/code-injection) |
| `tainted-import-or-attribute` | request data choosing a module, a native library, or an attribute to read or set | 470 | [Code injection](https://eyalsec.com/vulnerabilities/code-injection) |
| `tainted-deserialization` | request data loaded with pickle, marshal, jsonpickle or YAML without a safe loader | 502 | [Insecure deserialization](https://eyalsec.com/vulnerabilities/insecure-deserialization) |
| `tainted-file-path` | request data deciding which file is opened, written or deleted | 22 | [Path traversal](https://eyalsec.com/vulnerabilities/path-traversal) |
| `tarfile-extractall-without-filter` | `extract()` / `extractall()` with no extraction filter | 22 | [Path traversal](https://eyalsec.com/vulnerabilities/path-traversal) |
| `tainted-outbound-url` | request data deciding where the server sends a request (requests, httpx, urllib, aiohttp) | 918 | [SSRF](https://eyalsec.com/vulnerabilities/ssrf) |
| `tainted-template-source` | request data used as a Jinja2, Django, Mako or Tornado template | 1336 | [Template injection](https://eyalsec.com/vulnerabilities/server-side-template-injection) |
| `tainted-mongodb-filter` | a JSON body value placed in a MongoDB filter without a type check | 943 | [NoSQL injection](https://eyalsec.com/vulnerabilities/nosql-injection) |
| `tainted-nosql-code` | request data in a MongoDB `$where` / `$function`, or a Redis `eval()` script | 943 | [NoSQL injection](https://eyalsec.com/vulnerabilities/nosql-injection) |
| `tainted-regex-pattern` | request data compiled as a regular expression | 1333 | [ReDoS](https://eyalsec.com/vulnerabilities/redos) |
| `random-for-secret-value` | the `random` module making a token, password, OTP or key | 338 | [Weak randomness](https://eyalsec.com/vulnerabilities/weak-randomness) |

**Sources** are request data in Flask (`flask.request`), Django and Django REST
framework (`request.GET`, `POST`, `body`, `data`, `COOKIES`, `META`, `FILES`,
URL arguments), Starlette and FastAPI (route parameters, `await
request.json()`, `query_params`). FastAPI dependencies (`Depends(...)`,
`Security(...)`) are not treated as input.

**What counts as handled:** converting to a number (`int()`, `float()`), a UUID,
looking the value up in a constant table (`ALLOWED[name]`,
`ALLOWED.get(name)`), checking membership (`if name not in ALLOWED: ...`), and
the escaping each rule names in its message (`shlex.quote()`, `re.escape()`,
`os.path.basename()`, `secure_filename()`, `is_relative_to()` and so on).

## What static rules can and cannot see

These rules read your source code. That makes them fast and cheap to run on
every pull request, and it also sets their limits, which are worth knowing
before you trust a clean result:

- **They follow data within one function.** Semgrep's open-source taint
  analysis does not follow a value from a view into a helper in another module,
  so a flow that crosses that boundary is not reported.
- **They see shapes, not behaviour.** A rule cannot tell that your own
  validation function makes a value safe, so some findings need a person to
  read them. The reverse also holds: code that looks parameterized can still be
  exploitable inside a library.
- **They cannot see inside your dependencies.** Both Django CVEs above were
  inside the framework. A scan of your repository sees a call to `values()`,
  which is fine; whether attacker-controlled data reaches the query Django
  builds is a question about the running program.

That last point is where runtime detection helps. es-python, the EyalSec
Python runtime, follows untrusted data through the program as it runs,
including through framework and library code, and checks it at the operation
itself, the moment the query or command is performed. Each event is a flow
that really happened, with where the data came in and which line used it. The
two approaches work well together: rules in CI catch the shape before it is
merged, and the runtime shows what actually reaches the operation in staging
or production. To see es-python on your own code,
[book a live demo](https://eyalsec.com/contact).

## Testing

Every rule has a test file next to it, with `# ruleid:` above each line that
must be reported and `# ok:` above each line that must not.

```bash
semgrep --test python/
python3 scripts/bundle.py --check   # eyalsec-python.yaml matches python/
```

CI runs both on every pull request.

## Contributing

Issues and pull requests are welcome, especially a false positive or a missed
flow from real code. A change to a rule comes with a test line that shows it.
After editing a rule, run `python3 scripts/bundle.py` to refresh the bundle.

Thanks to the Semgrep team for the engine and the registry these rules build
on, and to Django's security team for fixing both CVEs quickly.

## License

MIT. See [LICENSE](LICENSE).
