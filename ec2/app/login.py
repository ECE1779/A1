from flask import render_template, redirect, url_for, request, session, g
from app import webapp

import mysql.connector
import boto3

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


@webapp.route("/", methods=["POST"])
def user_login():
    username = request.form.get("username","")
    password = request.form.get("password","")

    cnx = get_db()

    cursor = cnx.cursor()

    query = """SELECT *
               FROM users
               WHERE login = %s AND password = %s
            """
    cursor.execute(query, (username, password))

    row = cursor.fetchone()
    if row is None:
        return render_template("/main.html", error_msg="User does not exist!",
                               username = username)
    id = row[0]
    username = row[1]
    password = row[2]

    session["username"] = username
    #flash("User %s login successfully" % username)

    if username == "admin":
        return redirect(url_for("manager_ui"))
    else:
        return redirect(url_for('user_ui'))


@webapp.route("/logout", methods=["GET"])
def user_logout():
    session.clear()
    return render_template("/main.html", error_msg="You are logged out")


@webapp.route("/user_ui", methods=["GET"])
def user_ui():
    return render_template("/user_ui.html",title="Welcome")


@webapp.route("/manager_ui", methods=["GET"])
def manager_ui():
    return render_template("/manager_ui.html", title = "Welcome")


@webapp.route("/register", methods=["GET"])
def user_create():
    return render_template("user/new.html", title="New User")


@webapp.route('/register', methods=['POST'])
# Create a new student and save them in the database.
def user_create_save():
    username = request.form.get("username","")
    password = request.form.get("password","")
    error = False

    if username == "" or password == "" :
        error = True
        error_msg = "Error: All fields are required!"


    if error:
        return render_template("user/new.html", title="New User", error_msg=error_msg,
                               username=username, password = password)

    cnx = get_db()
    cursor = cnx.cursor()
    query = """SELECT *
               FROM users
               WHERE login = %s AND password = %s
            """

    cursor.execute(query, (username, password))

    row = cursor.fetchone()
    if row:
        error_msg = "Error: user already exist"
        return render_template("user/new.html", title="New User", error_msg=error_msg,
                               username=username, password = password)

    query = ''' INSERT INTO users (login, password)
                       VALUES (%s,%s)
    '''

    cursor.execute(query, (username, password))
    cnx.commit()

    return redirect(url_for('user_login'))


