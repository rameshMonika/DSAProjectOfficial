from flask import Blueprint, jsonify
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from web.calc import get_route

from .auth import login_required
from ..db import get_db

bp = Blueprint("root", __name__, url_prefix="/")

@bp.get('/')
def index():
    return render_template("root/index.html")

@bp.get('/search')
def search():
    origin = request.args.get('origin')
    dest = request.args.get('dest')

    flights = get_route(origin, dest)

    return render_template("root/search.html", origin=origin, dest=dest, flights=flights)
