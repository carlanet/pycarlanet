import functools
import threading
from copy import deepcopy


def closure(f):
    def closure_aux(item, *args):
        prec = None
        while item != prec:
            prec = deepcopy(item)
            item = f(item, *args)
        return item

    return closure_aux


def preconditions(*members, msg_to_print=None, valid=lambda *params: all(p is not None for p in params)):
    def wrapper_method(method):
        def validation(ref, *args, **kwargs):
            if not valid(*(getattr(ref, member) for member in members)):
                msg = msg_to_print if msg_to_print else f"Violated prerequisites of method {method.__name__}"
                raise Exception(msg)
            return method(ref, *args, **kwargs)

        return validation

    return wrapper_method


def synchronized(lock: threading.RLock):
    def _decorator(wrapped):
        @functools.wraps(wrapped)
        def _wrapper(*args, **kwargs):
            with lock:
                return wrapped(*args, **kwargs)

        return _wrapper

    return _decorator


class MetaClassSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in MetaClassSingleton._instances:
            MetaClassSingleton._instances[cls] = super().__call__(*args, **kwargs)
        return MetaClassSingleton._instances[cls]


class DecoratorSingleton:
    def __init__(self, decorated_type):
        self._decorated_type = decorated_type
        self._instance = None

    @property
    @preconditions("_instance")
    def instance(self):
        return self._instance

    def __call__(self, *args, **kwargs):
        if self._instance is not None: raise TypeError(
            'You already had instantiate this object, please call instance() method to retrieve')
        self._instance = self._decorated_type(*args, **kwargs)
        return self._instance

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated_type)

    def destroy(self):
        del self._instance
        self._instance = None
