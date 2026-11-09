from custom_errors.csv_exceptions import CsvNotFound
from custom_errors.db_exceptions import DbNotFound
from custom_errors.excel_exceptions import ExcelNotFound
from custom_errors.json_exceptions import JsonNotFound
from servicios.excel_format.excel_format import ExcelFormat
from logger.logger_service import LoggerService
from servicios.main_service import MainService


def main():
    logger = LoggerService("logs", "etl.logs")
    etl = MainService(logger)

    try:
        # Pipeline explicito: Extract -> Transform -> Load
        warehouse_path = etl.run()

        formatter = ExcelFormat("./output/output.xlsx")
        formatter.format()

        logger.info(f"Warehouse SQLite: {warehouse_path}")
        logger.info("Excel analitico: output/output.xlsx")
        logger.info("Reporte calidad: output/calidad_reporte.csv")
        if etl.powerbi_export_path:
            logger.info(f"CSVs Power BI: {etl.powerbi_export_path}")

        if etl.calidad_reporte is not None and not etl.calidad_reporte.empty:
            print("\n--- Resumen calidad ---")
            print(etl.calidad_reporte[["hallazgo", "severidad", "metrica", "valor_despues"]].to_string(index=False))

    except (DbNotFound, JsonNotFound, CsvNotFound, ExcelNotFound) as e:
        logger.error(e)
    except Exception as e:
        logger.exception(f"Error no controlado en ETL: {e}")
        raise


if __name__ == "__main__":
    main()
