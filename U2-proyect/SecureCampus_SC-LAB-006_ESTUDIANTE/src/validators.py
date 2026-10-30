from decimal import Decimal

def validar_calificacion(valor):
    # TODO: rechazar valores nulos, booleanos, texto no numérico, NaN, Infinity, fuera de 0..100 y >2 decimales.
    # No redondear entradas incorrectas.
    
    # 1. Rechazar valores nulos
    if valor is None:
        raise ValueError("El valor no puede ser nulo.")

    return Decimal(str(valor))

# compatibilidad
validate_grade = validar_calificacion
validate_score = validar_calificacion