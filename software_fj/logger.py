"""Configuración del registro de eventos y errores.

Es el ÚNICO uso de archivos del sistema: no hay base de datos ni persistencia
de entidades. Todo se escribe en logs/software_fj.log.
"""

import logging
from pathlib import Path

RUTA_LOG = Path("logs") / "software_fj.log"


def obtener_logger(nombre: str = "software_fj") -> logging.Logger:
    """Devuelve un logger con salida a archivo (idempotente)."""
    logger = logging.getLogger(nombre)
    if logger.handlers:  # ya configurado: evita duplicar líneas
        return logger

    logger.setLevel(logging.DEBUG)
    try:
        RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
        manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    except OSError:
        # Si no se puede escribir el archivo, el sistema sigue vivo
        # usando la consola para no perder los mensajes.
        manejador = logging.StreamHandler()

    manejador.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    )
    logger.addHandler(manejador)
    return logger


log = obtener_logger()
