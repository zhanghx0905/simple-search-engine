from index import load_index
from flask import Flask, request

APP = Flask(__name__)

INDEX = load_index()


@APP.route("/query")
def query():
    assert request.method == "GET"
    query: str = request.args.get("query", "")
    ret = INDEX.search(query)
    return ret
