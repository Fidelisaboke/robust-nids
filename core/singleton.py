"""
Singleton module.
Contains a singleton metaclass.
"""

import threading


class SingletonMeta(type):
    """
    Singleton metaclass.
    Follows the double-checked locking pattern.
    To be inherited by classes that instantiate a singleton instance.
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                # double check inside lock
                if cls not in cls._instances:
                    cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
