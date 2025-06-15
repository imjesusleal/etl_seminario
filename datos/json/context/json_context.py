import json
import os

from custom_errors.json_exceptions import JsonNotFound

class JsonContext():
    def __init__(self, json_str: str):
        self.__json = json_str
        self.datos = self.__read_data()

    def __read_data(self):
        return json.loads(self.__json)


try:
    ruta_relativa = os.path.join(os.path.dirname(__file__), '../../../soporte_tecnico.json')
    json_path = os.path.abspath(ruta_relativa)
except Exception as ex:
    raise JsonNotFound(f'No pude leer el json por esta razon: {ex}')

with open(json_path, 'r', encoding='utf-8') as f:
    json_content = f.read()

json_ctx = JsonContext(json_content)