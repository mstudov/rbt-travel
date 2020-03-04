from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps

class Role():
   TOURIST : int = 0
   GUIDE   : int = 1
   ADMIN   : int = 2

def requires_role(**options):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            roles = options.get('roles', None)
            if roles and current_user.user_role.role not in roles:
                flash('Permission denied.')
                return redirect(url_for('main.unauthorized'))
            return func(*args, **kwargs)
        return wrapped
    return wrapper
