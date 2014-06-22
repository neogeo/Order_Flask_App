from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
#get flask_sillywak here https://github.com/hobbeswalsh/flask-sillywalk
from flask_sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#for swagger documentation
registry = SwaggerApiRegistry(
  app,
  baseurl="http://localhost:5000",
  api_version="1.0",
  api_descriptions={"orders": "CRUD operations for an order Flask App"})
register = registry.register
registerModel = registry.registerModel

from app import views, models, helpers, order_api, product_type_api, order_line_items_api

