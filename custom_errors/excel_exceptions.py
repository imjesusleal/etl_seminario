class ExcelNotFound(Exception):
    def __init__(self, mensaje = 'No consegui el excel'):
        super().__init__(mensaje)