#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUBLICAR ESTA CARPETA EN GITHUB
===============================

Sube todos los archivos de esta carpeta a un repositorio de GitHub. Si el
repositorio no existe lo crea, y si algo cambia en local lo vuelve a subir.

Uso rápido
----------
    python publicar_github.py

    Ese comando pregunta el nombre del repositorio y sube todo.

Opciones
--------
    --repo NOMBRE        nombre del repositorio (si no se indica, lo pregunta)
    --private            crea el repositorio como privado (por defecto público)
    --watch              queda vigilando la carpeta y resube al detectar cambios
    --interval SEGUNDOS  cada cuánto revisa en modo --watch (por defecto 5)
    --pages              activa GitHub Pages para ver la app en línea
    --token TOKEN        token de GitHub (si no, usa GITHUB_TOKEN o lo pregunta)
    --branch RAMA        rama a publicar (por defecto main)
    --local              solo prepara el repositorio local y hace el commit
    --dry-run            muestra lo que haría, sin tocar nada
    --force              fuerza la subida si el remoto tiene historia distinta

Token
-----
Se crea en https://github.com/settings/tokens
  · Token clásico: marca el permiso "repo" (y "workflow" si usas Actions).
  · Token fine-grained: Contents = Read and write y Administration = Read and write.
También puedes definirlo en la variable de entorno GITHUB_TOKEN.

Archivos que NO se suben
------------------------
Los mayores de 50 MB (GitHub rechaza más de 100 MB), los *.pbf, los *.crdownload,
las carpetas .git / __pycache__ y los archivos temporales del sistema. Se genera
un .gitignore para que git tampoco los vea.
"""

import argparse
import base64
import getpass
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
API = "https://api.github.com"

# Límites y exclusiones
MAX_MB = 50
DIRS_IGNORADOS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}
SUFIJOS_IGNORADOS = {".pbf", ".crdownload", ".part", ".pyc", ".pyo", ".zip", ".7z", ".rar", ".tmp"}
NOMBRES_IGNORADOS = {".DS_Store", "Thumbs.db", "desktop.ini", ".github_token", "publicar_github.log"}


def dir_ignorado(nombre):
    """Carpetas ocultas (perfiles de Chrome, cachés) nunca se suben; .github sí."""
    if nombre in DIRS_IGNORADOS:
        return True
    if nombre.startswith(".") and nombre != ".github":
        return True
    return False

GITIGNORE = """\
# Generado por publicar_github.py
*.pbf
*.crdownload
*.part
*.zip
*.7z
*.rar
__pycache__/
*.pyc
.venv/
venv/
node_modules/
.idea/
.vscode/
.DS_Store
Thumbs.db
desktop.ini
.github_token
publicar_github.log
"""


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de consola
# ─────────────────────────────────────────────────────────────────────────────
def preparar_consola():
    """Fuerza UTF-8 en la consola de Windows para no romper con tildes."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def log(texto=""):
    print(texto, flush=True)


def titulo(texto):
    log("")
    log("─" * 64)
    log(texto)
    log("─" * 64)


def humano(n_bytes):
    for unidad in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024 or unidad == "GB":
            return f"{n_bytes:.0f} {unidad}" if unidad == "B" else f"{n_bytes:.1f} {unidad}"
        n_bytes /= 1024


# ─────────────────────────────────────────────────────────────────────────────
# Archivos de la carpeta
# ─────────────────────────────────────────────────────────────────────────────
def listar_archivos():
    """Devuelve (archivos_a_subir, omitidos) recorriendo la carpeta."""
    incluir, omitir = [], []
    for ruta in sorted(RAIZ.rglob("*")):
        if not ruta.is_file():
            continue
        relativa = ruta.relative_to(RAIZ)
        if any(dir_ignorado(parte) for parte in relativa.parts):
            continue
        nombre = ruta.name
        if nombre in NOMBRES_IGNORADOS or nombre.startswith(".~") or nombre.startswith("~$"):
            continue
        if ruta.suffix.lower() in SUFIJOS_IGNORADOS:
            omitir.append((relativa, ruta.stat().st_size, "extensión excluida"))
            continue
        tam = ruta.stat().st_size
        if tam > MAX_MB * 1024 * 1024:
            omitir.append((relativa, tam, f"supera {MAX_MB} MB"))
            continue
        incluir.append(ruta)
    return incluir, omitir


