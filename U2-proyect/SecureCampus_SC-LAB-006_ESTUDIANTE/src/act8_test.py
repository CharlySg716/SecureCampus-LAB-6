import hashlib, os, tempfile, time
from src import auth, db

path = os.path.join(tempfile.mkdtemp(), "test.db")
db.seed_demo(path)

def q(sql, args=()):
    con = db.connect(path)
    rows = con.execute(sql, args).fetchall()
    con.close()
    return rows

print("== 1. Hashes de contraseña (misma contraseña, distinta sal) ==")
for r in q("SELECT username, password_hash FROM users"):
    print(r["username"], r["password_hash"][:70])

print("\n== 2. Login correcto e incorrecto ==")
token, csrf = auth.login("alumna_eli", "Laboratorio2026!", path)
print("token:", token)
print("csrf :", csrf)
print("contraseña mala ->", auth.login("alumna_eli", "mala", path))
print("usuario falso   ->", auth.login("no_existe", "x", path))

print("\n== 3. Qué guarda la tabla sessions ==")
fila = q("SELECT * FROM sessions")[0]
print(dict(fila))
print("token crudo aparece en la BD:", token in str(tuple(fila)))
print("token_hash == sha256(token):",
      fila["token_hash"] == hashlib.sha256(token.encode()).hexdigest())

print("\n== 4. Sesión válida y logout ==")
print("antes :", auth.session_user(token, path)["username"])
auth.logout(token, path)
print("después:", auth.session_user(token, path))
print("filas en sessions:", len(q("SELECT * FROM sessions")))

print("\n== 5. Expiración ==")
token2, _ = auth.login("alumna_eli", "Laboratorio2026!", path)
con = db.connect(path)
con.execute("UPDATE sessions SET expires_at=?", (int(time.time()) - 1,))
con.commit(); con.close()
print("sesión vencida ->", auth.session_user(token2, path))
print("la fila sigue en la BD:", len(q("SELECT * FROM sessions")))

print("\n== 6. Sesiones acumuladas por logins repetidos ==")
for _ in range(3):
    auth.login("alumna_eli", "Laboratorio2026!", path)
print("filas para user 3:", len(q("SELECT * FROM sessions WHERE user_id=3")))

print("\n== 7. Tiempo de respuesta: usuario real vs inexistente ==")
def medir(u, n=5):
    t = time.perf_counter()
    for _ in range(n):
        auth.login(u, "x", path)
    return (time.perf_counter() - t) / n
print(f"existente  : {medir('alumna_eli')*1000:.1f} ms")
print(f"inexistente: {medir('no_existe')*1000:.1f} ms")