from pandas import read_excel
import os

from custom_errors.excel_exceptions import ExcelNotFound

class ExcelContext():
    def __init__(self, csv_path: str):
        self.__csv_path = csv_path
        self.__datos = self.__read_data()

    @property
    def datos(self):
        return self.__datos

    def __read_data(self):
        return read_excel(self.__csv_path)


try:
    ruta_relativa = os.path.join(os.path.dirname(__file__), '../../../inventario.xlsx')
    excel_path = os.path.abspath(ruta_relativa)
except Exception as ex:
    raise ExcelNotFound(f'No pude leer el path por esta razon: {ex}')


excel_ctx = ExcelContext(excel_path)