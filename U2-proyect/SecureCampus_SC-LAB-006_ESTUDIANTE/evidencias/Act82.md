# SecureCampus LAB 6: Actividad 8

## Contraseñas: hash y verificación

`generate_password_hash` se usa en `seed_demo` (`db.py`). Genera una sal aleatoria, aplica scrypt y devuelve una cadena con el formato `scrypt:32768:8:1$sal$hash`, donde 32768, 8 y 1 son los parámetros N, r y p. Esa cadena se guarda en `users.password_hash`.

`check_password_hash` se usa en `login` (`auth.py`). Lee el método, los parámetros y la sal de la cadena guardada, recalcula el hash con la contraseña recibida y compara. Si el usuario no existe o la contraseña falla, `login` devuelve `None` sin indicar cuál de las dos cosas ocurrió.

En la prueba, los cinco usuarios comparten contraseña y tienen cinco hashes distintos, porque cada uno lleva su propia sal (sección 7, bloque 1).

### Hash frente a cifrado

Un hash es una función de un solo sentido: del resultado no se recupera la contraseña. El servidor verifica recalculando y comparando, y nunca necesita conocer la contraseña original.

El cifrado es reversible: con la clave se recupera el texto original. Si las contraseñas estuvieran cifradas, quien robe la clave obtiene todas a la vez. Con hash lento y sal, cada contraseña se ataca por separado y el costo de cada intento es alto.

## Tokens de sesión y CSRF

`login` genera dos valores con `secrets.token_urlsafe`: el token de sesión con 32 bytes (unos 256 bits de entropía, 43 caracteres) y el token CSRF con 24 bytes (32 caracteres). El módulo `secrets` usa el generador criptográfico del sistema operativo.

El token de sesión crudo solo viaja al cliente. En la tabla `sessions` se guarda `sha256(token)` en hexadecimal (64 caracteres), junto con `user_id`, `csrf_token` y `expires_at`. Para validar, `session_user` aplica SHA-256 al token recibido y busca esa huella en la tabla.

La prueba confirma ambos puntos: el token crudo no aparece en ningún campo de la fila y `token_hash` coincide con `sha256(token)` (sección 7, bloque 3).

SHA-256 sin sal es suficiente aquí porque el token es aleatorio y tiene 256 bits, así que no hay un diccionario práctico que atacar. Con contraseñas escogidas por personas no bastaría, y por eso allí se usa un hash lento con sal.

El token CSRF queda guardado en claro. Su función es comprobar que una petición de cambio se realiza con el token asociado a la sesión. `session_user` lo devuelve como `csrf_token` para que las rutas lo comparen mediante `secrets.compare_digest`.

## Qué se almacena y qué no

La base de datos nunca contiene la contraseña ni el token de sesión originales. Contiene sus huellas, más el token CSRF y la expiración.

| Dato | ¿Se guarda? | Forma almacenada | Ubicación |
| --- | --- | --- | --- |
| Contraseña | No | — | — |
| Hash de la contraseña | Sí | scrypt con sal por usuario | `users.password_hash` |
| Token de sesión | No | Solo lo recibe el cliente | — |
| Hash del token de sesión | Sí | SHA-256 en hexadecimal | `sessions.token_hash` |
| Token CSRF | Sí | Texto claro | `sessions.csrf_token` |
| Expiración | Sí | Segundos epoch, 1800 s tras el login | `sessions.expires_at` |

Si alguien obtiene el archivo `.db`, no puede reutilizar directamente las sesiones porque necesitaría el token original, y SHA-256 no se invierte de forma práctica.

## Logout y expiración

`logout()` borra de `sessions` la fila cuyo `token_hash` coincide con el token. Después de llamarla, `session_user` devuelve `None` con ese mismo token. En la prueba, antes del logout la sesión resolvía a `alumna_eli` y después quedó en `None` con 0 filas en la tabla (sección 7, bloque 4).

La ruta `/logout` de `app.py` utiliza el método POST. Primero comprueba que exista una sesión autenticada y que la petición incluya el token CSRF correcto. Después llama a `logout()` y elimina la cookie `sc_session` de la respuesta.

