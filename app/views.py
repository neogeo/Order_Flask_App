from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    order = { 'total': '$1' }

    return render_template("index.html",
        order = order
    )