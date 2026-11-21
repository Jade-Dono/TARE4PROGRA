"""Software FJ - aplicación interactiva.

El usuario registra clientes, servicios y reservas desde un menú.
Cualquier error se captura, se registra en logs/software_fj.log y el
programa sigue funcionando.
"""

from software_fj.gestor import GestorFJ
from software_fj.logger import log
from software_fj.servicios import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ReservaSala,
)


# ------------------------------------------------------------- entradas seguras
def pedir_texto(mensaje):
    """Devuelve el texto escrito o None si queda vacío (el sistema valida después)."""
    valor = input(f"{mensaje}: ").strip()
    return valor or None


def pedir_numero(mensaje, tipo=float):
    """Convierte la entrada a número; si no es válida devuelve el texto tal cual
    para que las validaciones del sistema lo rechacen y lo registren en el log."""
    valor = input(f"{mensaje}: ").strip()
    if not valor:
        return None
    try:
        return tipo(valor)
    except ValueError:
        log.error("Entrada numérica inválida para '%s': %r", mensaje, valor)
        return valor


def pedir_si_no(mensaje):
    return input(f"{mensaje} (s/n): ").strip().lower() == "s"


def elegir(lista, etiqueta):
    """Muestra una lista numerada por id y devuelve el elemento elegido (o None)."""
    if not lista:
        print(f"  No hay {etiqueta} registrados todavía.")
        return None
    for e in lista:
        print("  ", e)
    try:
        ident = int(input(f"Id del {etiqueta}: ").strip())
    except ValueError:
        print("  Id inválido.")
        log.error("Id inválido al elegir %s", etiqueta)
        return None
    elegido = next((e for e in lista if e.id == ident), None)
    if elegido is None:
        print(f"  No existe un {etiqueta} con id {ident}.")
        log.error("No existe %s con id %s", etiqueta, ident)
    return elegido


# ------------------------------------------------------------------- acciones
def registrar_cliente(fj):
    print("\n-- Registrar cliente --")
    cliente = fj.registrar_cliente(
        nombre=pedir_texto("Nombre"),
        email=pedir_texto("Email"),
        telefono=pedir_texto("Teléfono"),
        documento=pedir_texto("Documento (5-12 dígitos)"),
    )
    if cliente:
        print("  Registrado:", cliente)


def registrar_servicio(fj):
    print("\n-- Registrar servicio --")
    print("  1) Reserva de sala\n  2) Alquiler de equipo\n  3) Asesoría especializada")
    opcion = input("Tipo: ").strip()
    nombre = pedir_texto("Nombre del servicio")
    tarifa = pedir_numero("Tarifa por hora")

    if opcion == "1":
        servicio = fj.registrar_servicio(
            ReservaSala, nombre=nombre, tarifa_hora=tarifa,
            capacidad=pedir_numero("Capacidad (personas)", int),
        )
    elif opcion == "2":
        servicio = fj.registrar_servicio(
            AlquilerEquipo, nombre=nombre, tarifa_hora=tarifa,
            deposito=pedir_numero("Depósito por unidad", float),
        )
    elif opcion == "3":
        servicio = fj.registrar_servicio(
            AsesoriaEspecializada, nombre=nombre, tarifa_hora=tarifa,
            especialidad=pedir_texto("Especialidad"),
        )
    else:
        print("  Opción de tipo no válida.")
        log.error("Tipo de servicio no válido: %r", opcion)
        return
    if servicio:
        print("  Registrado:", servicio)


def crear_reserva(fj):
    print("\n-- Nueva reserva --")
    cliente = elegir(fj.clientes, "cliente")
    if cliente is None:
        return
    servicio = elegir(fj.servicios, "servicio")
    if servicio is None:
        return

    duracion = pedir_numero("Duración en horas (máx. 12)")
    descuento = pedir_numero("Descuento 0-1 (Enter = sin descuento)") or 0.0

    # Parámetros propios de cada tipo de servicio
    extras = {}
    if isinstance(servicio, ReservaSala):
        extras["asistentes"] = pedir_numero("Número de asistentes", int)
        extras["proyector"] = pedir_si_no("¿Requiere proyector?")
    elif isinstance(servicio, AlquilerEquipo):
        extras["cantidad"] = pedir_numero("Cantidad de equipos (1-10)", int)
        extras["seguro"] = pedir_si_no("¿Con seguro?")
    elif isinstance(servicio, AsesoriaEspecializada):
        extras["nivel"] = pedir_texto("Nivel (junior / senior / experto)")

    fj.crear_reserva(cliente, servicio, duracion, descuento, **extras)


def cancelar_reserva(fj):
    print("\n-- Cancelar reserva --")
    reserva = elegir(fj.reservas, "reserva")
    if reserva:
        estado_previo = reserva.estado
        fj.cancelar_reserva(reserva)
        if reserva.estado is not estado_previo:  # solo si realmente cambió
            print("  Reserva cancelada.")


def listar(fj):
    print("\n-- Clientes --")
    for c in fj.clientes or ["  (ninguno)"]:
        print("  ", c)
    print("-- Servicios --")
    for s in fj.servicios or ["  (ninguno)"]:
        print("  ", s)
    print("-- Reservas --")
    for r in fj.reservas or ["  (ninguna)"]:
        print("  ", r)
    print("\n  " + fj.resumen())


MENU = """
===== SOFTWARE FJ =====
1) Registrar cliente
2) Registrar servicio
3) Crear reserva
4) Cancelar reserva
5) Listar todo / resumen
0) Salir
"""

ACCIONES = {
    "1": registrar_cliente,
    "2": registrar_servicio,
    "3": crear_reserva,
    "4": cancelar_reserva,
    "5": listar,
}


def main():
    log.info("===== INICIO DE SESIÓN =====")
    fj = GestorFJ()
    while True:
        try:
            print(MENU)
            opcion = input("Elige una opción: ").strip()
            if opcion == "0":
                break
            accion = ACCIONES.get(opcion)
            if accion is None:
                print("  Opción no válida.")
                log.error("Opción de menú no válida: %r", opcion)
                continue
            accion(fj)
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break
        except Exception:  # último recurso: el menú nunca se cae
            log.exception("Error inesperado en el menú")
            print("  Ocurrió un error inesperado; quedó registrado en el log.")
    log.info("===== FIN DE SESIÓN | %s =====", fj.resumen())
    print("Hasta pronto.")


if __name__ == "__main__":
    main()
