class DbNotFound(Exception):
    def __init__(self, mensaje = 'No consegui la base de datos'):
        super().__init__(mensaje)