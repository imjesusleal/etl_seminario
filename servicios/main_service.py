from models.clientes_model import ClientesModel
from models.etl_model import ETLModelCommand, ETLModelDataframe
from models.inventario_model import InventarioModel
from models.tickets_model import TicketsModel
from models.ventas_model import VentasModel
from logger.logger_service import LoggerService
from servicios.json_services.json_services import json_service
from servicios.csv_services.csv_services import csv_service
from servicios.excel_services.excel_services import excel_service
from servicios.db_services.db_services import db_service
from servicios.export.powerbi_export import export_powerbi_csvs
from .etl_service import ETLService


class MainService():
    """Orquestador ETL NovaShop: Extract -> Transform -> Load."""

    def __init__(self, logger: LoggerService | None = None):
        self.datos_clientes: list[ClientesModel] = []
        self.datos_tickets: list[TicketsModel] = []
        self.datos_ventas: list[VentasModel] = []
        self.datos_inventario: list[InventarioModel] = []

        self.etl_service: ETLService | None = None
        self._logger = logger or LoggerService("logs", "etl.logs")

        self.__command: ETLModelCommand | None = None
        self.__dfs: ETLModelDataframe | None = None
        self.__cliente_resumen = None
        self.__calidad_reporte = None
        self.warehouse_path: str | None = None
        self.powerbi_export_path: str | None = None

    @property
    def dfs(self) -> ETLModelDataframe:
        return self.__dfs

    @property
    def cliente_resumen(self):
        return self.__cliente_resumen

    @property
    def calidad_reporte(self):
        return self.__calidad_reporte

    def run(self) -> str:
        """Ejecuta el pipeline completo E -> T -> L (full refresh)."""
        self._logger.info("=== INICIO ETL NovaShop (full refresh) ===")
        self.extract()
        self.transform()
        db_path = self.load()
        self._logger.info("=== FIN ETL NovaShop ===")
        return db_path

    def extract(self) -> None:
        """EXTRACT: lee fuentes originales heterogenas."""
        self._logger.info("[E] Extract - inicio")
        self.datos_clientes = db_service.get_all()
        self.datos_tickets = json_service.get_all()
        self.datos_ventas = csv_service.get_all()
        self.datos_inventario = excel_service.get_all()

        self._logger.info(
            "[E] Extract - ok | "
            f"clientes={len(self.datos_clientes)} "
            f"ventas={len(self.datos_ventas)} "
            f"tickets={len(self.datos_tickets)} "
            f"inventario={len(self.datos_inventario)}"
        )

        self.__command = ETLModelCommand(
            self.datos_clientes,
            self.datos_tickets,
            self.datos_ventas,
            self.datos_inventario,
        )
        self.etl_service = ETLService(self.__command)

    def transform(self) -> None:
        """TRANSFORM: normalizacion, limpieza, calidad y tablas analiticas."""
        if self.etl_service is None:
            raise RuntimeError("Debes ejecutar extract() antes de transform()")

        self._logger.info("[T] Transform - inicio")
        self.__dfs = self.etl_service.transform()

        pasos = [
            ("normalizar", lambda: self.etl_service.normalizar(self.__dfs)),
            ("limpiar", lambda: self.etl_service.limpiar(self.__dfs)),
            ("format_handling", lambda: self.etl_service.format_handling(self.__dfs)),
            ("estandarizar_categorias", lambda: self.etl_service.estandarizar_categorias(self.__dfs)),
            ("handle_null", lambda: self.etl_service.handle_null(self.__dfs)),
            ("crear_columna_calculada", lambda: self.etl_service.crear_columna_calculada(self.__dfs.ventas)),
            ("marcar_integridad_referencial", lambda: self.etl_service.marcar_integridad_referencial(self.__dfs)),
            ("detectar_outliers", lambda: self.etl_service.detectar_outliers(self.__dfs)),
            ("ordenar", lambda: self.etl_service.ordenar(self.__dfs)),
        ]

        for nombre, fn in pasos:
            fn()
            self._logger.info(f"[T] paso ok: {nombre}")

        self.__cliente_resumen = self.etl_service.crear_cliente_resumen(self.__dfs)
        self.__calidad_reporte = self.etl_service.generar_reporte_calidad()

        self._logger.info(
            "[T] Transform - ok | "
            f"clientes={len(self.__dfs.clientes)} "
            f"ventas={len(self.__dfs.ventas)} "
            f"tickets={len(self.__dfs.tickets)} "
            f"inventario={len(self.__dfs.inventario)} "
            f"cliente_resumen={len(self.__cliente_resumen)} "
            f"hallazgos_calidad={len(self.__calidad_reporte)}"
        )

    def load(self) -> str:
        """LOAD: persiste warehouse SQLite + Excel para visualizacion (idempotente)."""
        if self.etl_service is None or self.__dfs is None:
            raise RuntimeError("Debes ejecutar extract() y transform() antes de load()")

        self._logger.info("[L] Load - inicio (recrea schema analitico)")
        self.warehouse_path = self.etl_service.load_warehouse(
            self.__dfs,
            self.__cliente_resumen,
            self.__calidad_reporte,
        )
        self.etl_service.output(
            self.__dfs,
            self.__cliente_resumen,
            self.__calidad_reporte,
        )
        powerbi_dir = export_powerbi_csvs(self.warehouse_path)
        self.powerbi_export_path = str(powerbi_dir)
        self._logger.info(
            "[L] Load - ok | "
            f"sqlite={self.warehouse_path} | "
            "excel=output/output.xlsx | "
            "calidad=output/calidad_reporte.csv | "
            f"powerbi={self.powerbi_export_path}"
        )
        return self.warehouse_path

    # Compatibilidad con llamadas previas
    def cargar_datos(self) -> None:
        self.extract()

    def inyect(self) -> None:
        # La inyeccion queda dentro de extract()
        if self.etl_service is None:
            self.extract()

    def manejar_datos(self) -> None:
        self.transform()
        self.load()


main_service = MainService()
