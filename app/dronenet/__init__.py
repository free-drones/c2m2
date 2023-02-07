import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# python3 -c 'import secrets; print(secrets.token_hex())'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'f930db42f87494ae191473dbae94e6429af44738fe1d0063d03fda9706d2eb40'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///remotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from dronenet import routes
