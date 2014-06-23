A CRUD application to manage an ordering system
===============

Features:
-----------------

* All CRUD operations for Product Type using /productType
* All CRUD operations for Orders using /order
* All CRUD operations for line items using /order/<id>/lineItems
* Live Interactive API documenation using Swagger and the Flask_Sillwalk module (https://github.com/hobbeswalsh/flask-sillywalk)
* Inventory managemnt
* Real-time inventory management UI view using Faye. Monitor the effect all the API calls have on the current invenory
, and restock empty ProductTypes!
* Descriptive API error messsages to aid with usage
* Currency handling that mitigates floating point loss of percsion errors

1. INSTALL
-----------------
```pip install Flask
pip install SQLAlchemy
pip install flask-sqlalchemy
pip install requests
python flask-sillywalk/setup.py install
```

* copy flask-sillywalk/flask_sillywalk.py to the python path
* For example 
```cp flask-sillwalk/setup.py ../virtual_env/lib/python2.7/site-packages```

2. CREATE DATABASE
-----------------
```python db_create.py```


3. RUN UNIT TESTS
-----------------
```python test.py
python app/helpers.py```

4. RUN APPLICATION
-----------------
```python run.py```
* Then go to localhost:5000/
* The API docs at localhost:5000/docs

By default the app runs with a sqllite database. you can change it to mysql in config.py. 





My environment
-----------------
* My environment contained the following modules:

```Flask==0.10.1
Flask-SQLAlchemy==1.0
Flask-Swagger==1.0
Jinja2==2.7.3
MarkupSafe==0.23
SQLAlchemy==0.9.4
Werkzeug==0.9.6
itsdangerous==0.24
requests==2.3.0
wsgiref==0.1.2```