def huella_carpeta():
    """Firma de la carpeta para detectar cambios (ruta, tamaño y fecha)."""
    partes = []
    for ruta in listar_archivos()[0]:
        est = ruta.stat()
        partes.append(f"{ruta.relative_to(RAIZ)}|{est.st_size}|{est.st_mtime_ns}")
    return hashlib.sha256("\n".join(sorted(partes)).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Git
# ─────────────────────────────────────────────────────────────────────────────
def git(*args, check=True):
    entorno = os.environ.copy()
    entorno["GIT_TERMINAL_PROMPT"] = "0"  # nunca pedir usuario/contraseña por consola
    try:
        proceso = subprocess.run(
            ["git", *args],
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=entorno,
        )
    except FileNotFoundError:
        raise SystemExit(
            "No se encontró Git. Instálalo desde https://git-scm.com/download/win "
            "y vuelve a ejecutar el script."
        )
    if check and proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout or "").strip()
        raise SystemExit(f"Error al ejecutar «git {' '.join(args)}»:\n{detalle}")
    return proceso


def asegurar_repositorio_local(usuario, rama):
    """Inicializa git, configura autor, .gitignore y la rama principal."""
    if not (RAIZ / ".git").exists():
        git("init")
        log("  · repositorio git inicializado")
    # Rama principal (compatible con git viejos)
    git("symbolic-ref", "HEAD", f"refs/heads/{rama}", check=False)

    if not git("config", "user.name", check=False).stdout.strip():
        git("config", "user.name", usuario or "Publicador GitHub")
    if not git("config", "user.email", check=False).stdout.strip():
        correo = f"{usuario}@users.noreply.github.com" if usuario else "publicador@localhost"
        git("config", "user.email", correo)

    destino = RAIZ / ".gitignore"
    actual = destino.read_text(encoding="utf-8") if destino.exists() else ""
    if "# Generado por publicar_github.py" not in actual:
        destino.write_text((actual + "\n" if actual else "") + GITIGNORE, encoding="utf-8")
        log("  · .gitignore actualizado")

    # Exclusiones solo locales (no se publican): perfiles de navegador y temporales
    info = RAIZ / ".git" / "info"
    info.mkdir(parents=True, exist_ok=True)
    archivo_excluir = info / "exclude"
    previo = archivo_excluir.read_text(encoding="utf-8") if archivo_excluir.exists() else ""
    patrones = [".cp*/", ".chrome*/", ".tmp*/", "*.log", ".github_token", "Thumbs.db", "desktop.ini"]
    faltantes = [p for p in patrones if p not in previo]
    if faltantes:
        archivo_excluir.write_text(previo + ("\n" if previo else "") + "\n".join(faltantes) + "\n", encoding="utf-8")
        log("  · exclusiones locales de git actualizadas")


def configurar_remoto(propietario, repositorio):
    url = f"https://github.com/{propietario}/{repositorio}.git"
    actual = git("remote", "get-url", "origin", check=False).stdout.strip()
    if actual == url:
        return url
    if actual:
        git("remote", "set-url", "origin", url)
        log(f"  · remoto actualizado → {url}")
    else:
        git("remote", "add", "origin", url)
        log(f"  · remoto agregado → {url}")
    return url


def commit_si_hay_cambios(mensaje):
    git("add", "-A")
    estado = git("status", "--porcelain", check=False).stdout.strip()
    if not estado:
        log("  · sin cambios locales que confirmar")
        return False
    git("commit", "-m", mensaje)
    lineas = len(estado.splitlines())
    log(f"  · commit creado con {lineas} archivo(s) modificado(s)")
    return True


def empujar(token, rama, forzar=False):
    """Sube la rama usando el token solo en esta orden (no queda guardado)."""
    credencial = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    cabecera = f"http.https://github.com/.extraheader=AUTHORIZATION: basic {credencial}"
    args = ["-c", cabecera, "push", "-u", "origin", rama]
    if forzar:
        args.insert(3, "--force-with-lease")
    resultado = git(*args, check=False)
    if resultado.returncode == 0:
        log(f"  · subido a origin/{rama}")
        return True

    salida = (resultado.stderr or resultado.stdout or "").strip()
    log("  · el remoto tiene historia distinta; intentando integrar…")
    git("-c", cabecera, "pull", "--rebase", "origin", rama, check=False)
    resultado = git(*args, check=False)
    if resultado.returncode == 0:
        log(f"  · subido a origin/{rama} tras integrar")
        return True
    raise SystemExit(
        "No se pudo subir. Detalle de git:\n" + salida +
        "\n\nSugerencia: ejecuta de nuevo con --force si el repositorio es solo tuyo."
    )


