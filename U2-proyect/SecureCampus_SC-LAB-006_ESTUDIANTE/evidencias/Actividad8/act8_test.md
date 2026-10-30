### 1. Hashes de contraseña (misma contraseña, distinta sal)
- profe_ana scrypt:32768:8:1$s6djvfUeutTR8V9B$d6c997f0ee105fa617603e1c548d50b7321f

- profe_luis scrypt:32768:8:1$VxBXHhosc0d7UhLf$56ed20b5cca3989eb8d76905adc691be5ed7

- alumna_eli scrypt:32768:8:1$n8LlSwxYRaDDl9Mk$803da9fd05443b944edb421f0ddc19570efd

- alumno_paz scrypt:32768:8:1$6mjPHxizQ33l8yt9$f7e7e34b766c85a7743619eb4753775dedfe

- admin_demo scrypt:32768:8:1$YvUMNdNW5XXPxhgt$a95849d7dff4bff408eb49d81e359045d051

### 2. Login correcto e incorrecto
- **token**: AnZfDaGQ1a3wtunpzwdjjsH_GViqh53y20yJ-2j2hN8

- **csrf** : I1IzEmuMw06cdXISnC8sYOS5s4r3IUFf

- **contraseña mala** -> None

- **usuario falso**   -> None

### 3. Qué guarda la tabla sessions
{'token_hash': '7f9eafb010e35dc6671463ca172220f26020d66c8efc81273aa9aaa6ef752326', 'user_id': 3, 'csrf_token': 'I1IzEmuMw06cdXISnC8sYOS5s4r3IUFf', 'expires_at': 1793370722}

- **¿El token crudo aparece en la BD?** : False

- **token_hash sha256(token)**: True

### 4. Sesión válida y logout
antes : alumna_eli

después: None

filas en sessions: 0

### 5. Expiración
sesión vencida -> None

la fila sigue en la BD: 1

### 6. Sesiones acumuladas por logins repetidos
filas para user 3: 4

### 7. Tiempo de respuesta: usuario real vs inexistente
existente  : 110.1 ms

inexistente: 0.2 ms