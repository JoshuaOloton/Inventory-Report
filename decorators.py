from functools import wraps
from flask import redirect, request, url_for, session, flash


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'id' not in session:
            flash("You need to login first",'danger')
            return redirect(url_for('user.login', next = request.url))
        return f(*args, **kwargs)            
        
    return wrap