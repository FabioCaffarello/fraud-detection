from abc import ABC, abstractmethod
from typing import Any


class BaseFakeFactory(ABC):
    @abstractmethod
    def generate(self) -> dict[str, Any]:
        """
        Gera e retorna um dicionário contendo os dados fake para o domínio.
        """
        pass
