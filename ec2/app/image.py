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
	f = request.files['new_file']
	if f.filename == '':
		abort(404)
	s3.Object("ece1779b",f.filename).put(Body=f)
	cnx = get_db()
	cursor = cnx.cursor()
	query = ''' INSERT INTO images (usersId,key1,key2,key3,key4) values (%s, %s, %s, %s, %s) '''
	cursor.execute(query, (id, f.filename, f.filename, f.filename, f.filename))
	cnx.commit()
	return redirect(url_for('user_ui', id=id))

@webapp.route("/view_img", methods=["GET"])
def view_img():
    cnx = get_db()

    cursor = cnx.cursor()

    query = """SELECT * FROM images WHERE usersId = %s"""

    row = cursor.fetchone()
    if row:
        return render_template("user_ui/view.html",title = "View images", cursor = cursor)

    return
