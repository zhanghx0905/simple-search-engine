from flask import Flask, request
from flask_cors import cross_origin

from index import load_index

APP = Flask(__name__)

INDEX = load_index()


@APP.route("/query")
@cross_origin()
def query():
    assert request.method == "GET"
    query: str = request.args.get("query", "")
    ret = INDEX.search(query)
    return ret
