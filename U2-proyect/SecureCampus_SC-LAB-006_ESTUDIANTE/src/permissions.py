
def puede_modificar(user, student_id, group_id, con):
    """
    Solo permite modificar calificaciones a profesores
    asignados al grupo y con estudiantes inscritos.
    """

    if user['role'] != 'profesor':
        return False

    resultado = con.execute(
        """
        SELECT 1
        FROM groups g
        INNER JOIN enrollments e ON e.group_id = g.id
        WHERE g.professor_id = ?
          AND g.id = ?
          AND e.student_id = ?
        """,
        (user['id'], group_id, student_id)
    ).fetchone()

    return resultado is not None


def puede_consultar(user, student_id, group_id, con):
    """
    Los estudiantes consultan sus propias calificaciones.
    Los profesores consultan las de estudiantes de sus grupos.
    Los administradores no tienen permisos por defecto.
    """

    if user['role'] == 'estudiante':
        if user['id'] != student_id:
            return False

        resultado = con.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ?
              AND group_id = ?
            """,
            (student_id, group_id)
        ).fetchone()

        return resultado is not None

    if user['role'] == 'profesor':
        resultado = con.execute(
            """
            SELECT 1
            FROM groups g
            INNER JOIN enrollments e ON e.group_id = g.id
            WHERE g.professor_id = ?
              AND g.id = ?
              AND e.student_id = ?
            """,
            (user['id'], group_id, student_id)
        ).fetchone()

        return resultado is not None

    return False
