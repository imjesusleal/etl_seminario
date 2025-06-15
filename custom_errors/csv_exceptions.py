class CsvNotFound(Exception):
    def __init__(self, mensaje = 'No consegui el csv'):
        super().__init__(mensaje)