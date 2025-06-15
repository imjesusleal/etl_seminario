from pandas import read_csv
import os

from custom_errors.csv_exceptions import CsvNotFound

class CsvContext():
    def __init__(self, csv_path: str):
        self.__csv_path = csv_path
        self.__datos = self.__read_data()

    @property
    def datos(self):
        return self.__datos

    def __read_data(self):
        return read_csv(self.__csv_path)


try:
    ruta_relativa = os.path.join(os.path.dirname(__file__), '../../../datos_ventas.csv')
    csv_path = os.path.abspath(ruta_relativa)
except Exception as ex:
    raise CsvNotFound(f'No pude leer el path por esta razon: {ex}')


csv_ctx = CsvContext(csv_path)