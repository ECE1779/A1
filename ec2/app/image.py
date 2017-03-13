from flask import render_template, redirect, url_for, request, session, g
from app import webapp
import mysql.connector
import boto3
from app.config import db_config
from wand.image import Image
import os

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


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route("/upload", methods=["GET"])
def upload_img():
    return render_template("image/new.html", title="New image")


@webapp.route('/upload', methods=['POST'])
def upload_img_save():
    f = request.files['new_file']
    if f.filename == '':
        return redirect(url_for("upload_img"))

    #get rotated images
    image_binary = f.read()

    f1_filename = "1_" + f.filename
    f1 = image_transform(image_binary, 0, f1_filename)

    f2_filename = "2_" + f.filename
    f2 = image_transform(image_binary, 90, f2_filename)


    f3_filename = "3_" + f.filename
    f3 = image_transform(image_binary, 180, f3_filename)


    f4_filename = "4_" + f.filename
    f4 = image_transform(image_binary, 270, f4_filename)


    #upload files to s3 bucket
    s3 = boto3.client("s3")
    #s3.upload_fileobj(f, "bucket-name", "key-name")
    #s4 = boto3.resource("s3")
    #s4.Object("bucketforprj1", f1_filename).put(Body=f)
    s3.upload_fileobj(f1, "bucketforprj1", f1_filename)
    s3.upload_fileobj(f2, "bucketforprj1", f2_filename)
    s3.upload_fileobj(f3, "bucketforprj1", f3_filename)
    s3.upload_fileobj(f4, "bucketforprj1", f4_filename)

    cnx = get_db()
    cursor = cnx.cursor()
    query = """SELECT * FROM users WHERE login = %s"""
    cursor.execute(query, (session["username"],))
    id = cursor.fetchone()[0]

    query = ''' INSERT INTO images (userId,key1,key2,key3,key4) values (%s, %s, %s, %s, %s) '''
    cursor.execute(query, (id, f1_filename, f2_filename, f3_filename, f4_filename))
    cnx.commit()
    return redirect(url_for('list_img'))


#Upload a new image and tranform it
def image_transform(image_binary, degree, fname):

    #image_binary = f.read()

    img = Image(blob=image_binary)
    i = img.clone()

    i.rotate(degree)
    i.format = "jpeg"
    i.save(filename=fname)

    newfile = open(fname, "rb")

    return newfile




@webapp.route("/list_img", methods=["GET"])
def list_img():
    cnx = get_db()

    cursor = cnx.cursor()
    query = """SELECT * FROM users WHERE login = %s"""
    cursor.execute(query, (session["username"],))
    id = cursor.fetchone()[0]

    query = """SELECT * FROM images WHERE userId = %s"""

    cursor.execute(query, (id,))

    #row = cursor.fetchone()
    #	http://s3.amazonaws.com/bucket/key  access an object
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')
    for obj in bucket.objects.all():
        print(obj.key)
    """
    count = cursor.rowcount
    if count > 0:
        return render_template("image/list.html", title = "List images", cursor = cursor)
    else:
        return render_template("image/list.html", title = "List images", info_msg = "you dont have any images")


@webapp.route("/view_img/<fname>", methods=["GET"])
def view_img(fname):
    cnx = get_db()

    cursor = cnx.cursor()
    query = """SELECT * FROM users WHERE login = %s"""
    cursor.execute(query, (session["username"],))
    id = cursor.fetchone()[0]


    query = """SELECT * FROM images where userId = %s AND key1 = %s"""

    cursor.execute(query, (id, fname))

    row = cursor.fetchone()

    if row:
        return render_template("image/view.html", title = "View images", f1 = row[2], f2 = row[3], f3 = row[4], f4 = row[5])
    else:
        return redirect(url_for("user_ui"), error_msg="image not found")