La expiración también se aplica: `session_user` filtra con `expires_at>?`, y una sesión con `expires_at` en el pasado devuelve `None`. La fila vencida, en cambio, sigue en la base (1 fila en la prueba), porque ningún código la elimina (sección 7, bloque 5).

La prueba de la función `logout()` está demostrada en la sección 7. No se realizó una prueba HTTP adicional para comprobar la reutilización de la cookie después de ejecutar la ruta `/logout`.

## Evidencia de la ejecución

Salida de una corrida de `act8.py`, con los siete bloques que respaldan las secciones anteriores. Los valores de token, CSRF y sal cambian en cada corrida, y los tiempos del bloque 7 son promedios de 5 intentos en el equipo del autor.

```text
== 1. Hashes de contraseña (misma contraseña, distinta sal) ==
profe_ana scrypt:32768:8:1$s6djvfUeutTR8V9D$d6c997f0ee105fa617603e1c548d50b7321f
profe_luis scrypt:32768:8:1$VxBXHhosc0d7UhLf$56ed20b5cca3989eb8d76905adc691be5ed7
alumna_eli scrypt:32768:8:1$n8LlSwxYRaDDl9Mk$803da9fd05443b944edb421f0ddc19570efd
alumno_paz scrypt:32768:8:1$6mjPHxizQ33l8yt9$f7e7e34b766c85a7743619eb4753775dedfe
admin_demo scrypt:32768:8:1$YvUMNdNW5XXPxhgt$a95849d7dff4bff408eb49d81e359045d051

== 2. Login correcto e incorrecto ==
token: [valor omitido]
csrf : [valor omitido]
contraseña mala -> None
usuario falso   -> None

== 3. Qué guarda la tabla sessions ==
{'token_hash': '7f9eafb010e35dc6671463ca172220f26020d66c8efc81273aa9aaa6ef752326', 'user_id': 3, 'csrf_token': '[valor omitido]', 'expires_at': 1793370722}
token crudo aparece en la BD: False
token_hash == sha256(token): True

== 4. Sesión válida y logout ==
antes : alumna_eli
después: None
filas en sessions: 0

== 5. Expiración ==
sesión vencida -> None
la fila sigue en la BD: 1

== 6. Sesiones acumuladas por logins repetidos ==
filas para user 3: 4

== 7. Tiempo de respuesta: usuario real vs inexistente ==
existente  : 110.1 ms
inexistente: 0.2 ms
```

Nota: Los hashes del bloque 1 aparecen recortados a 70 caracteres. Se omitieron los valores completos de token y CSRF porque son credenciales temporales y no deben compartirse en evidencias públicas.

## Enumeración de usuarios por tiempo de respuesta

`login` tarda 110.1 ms con un usuario existente y 0.2 ms con uno inexistente, unas 550 veces menos (sección 7, bloque 7). Con usuario inexistente la función termina antes de ejecutar `check_password_hash`, mientras que con usuario real paga el costo deliberado de scrypt.

Un atacante que mida los tiempos puede distinguir qué nombres de usuario existen sin conocer ninguna contraseña, aunque el mensaje de error sea idéntico en ambos casos.

La corrección habitual es ejecutar siempre una verificación contra un hash ficticio cuando el usuario no existe, para igualar los tiempos.

## Cookie y CSRF en las rutas

La revisión de `app.py` confirmó que el login utiliza una cookie llamada `sc_session` con los atributos `HttpOnly`, `Secure`, `SameSite=Lax` y `Max-Age=1800`. Esto limita el acceso de JavaScript a la cookie, restringe su envío a conexiones seguras y añade protección frente a solicitudes entre sitios.

La ruta `/logout` exige una sesión autenticada y un token CSRF válido antes de cerrar la sesión. La ruta `PUT /grades/<student_id>/<group_id>` también exige autenticación y CSRF antes de modificar una calificación.

El token se compara con `secrets.compare_digest`, que realiza una comparación diseñada para reducir filtraciones por diferencias de tiempo.

### Resultados de las pruebas manuales

