"""Clase Cliente: datos personales encapsulados con validaciones estrictas."""

import re

from .entidades import EntidadBase
from .excepciones import ClienteInvalidoError, ParametroFaltanteError

_RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_RE_TELEFONO = re.compile(r"^\+?\d{7,15}$")
_RE_DOCUMENTO = re.compile(r"^\d{5,12}$")


class Cliente(EntidadBase):
    """Cliente de Software FJ. Los atributos son privados y se validan en los setters."""

    _familia = "cliente"

    def __init__(self, nombre=None, email=None, telefono=None, documento=None):
        # Parámetros faltantes -> excepción específica
        faltantes = [
            n
            for n, v in (
                ("nombre", nombre),
                ("email", email),
                ("telefono", telefono),
                ("documento", documento),
            )
            if v is None or (isinstance(v, str) and not v.strip())
        ]
        if faltantes:
            raise ParametroFaltanteError(
                f"Faltan parámetros del cliente: {', '.join(faltantes)}"
            )

        super().__init__()
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.documento = documento

    # ---- propiedades con validación (ENCAPSULACIÓN) ----
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe ser texto de al menos 3 caracteres")
        if any(ch.isdigit() for ch in valor):
            raise ClienteInvalidoError("El nombre no puede contener números")
        self.__nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not _RE_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Email inválido: {valor!r}")
        self.__email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = re.sub(r"[\s-]", "", str(valor))
        if not _RE_TELEFONO.match(limpio):
            raise ClienteInvalidoError(f"Teléfono inválido: {valor!r}")
        self.__telefono = limpio

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if not _RE_DOCUMENTO.match(str(valor)):
            raise ClienteInvalidoError(f"Documento inválido: {valor!r}")
        self.__documento = str(valor)

    def describir(self) -> str:
        # El documento se enmascara: dato personal sensible
        return (
            f"Cliente #{self.id}: {self.nombre} <{self.email}> "
            f"tel {self.telefono} doc ***{self.documento[-3:]}"
        )
