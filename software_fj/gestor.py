"""Gestor central: listas internas + captura de errores para que nada detenga el sistema."""

from functools import singledispatchmethod

from .cliente import Cliente
from .excepciones import ClienteInvalidoError, ErrorSoftwareFJ, ServicioInvalidoError
from .logger import log
from .reserva import Reserva
from .servicios import Servicio


class GestorFJ:
    def __init__(self):
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    # Copias de solo lectura (encapsulación de las listas internas)
    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    # ---------------------------------------------------------- utilidad común
    def _ejecutar(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación; ante CUALQUIER error lo registra y devuelve None."""
        try:
            return funcion(*args, **kwargs)
        except ErrorSoftwareFJ as e:
            causa = f" | causa: {e.__cause__!r}" if e.__cause__ else ""
            log.error("%s -> %s: %s%s", descripcion, type(e).__name__, e, causa)
            print(f"  [ERROR controlado] {descripcion}: {e}")
        except Exception as e:  # error no previsto: el sistema sigue activo
            log.exception("%s -> ERROR INESPERADO %s", descripcion, type(e).__name__)
            print(f"  [ERROR inesperado controlado] {descripcion}: {type(e).__name__}: {e}")
        return None

    # ---------------------------------------------------------------- registro
    def registrar_cliente(self, **datos):
        def _crear():
            cliente = Cliente(**datos)
            if any(c.documento == cliente.documento for c in self._clientes):
                raise ClienteInvalidoError(f"Documento duplicado: {cliente.documento}")
            self._clientes.append(cliente)
            log.info("Cliente registrado: %s", cliente.describir())
            return cliente

        return self._ejecutar("Registrar cliente", _crear)

    def registrar_servicio(self, clase, **datos):
        def _crear():
            try:
                servicio = clase(**datos)
            except TypeError as e:
                # Argumentos faltantes/sobrantes o clase abstracta -> error propio encadenado
                raise ServicioInvalidoError(
                    f"No se pudo crear el servicio: {e}"
                ) from e
            self._servicios.append(servicio)
            log.info("Servicio registrado: %s", servicio.describir())
            return servicio

        return self._ejecutar(f"Registrar servicio {getattr(clase, '__name__', clase)}", _crear)

    def crear_reserva(self, cliente, servicio, duracion, descuento=0.0, **parametros):
        """Crea y procesa una reserva; devuelve la Reserva o None si falló."""

        def _crear():
            reserva = Reserva(cliente, servicio, duracion, **parametros)
            self._reservas.append(reserva)  # se conserva también si falla el procesamiento
            print("  " + reserva.procesar(descuento))
            return reserva

        return self._ejecutar("Crear reserva", _crear)

    def cancelar_reserva(self, reserva):
        return self._ejecutar("Cancelar reserva", reserva.cancelar)

    # -------------------------------------------- búsqueda (despacho por tipo)
    @singledispatchmethod
    def buscar_cliente(self, clave):
        raise TypeError(f"Tipo de búsqueda no soportado: {type(clave).__name__}")

    @buscar_cliente.register
    def _(self, clave: int):  # por id
        return next((c for c in self._clientes if c.id == clave), None)

    @buscar_cliente.register
    def _(self, clave: str):  # por documento
        return next((c for c in self._clientes if c.documento == clave), None)

    # ------------------------------------------------------------------ resumen
    def resumen(self) -> str:
        confirmadas = [r for r in self._reservas if r.estado.value == "confirmada"]
        ingresos = sum(r.costo for r in confirmadas)
        return (
            f"Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)} | "
            f"Reservas: {len(self._reservas)} (confirmadas: {len(confirmadas)}) | "
            f"Ingresos: ${ingresos:,.2f}"
        )