| # | Prueba | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| 1 | Atributos de la cookie | `HttpOnly`, `Secure`, `SameSite=Lax` y expiración presentes | **PASS:** los cuatro atributos aparecen en `Set-Cookie` |
| 2 | JavaScript no lee la cookie | La cookie `sc_session` no aparece en `document.cookie` después de iniciar sesión | **No concluyente:** `document.cookie` devolvió `""`, pero el intento de login desde la consola falló por un error de sintaxis |
| 3 | CSRF ausente | Rechazo con HTTP 403 | **PASS:** HTTP 403, `CSRF inválido` |
| 4 | CSRF correcto | Modificación aceptada | **PASS:** HTTP 200, calificación guardada en 90 |
| 5 | CSRF de otra sesión | Rechazo con HTTP 403 | No realizada |
| 6 | Logout y reutilización de cookie | Logout exitoso y posterior respuesta HTTP 401 al reutilizar la cookie | No realizada |

### Evidencias generadas

| Archivo | Evidencia |
| --- | --- |
| `evidencias/seguridad/cookieAct8.txt` | Respuesta del login y atributos de la cookie |
| `evidencias/seguridad/login_headers.txt` | Encabezados HTTP del login de `profe_ana` |
| `evidencias/seguridad/csrf_ausente.txt` | Rechazo de petición sin token CSRF |
| `evidencias/seguridad/csrf_correcto.txt` | Aceptación de petición con token CSRF válido |


## Limitaciones frente a un sistema de producción

Son nueve limitaciones: tres quedaron demostradas con la ejecución y seis salen de leer el código.

| Limitación | Respaldo | Mitigación en producción |
| --- | --- | --- |
| Las sesiones vencidas no se eliminan | Demostrada, bloque 5 | Tarea periódica de limpieza o borrado al consultar |
| Un nuevo login no invalida las sesiones anteriores | Demostrada, bloque 6 | Límite de sesiones por usuario y opción de cerrar las demás |
| El tiempo de respuesta revela si el usuario existe | Demostrada, bloque 7 | Verificar contra un hash ficticio cuando el usuario no existe |
| Sin límite de intentos ni bloqueo de cuenta | Código de `login` | Límite por usuario y por IP, con espera creciente |
| Expiración fija de 1800 s, sin renovación por actividad ni tope absoluto | `SESSION_SECONDS` en `auth.py` | Expiración por inactividad más una duración máxima |
| Sin MFA, política de contraseñas ni registro de auditoría | Código de `auth.py` | Segundo factor, reglas de contraseña y bitácora de accesos |
| Contraseña de demostración compartida y escrita en el código | `seed_demo` en `db.py` | Credenciales propias por usuario, fuera del repositorio |
| SQLite en un archivo local, sin cifrado en reposo ni soporte para varios servidores | `connect` en `db.py` | Base de datos de servidor con cifrado en reposo |
| No se observa una política de HTTPS forzado en la aplicación | Configuración de Flask en `app.py` | HTTPS obligatorio en producción y cookie `Secure` |

## Conclusiones

El almacenamiento de credenciales y sesiones sigue buenas prácticas: contraseñas con scrypt y sal por usuario, tokens aleatorios de 256 bits y solo el SHA-256 del token de sesión en la base de datos. La función de logout y la expiración invalidan las sesiones en el servidor.

La ejecución también encontró tres debilidades concretas: las sesiones vencidas se acumulan, los logins repetidos no invalidan sesiones previas y el tiempo de respuesta permite enumerar usuarios (110.1 ms frente a 0.2 ms).

La revisión de `app.py` confirmó que la cookie incluye `HttpOnly`, `Secure` y `SameSite=Lax`, y que las rutas de modificación y logout exigen un token CSRF válido. Las pruebas HTTP confirmaron el rechazo de solicitudes sin CSRF y la aceptación de una solicitud con el token correcto.

En las pruebas manuales, tres verificaciones quedaron aprobadas, una no pudo concluirse y dos no se realizaron. Estos resultados se distinguen para no presentar como comprobaciones ejecutadas aquellas que no cuentan con evidencia.

En conjunto, la revisión del código y las pruebas realizadas respaldan el funcionamiento de los mecanismos principales de autenticación, almacenamiento de sesiones y protección CSRF, aunque no todas las verificaciones de integración llegaron a ejecutarse.