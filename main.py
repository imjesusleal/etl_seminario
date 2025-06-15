from custom_errors.csv_exceptions import CsvNotFound
from custom_errors.db_exceptions import DbNotFound
from custom_errors.excel_exceptions import ExcelNotFound
from custom_errors.json_exceptions import JsonNotFound
from servicios.excel_format.excel_format import ExcelFormat
from logger.logger_service import LoggerService
from servicios.main_service import main_service

def main():

    _logger = LoggerService('logs', 'etl.logs')

    try:

        main_service.cargar_datos()
        main_service.inyect()
        main_service.transform()
        main_service.manejar_datos()
        
        formatter = ExcelFormat('./output/output.xlsx')
        formatter.format()
    
    except (DbNotFound, JsonNotFound, CsvNotFound, ExcelNotFound) as e:
        _logger.error(e)
    

main()