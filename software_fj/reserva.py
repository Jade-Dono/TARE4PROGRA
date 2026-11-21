"""Clase Reserva: integra cliente, servicio, duración y estado."""

from enum import Enum

from .cliente import Cliente
from .entidades import EntidadBase
from .excepciones import (
    CalculoInconsistenteError,
    ErrorSoftwareFJ,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)
from .logger import log
from .servicios import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    FALLIDA = "fallida"


class Reserva(EntidadBase):
    _familia = "reserva"

    def __init__(self, cliente, servicio, duracion_horas, **parametros):
        # Validaciones estrictas de construcción
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        if (
            isinstance(duracion_horas, bool)
            or not isinstance(duracion_horas, (int, float))
            or not 0 < duracion_horas <= 12
        ):
            raise ReservaInvalidaError(
                f"Duración inválida (0-12 h): {duracion_horas!r}"
            )

        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_horas
        self._parametros = parametros  # extras propios de cada servicio
        self._estado = EstadoReserva.PENDIENTE
        self._costo = None

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo(self):
        return self._costo

    # ---------------------------------------------------------------- confirmar
    def confirmar(self, descuento: float = 0.0) -> float:
        """Confirma la reserva. try / except / else / finally + encadenamiento."""
        # Operación no permitida: se rechaza SIN cambiar el estado actual
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"Reserva #{self.id} en estado '{self._estado.value}': no se puede confirmar"
            )

        try:
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self._servicio.nombre}' no está disponible"
                )
            self._servicio.validar_parametros(**self._parametros)
            costo = self._servicio.calcular_costo(
                self._duracion, descuento=descuento, **self._parametros
            )
        except ErrorSoftwareFJ as e:
            self._estado = EstadoReserva.FALLIDA
            # Encadenamiento: la causa original queda en __cause__
            raise ReservaInvalidaError(
                f"No se pudo confirmar la reserva #{self.id}: {e}"
            ) from e
        except Exception as e:  # error inesperado (bug, tipo incorrecto...)
            self._estado = EstadoReserva.FALLIDA
            raise CalculoInconsistenteError(
                f"Error inesperado confirmando la reserva #{self.id}"
            ) from e
        else:
            # Solo se ejecuta si el try terminó sin errores
            self._costo = costo
            self._estado = EstadoReserva.CONFIRMADA
            log.info(
                "Reserva #%s CONFIRMADA | cliente=%s | servicio=%s | %sh | total=%s",
                self.id, self._cliente.nombre, self._servicio.nombre, self._duracion, costo,
            )
            return costo
        finally:
            # Siempre se ejecuta: deja traza del intento
            log.debug("Intento de confirmación reserva #%s -> %s", self.id, self._estado.value)

    # ----------------------------------------------------------------- cancelar
    def cancelar(self) -> None:
        if self._estado is EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(f"La reserva #{self.id} ya estaba cancelada")
        if self._estado is EstadoReserva.FALLIDA:
            raise OperacionNoPermitidaError(
                f"La reserva #{self.id} falló; no hay nada que cancelar"
            )
        self._estado = EstadoReserva.CANCELADA
        self._costo = None
        log.info("Reserva #%s CANCELADA", self.id)

    # ---------------------------------------------------------------- procesar
    def procesar(self, descuento: float = 0.0) -> str:
        """Flujo completo: confirmar y devolver un resumen."""
        try:
            costo = self.confirmar(descuento)
        except ErrorSoftwareFJ as e:
            log.error("Procesamiento fallido reserva #%s: %s", self.id, e)
            raise
        return f"Reserva #{self.id} confirmada: {self._servicio.nombre} x {self._duracion}h = ${costo:,.2f}"

    def describir(self) -> str:
        costo = f"${self._costo:,.2f}" if self._costo is not None else "sin calcular"
        return (
            f"Reserva #{self.id} [{self._estado.value}] {self._cliente.nombre} -> "
            f"{self._servicio.nombre} ({self._duracion}h) {costo}"
        )
