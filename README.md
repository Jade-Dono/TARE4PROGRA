# Software FJ — Sistema de clientes, servicios y reservas

Sistema orientado a objetos en Python, sin base de datos: todo en objetos y listas
en memoria. El único archivo que se escribe es el log de eventos y errores (`logs/software_fj.log`).

## Ejecutar

```bash
python main.py
```

No requiere dependencias externas.

## Estructura

```
software_fj/
├── excepciones.py   # jerarquía de excepciones personalizadas
├── logger.py        # registro en logs/software_fj.log
├── entidades.py     # EntidadBase (clase abstracta)
├── cliente.py       # Cliente (encapsulación + validaciones)
├── servicios.py     # Servicio (abstracta) + ReservaSala, AlquilerEquipo, AsesoriaEspecializada
├── reserva.py       # Reserva (confirmar / cancelar / procesar) + EstadoReserva
└── gestor.py        # GestorFJ: listas internas y captura global de errores
main.py              # simulación completa
```

## Principios POO aplicados

| Principio | Dónde |
|---|---|
| Abstracción | `EntidadBase` y `Servicio` (`ABC` + `@abstractmethod`) |
| Herencia | `Cliente`, `Servicio`, `Reserva` ← `EntidadBase`; 3 servicios ← `Servicio` |
| Polimorfismo | `describir()`, `calcular_costo_base()`, `validar_parametros()` sobrescritos en cada servicio |
| Encapsulación | atributos privados con `@property` y validación en los setters; listas del gestor expuestas como copias |
| Sobrecarga | `calcular_costo(h)`, `(h, impuesto)`, `(h, impuesto, descuento)`, `calcular_costo_con_impuesto`, `calcular_costo_con_descuento`; `buscar_cliente` por `int` (id) o `str` (documento) con `singledispatchmethod` |

> Python no tiene sobrecarga por firma como Java; se implementa con parámetros opcionales,
> variantes nombradas y `functools.singledispatchmethod`.

## Manejo de excepciones

- Jerarquía propia: `ErrorSoftwareFJ` → `ClienteInvalidoError`, `ServicioInvalidoError`,
  `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`,
  `CalculoInconsistenteError`, `ParametroFaltanteError`.
- `Reserva.confirmar()` usa `try / except / else / finally`.
- Encadenamiento con `raise ... from e`: el log registra la causa original.
- `GestorFJ._ejecutar()` captura errores previstos e imprevistos (con traceback), los registra y
  devuelve `None`, así el sistema sigue activo.
