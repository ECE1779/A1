
from flask import Flask

webapp = Flask(__name__)
webapp.secret_key = "some secret key"

from app import ec2_examples
from app import s3_examples
from app import main
from app import login
from app import image

