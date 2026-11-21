"""Servicio abstracto y tres servicios especializados (HERENCIA + POLIMORFISMO)."""

import math
from abc import ABC, abstractmethod

from .entidades import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)


class Servicio(EntidadBase, ABC):
    """Clase abstracta: define el contrato común de todos los servicios."""

    IVA = 0.19  # impuesto por defecto
    _familia = "servicio"

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()
        self.nombre = nombre
        self.tarifa_hora = tarifa_hora
        self.disponible = disponible

    # ---- encapsulación ----
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ServicioInvalidoError("El nombre del servicio no puede estar vacío")
        self._nombre = valor.strip()

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @tarifa_hora.setter
    def tarifa_hora(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
            raise ServicioInvalidoError(f"Tarifa por hora inválida: {valor!r}")
        self._tarifa_hora = float(valor)

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise ServicioInvalidoError("'disponible' debe ser booleano")
        self._disponible = valor

    # ---- métodos abstractos (cada servicio los SOBRESCRIBE) ----
    @abstractmethod
    def calcular_costo_base(self, horas: float, **extras) -> float:
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, **extras) -> None:
        """Valida los parámetros propios del servicio; lanza ServicioInvalidoError."""

    @abstractmethod
    def describir(self) -> str:
        ...

    # ---- SOBRECARGA de cálculo de costos ----
    # Python no tiene sobrecarga por firma; se simula con parámetros opcionales
    # y con variantes nombradas que delegan en el método principal.
    def calcular_costo(self, horas, impuesto=None, descuento=0.0, **extras) -> float:
        """Variante general: calcular_costo(h) / (h, impuesto) / (h, impuesto, descuento)."""
        if isinstance(horas, bool) or not isinstance(horas, (int, float)) or horas <= 0:
            raise ServicioInvalidoError(f"Duración inválida: {horas!r}")
        impuesto = self.IVA if impuesto is None else impuesto
        if not 0 <= impuesto <= 1:
            raise ServicioInvalidoError(f"Impuesto fuera de rango: {impuesto!r}")
        if not 0 <= descuento <= 1:
            raise ServicioInvalidoError(f"Descuento fuera de rango: {descuento!r}")

        try:
            base = self.calcular_costo_base(horas, **extras)
            total = base * (1 - descuento) * (1 + impuesto)
        except ServicioInvalidoError:
            raise
        except Exception as e:  # cualquier fallo interno -> excepción encadenada
            raise CalculoInconsistenteError(
                f"Fallo calculando el costo de '{self.nombre}'"
            ) from e

        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"Costo inconsistente: {total!r}")
        return round(total, 2)

    def calcular_costo_con_impuesto(self, horas, impuesto, **extras) -> float:
        """Variante: solo impuesto personalizado."""
        return self.calcular_costo(horas, impuesto=impuesto, **extras)

    def calcular_costo_con_descuento(self, horas, descuento, **extras) -> float:
        """Variante: solo descuento (con IVA por defecto)."""
        return self.calcular_costo(horas, descuento=descuento, **extras)


class ReservaSala(Servicio):
    """Reserva de salas de reuniones."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, asistentes=None, **extras) -> None:
        if asistentes is None:
            raise ParametroFaltanteError("Falta el parámetro 'asistentes'")
        if not isinstance(asistentes, int) or asistentes <= 0:
            raise ServicioInvalidoError(f"Número de asistentes inválido: {asistentes!r}")
        if asistentes > self._capacidad:
            raise ServicioInvalidoError(
                f"{asistentes} asistentes exceden la capacidad ({self._capacidad})"
            )

    def calcular_costo_base(self, horas, proyector=False, **extras) -> float:
        recargo = 15_000 * horas if proyector else 0  # recargo por proyector
        return self.tarifa_hora * horas + recargo

    def describir(self) -> str:
        return (
            f"Sala '{self.nombre}' (cap. {self.capacidad}) - "
            f"${self.tarifa_hora:,.0f}/h - {'disponible' if self.disponible else 'NO disponible'}"
        )


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos."""

    def __init__(self, nombre, tarifa_hora, deposito, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if isinstance(deposito, bool) or not isinstance(deposito, (int, float)) or deposito < 0:
            raise ServicioInvalidoError(f"Depósito inválido: {deposito!r}")
        self._deposito = float(deposito)

    @property
    def deposito(self) -> float:
        return self._deposito

    def validar_parametros(self, cantidad=None, **extras) -> None:
        if cantidad is None:
            raise ParametroFaltanteError("Falta el parámetro 'cantidad'")
        if not isinstance(cantidad, int) or not 1 <= cantidad <= 10:
            raise ServicioInvalidoError(f"Cantidad inválida (1-10): {cantidad!r}")

    def calcular_costo_base(self, horas, cantidad=1, seguro=False, **extras) -> float:
        subtotal = self.tarifa_hora * horas * cantidad
        if seguro:
            subtotal *= 1.05  # seguro 5 %
        return subtotal + self._deposito * cantidad

    def describir(self) -> str:
        return (
            f"Equipo '{self.nombre}' - ${self.tarifa_hora:,.0f}/h, "
            f"depósito ${self.deposito:,.0f} - "
            f"{'disponible' if self.disponible else 'NO disponible'}"
        )


class AsesoriaEspecializada(Servicio):
    """Asesoría con un especialista; la tarifa varía según el nivel."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad no puede estar vacía")
        self._especialidad = especialidad.strip()

    @property
    def especialidad(self) -> str:
        return self._especialidad

    def validar_parametros(self, nivel=None, **extras) -> None:
        if nivel is None:
            raise ParametroFaltanteError("Falta el parámetro 'nivel'")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' inválido; opciones: {', '.join(self.NIVELES)}"
            )

    def calcular_costo_base(self, horas, nivel="junior", **extras) -> float:
        return self.tarifa_hora * horas * self.NIVELES[nivel]  # KeyError si nivel malo

    def describir(self) -> str:
        return (
            f"Asesoría '{self.nombre}' en {self.especialidad} - "
            f"${self.tarifa_hora:,.0f}/h base - "
            f"{'disponible' if self.disponible else 'NO disponible'}"
        )
