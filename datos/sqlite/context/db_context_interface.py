from abc import ABC, abstractmethod
from sqlite3 import Connection

class IDbContext(ABC):

    @abstractmethod
    def _create_conn(self) -> Connection:
        pass

    def execute(self, query: str) -> None:
        pass

    def fetch_one(self):
        pass

    def fetch_all(self):
        pass
    
    def close(self):
        pass
    