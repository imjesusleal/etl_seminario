class JsonNotFound(Exception):
    def __init__(self, mensaje = 'No consegui el json'):
        super().__init__(mensaje)