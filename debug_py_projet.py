#!/usr/bin/env python3

"""
Archivo: debub_py_proyect.py

Descripción breve: Script de diagnóstico para proyectos Python tipo "src layout" o similar.

Descripción amplia: 
    Se trata de una utilidad de diagnóstico. Está Pensada para ejecutarse así, desde la raíz del proyecto:

        source <tu_entorno>/bin/activate   # (si usas venv)
        python debug_project_env.py

Fecha última modificación: (2-dic-2025)

IMPORTANTE:
-----------
Tal y como está ahora, el script es seguro de ejecutar en cualquier momento: no borra nada, no modifica ficheros, 
no instala ni desinstala paquetes. Solo lee información y llama a comandos externos (python/pip/git) en modo lectura.

ADAPTACIÓN A OTROS PROYECTOS:
-----------------------------
Edita la sección "CONFIGURACIÓN" de abajo:

    PROJECT_NAME        -> nombre del proyecto en [project].name del pyproject.toml
    PACKAGE_IMPORT_NAME -> nombre del paquete que se importa en Python
    EXPECTED_SRC_DIR    -> directorio donde está el código fuente (habitual: "src")
    EXTRA_IMPORT_SYMBOLS-> símbolos (funciones, clases, etc.) a probar al importar
"""

import os, sys, subprocess
import sys
import textwrap
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    tomllib = None

# =============================================================================
# CONFIGURACIÓN (EDITA ESTOS VALORES PARA REUSAR EL SCRIPT EN OTROS PROYECTOS)
# =============================================================================

PROJECT_NAME = "help-core-pygame"       # Nombre del proyecto tal y como aparece en pyproject.toml -> [project].name
PACKAGE_IMPORT_NAME = "help_core_pygame"    # Nombre del paquete que se importa en Python
EXPECTED_SRC_DIR = "src"                    # Directorio donde se espera encontrar el código fuente

# Lista de nombres (funciones, clases, etc.) que se intentarán importar
# desde el paquete principal para comprobar su disponibilidad.
EXTRA_IMPORT_SYMBOLS = [
    "open_help_standalone",
    # Añade aquí más símbolos relevantes para otros proyectos
]


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def hr():
    print("\n" + "=" * 80 + "\n")


def run_cmd(label, cmd, check=False):
    """Ejecuta un comando de shell, lo muestra y devuelve (returncode, stdout, stderr)."""
    print(f"▶ {label}")
    print(f"  $ {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
        )
    except FileNotFoundError:
        print("  ✖ Comando no encontrado.")
        return 127, "", "Comando no encontrado"

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    if stdout:
        print("  --- stdout ---")
        print(textwrap.indent(stdout, "  "))
    if stderr:
        print("  --- stderr ---")
        print(textwrap.indent(stderr, "  "))

    print(f"  → Código de salida: {proc.returncode}")
    print()
    return proc.returncode, stdout, stderr


# =============================================================================
# BLOQUES DE COMPROBACIÓN
# =============================================================================

def check_python_info():
    hr()
    print("INFO SOBRE PYTHON ACTUAL")
    print("------------------------")
    print(f"Python executable      : {sys.executable}")
    print(f"Python version         : {sys.version.split()[0]}")
    print(f"Current working dir    : {os.getcwd()}")
    script_path = Path(__file__).resolve()
    print(f"Script path            : {script_path}")
    print(f"Project root (script)  : {script_path.parent}")
    print("sys.prefix             :", sys.prefix)
    print("VIRTUAL_ENV            :", os.environ.get("VIRTUAL_ENV"))
    print("sys.path[0..3]         :", *sys.path[:3], sep="\n        ")




