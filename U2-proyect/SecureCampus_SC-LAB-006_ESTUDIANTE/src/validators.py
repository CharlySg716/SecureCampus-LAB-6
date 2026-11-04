from decimal import Decimal, InvalidOperation

def validar_calificacion(valor):
    # TODO: rechazar valores nulos, booleanos, texto no numérico, NaN, Infinity, fuera de 0..100 y >2 decimales.
    # No redondear entradas incorrectas.
    
    # 1. Rechazar valores nulos
    if valor is None:
        raise ValueError("El valor no puede ser nulo.")
        
    # 2. Rechazar valores booleanos explícitamente (en Python bool hereda de int)
    if isinstance(valor, bool):
        raise ValueError("Los valores booleanos no son válidos.")

     # 3. Rechazar cadenas vacías o con espacios en blanco
    if isinstance(valor, str):
        if not valor.strip():
            raise ValueError("La cadena no puede estar vacía.")
        val_str = valor.strip()
    else:
        val_str = str(valor)
    
    # 4. Convertir a Decimal (esto rechaza texto no numérico)
    try:
        dec = Decimal(val_str)
    except (InvalidOperation, ValueError):
        raise ValueError("El valor proporcionado no es un número válido.")

       # 5. Rechazar valores NaN e infinitos
    if dec.is_nan() or dec.is_infinite():
        raise ValueError("Los valores NaN o infinitos no están permitidos.")

     # 6. Validar que el rango esté estrictamente entre 0 y 100
    if not (Decimal('0') <= dec <= Decimal('100')):
        raise ValueError("La calificación debe estar entre 0 y 100.")

    # 7. Validar un máximo de dos decimales sin redondeo silencioso
    exp = dec.as_tuple().exponent
    if isinstance(exp, int) and exp < -2:
        raise ValueError("La calificación no puede tener más de dos decimales.")

        
    return dec

# Aliases de compatibilidad requeridos por el proyecto
validate_grade = validar_calificacion
validate_score = validar_calificacion
