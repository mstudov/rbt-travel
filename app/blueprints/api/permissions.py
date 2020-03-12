from flask import g
from functools import wraps

from app.blueprints.api.errors import error_response

class Role():
   TOURIST : int = 0
   GUIDE   : int = 1
   ADMIN   : int = 2

def requires_role(**options):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            roles = options.get('roles', None)
            if roles and g.current_user.user_role.role not in roles:
                return error_response(403)
            return func(*args, **kwargs)
        return wrapped
    return wrapper
