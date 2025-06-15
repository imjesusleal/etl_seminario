from abc import ABC, abstractmethod
from models.generic_model import T
from typing import Generic

class IGenericService(ABC, Generic[T]):

    @abstractmethod
    def get_all(self) -> list[T]:
        pass

    @abstractmethod
    def get_one_by_id(self, cliente_id: int) -> T:
        pass