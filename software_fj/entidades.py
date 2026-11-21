"""Clase abstracta base para todas las entidades del sistema (ABSTRACCIÓN)."""

from abc import ABC, abstractmethod
from itertools import count


class EntidadBase(ABC):
    """Entidad general: toda entidad tiene un id único y se sabe describir."""

    _familia = "entidad"  # cada familia (cliente, servicio, reserva) numera aparte
    _contadores: dict = {}

    def __init__(self) -> None:
        contador = EntidadBase._contadores.setdefault(self._familia, count(1))
        self._id = next(contador)  # encapsulado: solo lectura

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad concreta debe devolver su descripción textual."""

    def __str__(self) -> str:
        return self.describir()