def check_pip_vs_python():
    hr()
    print("COMPARACIÓN: `python -m pip` vs `pip`")
    print("--------------------------------------")

    # Versión de pip vinculada a este Python
    run_cmd("python -m pip --version", [sys.executable, "-m", "pip", "--version"])

    # Versión de pip encontrada en PATH (si existe)
    from shutil import which

    pip_path = which("pip")
    if pip_path is None:
        print("▶ pip no encontrado en PATH (se usará siempre `python -m pip`).")
        return

    print(f"▶ pip encontrado en PATH: {pip_path}")

    # Mostrar la primera línea del script pip (shebang) para ver a qué Python apunta
    try:
        first_line = Path(pip_path).read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        print(f"  Primera línea de {pip_path}:")
        print(f"  {first_line}")
    except Exception as e:
        print(f"  (No se pudo leer {pip_path}: {e})")

    run_cmd("pip --version", ["pip", "--version"])

    print(
        textwrap.dedent(
            """
            Nota:
              - Si el shebang de `pip` NO apunta al mismo ejecutable que `sys.executable`,
                entonces `pip` y `python -m pip` están usando entornos distintos.
            """
        )
    )


def check_pyproject():
    hr()
    print("LECTURA DE pyproject.toml")
    print("-------------------------")

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("✖ No se encontró pyproject.toml en el directorio actual.")
        return

    print(f"▶ Usando pyproject.toml en: {pyproject_path.resolve()}")

    if tomllib is None:
        print("✖ tomllib no disponible (Python < 3.11). No se puede parsear pyproject.toml.")
        return

    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"✖ Error al parsear pyproject.toml: {e}")
        return

    project = data.get("project", {})
    name = project.get("name")
    print(f"  Nombre de proyecto en [project].name: {name!r}")
    if name != PROJECT_NAME:
        print(
            f"  ⚠ Atención: PROJECT_NAME ({PROJECT_NAME!r}) no coincide con "
            f"[project].name ({name!r})."
        )

    tool = data.get("tool", {})
    setuptools_cfg = tool.get("setuptools", {})
    find_cfg = setuptools_cfg.get("packages", {}).get("find", {})
    where = find_cfg.get("where")

    print(f"  Configuración [tool.setuptools.packages.find]: {find_cfg!r}")
    if where:
        print(f"  Directorios de búsqueda de paquetes (where): {where}")
    else:
        print("  (No se ha definido `where` en packages.find; se usará el valor por defecto).")


def check_src_layout():
    hr()
    print("COMPROBACIÓN DE ESTRUCTURA DEL CÓDIGO")
    print("--------------------------------------")

    src_dir = Path(EXPECTED_SRC_DIR)
    if not src_dir.exists():
        print(f"✖ No existe el directorio esperado '{EXPECTED_SRC_DIR}/' en el proyecto.")
        return

    print(f"▶ Directorio de código encontrado en: {src_dir.resolve()}")

    package_dir = src_dir / PACKAGE_IMPORT_NAME
    print(f"▶ Buscando paquete importable en: {package_dir}")

    if not package_dir.exists():
        print(f"✖ No existe el directorio {package_dir}")
        return

    print(f"✔ Existe el directorio {package_dir}")

    init_file = package_dir / "__init__.py"
    if init_file.exists():
        print(f"✔ Encontrado __init__.py en {init_file}")
    else:
        print(f"✖ Falta __init__.py en {package_dir} (sin él, Python no puede importarlo).")

    # Listar ficheros básicos
    print("▶ Contenido de la carpeta del paquete:")
    for p in sorted(package_dir.iterdir()):
        print(f"  - {p.name}")


def check_installation_in_pip():
    hr()
    print("COMPROBACIÓN EN pip (para ESTE Python)")
    print("--------------------------------------")
    print("Usando siempre `python -m pip` para evitar confusiones.")

    # Mostrar info del paquete
    run_cmd(
        f"python -m pip show {PROJECT_NAME}",
        [sys.executable, "-m", "pip", "show", PROJECT_NAME],
    )

    # Listado de paquetes (sin grep para que funcione en Windows también)
    run_cmd(
        "python -m pip list",
        [sys.executable, "-m", "pip", "list"],
    )


