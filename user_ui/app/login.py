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
"""
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# silly user model
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username

        self.password = password

    def __repr__(self):
        return "%s/%s" % (self.username, self.password)

@webapp.route("/logout", methods=["GET"])
def user_logout():
    return
"""
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

    #do the login


    return redirect(url_for('welcome_page'))

@webapp.route("/welcome", methods=["GET"])
def welcome_page():
    return render_template("/welcome.html",title="Welcome")


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


