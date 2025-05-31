def singleton(cls):
    cls._instance = None

    def get_instance(*args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    cls.get_instance = staticmethod(get_instance)
    return cls
