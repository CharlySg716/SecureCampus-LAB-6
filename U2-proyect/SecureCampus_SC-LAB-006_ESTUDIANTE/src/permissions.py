def puede_modificar(user,student_id,group_id,con):
    # TODO: solo profesor asignado al grupo Y estudiante inscrito en él.
    """
    Permite modificar calificaciones unicamente a profesores
    asignados al grupo y cuando el estudiante esta inscrrito
    """
    #Solo los profesores pueden modificar calificaciones
    if user['role'] != 'profesor':
        return False

    #Comprobar que el profesor este asignado al grupo
    # y que el estudiante este inscrito en ese grupo

    resultado = con.execute(
        """
        SELECT 1
        FROM grupos g
        INNER JOIN ENROLLMENTS e ON e.group_id = g.id
        WHERE g.profesor_id = ?
        AND g.id = ?
        AND e.student_id = ?
        """,
        (user['id'], group_id, student_id)
    ).fetchone()

    return resultado is not None

def puede_consultar(user, student_id, group_id, con):
    # TODO: estudiante propio e inscrito, o profesor asignado al grupo con estudiante inscrito.
    """
    Permite consultar:
    - A los estudiantes, únicamente sus propias calificaciones.
    - A los profesores, las calificaciones de estudiantes
      inscritos en sus grupos asignados.

    Los administradores no tienen acceso por defecto.
    """
    
    # Los estudiantes solamente pueden consultar sus propias notas.
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

    # Los profesores solamente pueden consultar las notas
    # de estudiantes inscritos en sus grupos.
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

    # Cualquier otro rol queda denegado por defecto.
    return False
