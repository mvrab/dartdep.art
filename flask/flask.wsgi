import os, sys

# edit your username below
sys.path.append("/home/username/public_html/flask")

sys.path.insert(0, os.path.dirname(__file__))
from myapp import app as application

# make the secret code a little better
application.secret_key = 'somethingdifferentthanthis'