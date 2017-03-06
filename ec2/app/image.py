from flask import render_template, redirect, url_for, request, session
from app import webapp
import mysql.connector

from app.config import db_config

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.route("/upload", methods=["GET"])
def upload_img():
    return render_template("image/new.html", title="New image")


@webapp.route('/upload', methods=['POST'])
def upload_img_save():
    return

@webapp.route("/view_img", methods=["GET"])
def view_img():
    return