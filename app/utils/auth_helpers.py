from functools import wraps
from flask_login import current_user, login_required
from app.utils.errors import AuthenticationError, UnauthorizedError


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                raise AuthenticationError('Authentication required to access this resource.')
            if current_user.role != role:
                raise UnauthorizedError(f'Only {role.replace("_", " ")} users can access this page.')
            return fn(*args, **kwargs)
        return wrapper
    return decorator


admin_required = role_required('admin')
owner_required = role_required('salon_owner')
bride_required = role_required('bride')
