import pickle
import os

def cache_name(name):
    return name + '.pickle'

def cache_load(name):
    fn = cache_name(name)
    if os.path.exists(fn):
        with open(fn, 'rb') as f:
            return pickle.load(f)
    return None

def cache_dump(name, data):
    fn = cache_name(name)
    with open(fn, 'wb') as f:
        pickle.dump(data, f)
    return data

def cached(func):
    def wrapper(*args, **kwargs):
        if c := cache_load(func.__name__):
            return c
        return cache_dump(func.__name__, func(*args, **kwargs))
    return wrapper


def truncate_title(ftitle):
    try:
      return ftitle.encode()[:99].decode()
    except UnicodeDecodeError as err:
      return ftitle.encode()[:err.start].decode()
    raise RuntimeError("unexpected error truncating title")
