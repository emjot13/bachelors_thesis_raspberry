from functools import wraps

def check_initialized(field_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            field_value = getattr(self, field_name, None)
            if field_value is not None:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator
