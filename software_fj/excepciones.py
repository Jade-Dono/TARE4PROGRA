"""Excepciones personalizadas de Software FJ.

Todas heredan de ErrorSoftwareFJ para poder capturarlas de forma genérica
(`except ErrorSoftwareFJ`) o de forma específica según el caso.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de todo el sistema."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Falta un parámetro obligatorio."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Datos de cliente inválidos (nombre, email, teléfono, documento...)."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Datos o parámetros de servicio inválidos."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio solicitado no está disponible."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """La reserva no se pudo crear o procesar."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Operación incompatible con el estado actual (ej. cancelar una cancelada)."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """El cálculo de costos produjo un resultado imposible o falló."""
