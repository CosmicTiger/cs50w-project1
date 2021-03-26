import os

class Config(object):
    # Check for environment variable
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is not set")

    DATABASE_URL = os.getenv("DATABASE_URL")

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_1sBO0ksR4t3'
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
