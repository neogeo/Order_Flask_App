from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers



@app.route('/')
@app.route('/inventory')
def inventory():
    return render_template("inventory.html")

@app.route('/docs')
def swagger():
    return render_template("swagger.html")