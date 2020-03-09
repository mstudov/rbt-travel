import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'random-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
                                    os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESULTS_PER_PAGE = 5
