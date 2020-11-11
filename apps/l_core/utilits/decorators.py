from functools import wraps

def print_fn_name(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        if hasattr(func, 'name'):
            f = func
        elif hasattr(func, '__func__'):
            f = func.__func__

        print('START :',f.__name__)
        res =  func(*args, **kwargs)
        print('END :', f.__name__)
        return res

    return tmp
