from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers


@app.route('/')
@app.route('/index')
def index():
    order = { 'total': '$1' }

    return render_template("index.html",
        order = order
    )