# ─────────────────────────────────────────────────────────────────────────────
# GitHub API
# ─────────────────────────────────────────────────────────────────────────────
def api(metodo, ruta, token, datos=None):
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(
        API + ruta,
        data=cuerpo,
        method=metodo,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "publicar-github-sena",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            texto = respuesta.read().decode("utf-8") or "{}"
            return respuesta.status, json.loads(texto)
    except urllib.error.HTTPError as error:
        texto = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(texto)
        except json.JSONDecodeError:
            return error.code, {"message": texto}
    except urllib.error.URLError as error:
        raise SystemExit(f"No se pudo conectar con GitHub: {error.reason}")


def validar_token(token):
    estado, datos = api("GET", "/user", token)
    if estado == 401:
        raise SystemExit("El token no es válido o expiró. Genera uno nuevo en https://github.com/settings/tokens")
    if estado != 200:
        raise SystemExit(f"GitHub respondió {estado}: {datos.get('message', datos)}")
    return datos["login"]


def crear_repositorio(token, propietario, nombre, privado):
    estado, existente = api("GET", f"/repos/{propietario}/{nombre}", token)
    if estado == 200:
        log(f"  · el repositorio ya existe: {existente['html_url']}")
        return existente
    if estado not in (404, 403):
        raise SystemExit(f"No se pudo consultar el repositorio ({estado}): {existente.get('message', existente)}")

    estado, creado = api("POST", "/user/repos", token, {
        "name": nombre,
        "private": bool(privado),
        "auto_init": False,
        "description": "Georreferenciación de datos · Ficha del Ciudadano · SENA",
        "has_issues": True,
        "has_wiki": False,
    })
    if estado == 201:
        log(f"  · repositorio creado: {creado['html_url']}")
        return creado
    if estado == 422:
        log("  · el repositorio ya existe (o el nombre no es válido)")
        estado, existente = api("GET", f"/repos/{propietario}/{nombre}", token)
        if estado == 200:
            return existente
    raise SystemExit(f"No se pudo crear el repositorio ({estado}): {creado.get('message', creado)}")


def habilitar_pages(token, propietario, repositorio, rama):
    estado, datos = api("POST", f"/repos/{propietario}/{repositorio}/pages", token, {
        "source": {"branch": rama, "path": "/"}
    })
    if estado in (201, 204):
        log("  · GitHub Pages activado")
    elif estado == 409:
        log("  · GitHub Pages ya estaba activo")
    else:
        log(f"  · no se pudo activar Pages ({estado}): {datos.get('message', '')}")


# ─────────────────────────────────────────────────────────────────────────────
# Flujo principal
# ─────────────────────────────────────────────────────────────────────────────
def normalizar_repo(texto):
    """Acepta «repo», «usuario/repo» o la URL completa y devuelve solo el nombre."""
    limpio = (texto or "").strip()
    limpio = re.sub(r"^https?://(www\.)?github\.com/", "", limpio, flags=re.IGNORECASE)
    limpio = limpio.strip("/")
    if "/" in limpio:
        partes = [p for p in limpio.split("/") if p]
        limpio = partes[-1] if partes else limpio
    if limpio.lower().endswith(".git"):
        limpio = limpio[:-4]
    limpio = re.sub(r"[^A-Za-z0-9._-]+", "-", limpio)
    return limpio.strip("-._")


def pedir_nombre_repositorio(propuesta="geosenamed"):
    log("")
    log("Nombre del repositorio en GitHub")
    log("  Puedes escribir solo el nombre o pegar la URL completa.")
    log(f"  (Enter para usar «{propuesta}»)")
    while True:
        try:
            entrada = input("  Nombre: ").strip()
        except (EOFError, KeyboardInterrupt):
            log("")
            raise SystemExit("Operación cancelada.")
        if not entrada:
            entrada = propuesta
        limpio = normalizar_repo(entrada)
        if 1 <= len(limpio) <= 100:
            return limpio
        log("  Nombre no válido: usa letras, números, guiones o puntos (máx. 100).")


def pedir_token():
    log("")
    log("Token de GitHub (no se muestra al escribir)")
    log("  Créalo en https://github.com/settings/tokens con permiso «repo»")
    try:
        return getpass.getpass("  Token: ").strip()
    except (EOFError, KeyboardInterrupt):
        log("")
        raise SystemExit("Operación cancelada.")


def mostrar_archivos(maximo=40):
    incluir, omitir = listar_archivos()
    total = sum(r.stat().st_size for r in incluir)
    log(f"  · {len(incluir)} archivo(s) para subir ({humano(total)})")
    for ruta in incluir[:maximo]:
        log(f"      {ruta.relative_to(RAIZ)}  ({humano(ruta.stat().st_size)})")
    if len(incluir) > maximo:
        log(f"      … y {len(incluir) - maximo} archivo(s) más")
    if omitir:
        log(f"  · {len(omitir)} archivo(s) omitido(s):")
        for ruta, tam, motivo in omitir[:10]:
            log(f"      {ruta}  ({humano(tam)} · {motivo})")
        if len(omitir) > 10:
            log(f"      … y {len(omitir) - 10} más")
    return incluir


def publicar_una_vez(token, rama, forzar):
    titulo("Subiendo cambios")
    mensaje = time.strftime("Actualización %Y-%m-%d %H:%M:%S")
    cambios = commit_si_hay_cambios(mensaje)
    subido = empujar(token, rama, forzar)
    return cambios or subido


def main():
    preparar_consola()
    analizador = argparse.ArgumentParser(
        description="Publica esta carpeta en un repositorio de GitHub.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplo: python publicar_github.py --watch",
    )
    analizador.add_argument("--repo", help="nombre del repositorio")
    analizador.add_argument("--private", action="store_true", help="repositorio privado")
    analizador.add_argument("--watch", action="store_true", help="vigilar cambios y resubir")
    analizador.add_argument("--interval", type=int, default=5, help="segundos entre revisiones en --watch")
    analizador.add_argument("--pages", action="store_true", help="activar GitHub Pages")
    analizador.add_argument("--token", help="token de GitHub")
    analizador.add_argument("--branch", default="main", help="rama a publicar (por defecto main)")
    analizador.add_argument("--local", action="store_true", help="solo repositorio local y commit")
    analizador.add_argument("--dry-run", action="store_true", help="mostrar lo que haría, sin cambios")
    analizador.add_argument("--force", action="store_true", help="forzar la subida")
    args = analizador.parse_args()

    titulo("Publicar en GitHub · Datos Sensibles Georreferenciados (SENA)")
    log(f"Carpeta: {RAIZ}")

    incluir = mostrar_archivos()
    if not incluir:
        raise SystemExit("No hay archivos para subir.")

    if args.dry_run:
        log("")
        log("Simulación (--dry-run): no se creó el repositorio ni se subió nada.")
        log("Comandos que se ejecutarían: git init / add / commit / push")
        if args.watch:
            log("Modo vigilancia: se resubiría al detectar cambios.")
        return

    repositorio = normalizar_repo(args.repo) if args.repo else pedir_nombre_repositorio()
    if not repositorio:
        raise SystemExit("El nombre del repositorio no es válido.")
    log("")
    log(f"Repositorio: {repositorio}  ({'privado' if args.private else 'público'})")

    if args.local:
        asegurar_repositorio_local("", args.branch)
        commit_si_hay_cambios(time.strftime("Actualización %Y-%m-%d %H:%M:%S"))
        log("")
        log("Repositorio local listo (no se subió nada por usar --local).")
        return

    token = args.token or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        token = pedir_token()
    if not token:
        raise SystemExit("Se necesita un token para publicar.")

    titulo("Conectando con GitHub")
    propietario = validar_token(token)
    log(f"  · usuario autenticado: {propietario}")
    datos = crear_repositorio(token, propietario, repositorio, args.private)
    url_repo = datos.get("html_url", f"https://github.com/{propietario}/{repositorio}")

    asegurar_repositorio_local(propietario, args.branch)
    configurar_remoto(propietario, repositorio)
    publicar_una_vez(token, args.branch, args.force)

    log("")
    log(f"Repositorio: {url_repo}")
    log(f"Sitio web:   https://{propietario}.github.io/{repositorio}/")
    if args.pages:
        habilitar_pages(token, propietario, repositorio, args.branch)

    if not args.watch:
        log("")
        log("Listo. Para resubir automáticamente cuando cambies algo:")
        log("    python publicar_github.py --watch")
        return

    titulo(f"Vigilando cambios cada {args.interval} s  ·  Ctrl+C para salir")
    anterior = huella_carpeta()
    try:
        while True:
            time.sleep(max(1, args.interval))
            actual = huella_carpeta()
            if actual == anterior:
                continue
            log("")
            log(time.strftime("[%H:%M:%S]") + " Cambios detectados, subiendo…")
            time.sleep(1.0)  # deja que el archivo se termine de escribir
            try:
                publicar_una_vez(token, args.branch, args.force)
                anterior = huella_carpeta()
            except SystemExit as error:
                log(f"  · error al subir: {error}")
    except KeyboardInterrupt:
        log("")
        log("Vigilancia detenida.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada.", flush=True)
        sys.exit(1)
