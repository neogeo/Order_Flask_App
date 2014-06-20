import os
basedir = os.path.abspath(os.path.dirname(__file__))

#mysql table must already exist before running 'db_create.py'
SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/order'

#SQLLite
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')