def check_import():
    hr()
    print("PRUEBA DE IMPORTACIÓN DEL PAQUETE")
    print("---------------------------------")

    try:
        print(f"▶ Intentando 'import {PACKAGE_IMPORT_NAME}' ...")
        pkg = __import__(PACKAGE_IMPORT_NAME)
    except Exception as e:
        print(f"✖ Error al importar {PACKAGE_IMPORT_NAME}: {e.__class__.__name__}: {e}")
        return

    print(f"✔ Importación de {PACKAGE_IMPORT_NAME} correcta.")
    pkg_file = getattr(pkg, "__file__", None)
    print(f"  {PACKAGE_IMPORT_NAME}.__file__ = {pkg_file}")

    # Probar import de símbolos concretos si se han configurado
    if not EXTRA_IMPORT_SYMBOLS:
        return

    from importlib import import_module

    try:
        module = import_module(PACKAGE_IMPORT_NAME)
    except Exception as e:
        print(f"✖ Error al importar el módulo {PACKAGE_IMPORT_NAME}: {e}")
        return

    for symbol in EXTRA_IMPORT_SYMBOLS:
        print(f"▶ Intentando acceder a '{symbol}' en {PACKAGE_IMPORT_NAME}...")
        try:
            obj = getattr(module, symbol)
        except AttributeError:
            print(f"  ✖ {symbol} no encontrado en {PACKAGE_IMPORT_NAME}.")
        else:
            print(f"  ✔ {symbol} encontrado: {obj}")


def show_sys_path():
    hr()
    print("sys.path (rutas de búsqueda de módulos)")
    print("---------------------------------------")
    for i, p in enumerate(sys.path):
        print(f"  [{i}] {p}")


def list_git_files(root_dir: str = ".") -> list[str]:
    """
    Devuelve la lista de ficheros del proyecto controlados por git,
    incluyendo los no trackeados, pero excluyendo todo lo que ignore
    .gitignore (y los ignores estándar de git).

    Usa:
        git -C root_dir ls-files --cached --others --exclude-standard

    Si root_dir no es un repositorio git o hay algún problema,
    devuelve una lista vacía.
    """
    root_dir = os.path.abspath(root_dir)

    # Comprobamos que parece un repo git
    if not os.path.isdir(os.path.join(root_dir, ".git")):
        print(f"[list_git_files] {root_dir} no parece un repositorio git (falta .git/)")
        print("""
En caso de querer crear un nuevo proyecto en GitHub, cerciorese de:
    1) Estar situado en el directorio del proyecto.
    2) Crear un fichero .gitignore
    3) y por útimo use los siguientes comandos para crea el nueco proyecto
 
git init
git add .
git commit -m "Versión inicial (fecha:...)" 
"""
    ) # Fin del print("""...""")
        return []

    try:
        result = subprocess.run(
            ["git", "-C", root_dir, "ls-files", "--cached", "--others", "--exclude-standard"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        print("[list_git_files] 'git' no está instalado o no está en PATH.")
        return []
    except subprocess.CalledProcessError as e:
        print("[list_git_files] Error al ejecutar git ls-files:")
        if e.stderr:
            print(e.stderr.strip())
        return []

    files = result.stdout.splitlines()
    return files

def show_git_files():
    hr()
    print("FICHEROS DEL PROYECTO SEGÚN GIT (respetando .gitignore):")
    print("--------------------------------------------------------")
    for path in list_git_files("."):
        print("  ", path)

# =============================================================================
# MAIN
# =============================================================================

def main():
    check_python_info()
    check_pip_vs_python()
    check_pyproject()
    check_src_layout()
    check_installation_in_pip()
    check_import()
    show_sys_path()
    show_git_files()
    hr()
    print("FIN DEL DIAGNÓSTICO")
    print("-------------------")
    print(
        textwrap.dedent(
            f"""
            Interpretación típica:
              - Si `python -m pip show {PROJECT_NAME}` NO encuentra el paquete,
                pero `pip list` (a secas) SÍ lo ve, entonces `pip` y `python`
                pertenecen a entornos diferentes.
              - Si el import de {PACKAGE_IMPORT_NAME} falla pero el paquete aparece
                instalado para este Python, suele ser problema de rutas/sys.path
                o de estructura del paquete (por ejemplo, faltan __init__.py).
            """
        )
    )


if __name__ == "__main__":
    main()

