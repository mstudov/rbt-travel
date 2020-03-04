from flask import Flask
from config import Config

from app.blueprints import auth, main, user, arrangement
from app.extensions import login_manager, migrate, db
from app.permissions import Role

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    register_shellcontext(app)
    return app

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    return None

def register_blueprints(app):
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(main.blueprint)
    app.register_blueprint(user.blueprint)
    app.register_blueprint(arrangement.blueprint)
    return None

def register_shellcontext(app):
    def shell_context():
        return { 'db': db }
        #return { 'db':db, 'User':User, 'TravelArrangement': TravelArrangement,
        #        'TravelArrangementTouristUser': TravelArrangementTouristUser,
        #        'AdminUser': AdminUser, 'TouristUser': TouristUser }
    def context_processor():
        return { 
            'TYPE_TOURIST':Role.TOURIST, 
            'TYPE_GUIDE':Role.GUIDE,
            'TYPE_ADMIN':Role.ADMIN }

    app.context_processor(context_processor)
    app.shell_context_processor(shell_context)
