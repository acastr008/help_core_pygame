"""
Programa asistido por ChatGPT en fecha 13/feb/2026 y hora 00:00
Titulo: Diagnóstico previo a subida a PyPI (help_core_pygame)
Descripción: Ejecuta comprobaciones mínimas y deterministas para decidir si es seguro iniciar el proceso de subida a PyPI.
"""

from __future__ import annotations

import dataclasses
import os
import re
import subprocess
import sys
import tomllib
import configparser
from pathlib import Path
from typing import Iterable


# -------------------------------------------------------------------------------------------------
# ZONA DE CONSTANTES (modificar aquí para reutilizar el script en otros proyectos)
# -------------------------------------------------------------------------------------------------

PROJECT_ROOT_MARKER_FILES = ("pyproject.toml",)  # Ficheros cuya presencia identifica la raíz del proyecto.

PYPI_PROJECT_NAME = "help-core-pygame"

# Directorio del venv esperado (según tu flujo: source pyenv_dev_help/bin/activate)
EXPECTED_VENV_DIRNAME = "pyenv_dev_help"

# Rutas que, si tienen cambios locales (git status), se consideran FAIL (fatal)
FATAL_CHANGED_PATHS_EXACT = {
    "pyproject.toml",
    "README.md",
}

# Prefijos fatales (por ejemplo, todo el árbol src/)
FATAL_CHANGED_PATH_PREFIXES = {
    "src/",
}

# Patrones fatales (LICENSE*, MANIFEST.in, etc.)
FATAL_CHANGED_PATH_REGEXES = (
    r"^LICENSE.*",     # LICENSE, LICENSE.md, LICENSE.txt, etc.
    r"^MANIFEST\.in$",  # MANIFEST.in
)

# Ficheros/paths que deben aparecer dentro del wheel
REQUIRED_WHEEL_PATH_SUBSTRINGS = (
    "help_core_pygame/",
    "help_core_pygame/assets/mp3/beep_scroll.mp3",
)

# Directorio temporal para venv de instalación limpia
CLEAN_VENV_DIR = Path("/tmp/venv_pypi_check")

# Códigos de retorno (pensados para uso en CI/scripts)
EXIT_OK = 0
EXIT_WARN = 1
EXIT_FAIL = 2

# -------------------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CheckMessage:
    """Mensaje de diagnóstico asociado a un nivel (OK/WARN/FAIL)."""

    level: str
    text: str


@dataclasses.dataclass
class DiagnosisReport:
    """Informe agregando mensajes y calculando el estado global."""

    messages: list[CheckMessage] = dataclasses.field(default_factory=list)

    def add_ok(self, text: str) -> None:
        self.messages.append(CheckMessage(level="OK", text=text))

    def add_warn(self, text: str) -> None:
        self.messages.append(CheckMessage(level="WARN", text=text))

    def add_fail(self, text: str) -> None:
        self.messages.append(CheckMessage(level="FAIL", text=text))

    def has_fail(self) -> bool:
        return any(m.level == "FAIL" for m in self.messages)

    def has_warn(self) -> bool:
        return any(m.level == "WARN" for m in self.messages)

    def exit_code(self) -> int:
        if self.has_fail():
            return EXIT_FAIL
        if self.has_warn():
            return EXIT_WARN
        return EXIT_OK

    def print(self) -> None:
        for msg in self.messages:
            print(f"{msg.level}: {msg.text}")
        print("-" * 80)
        final = "FAIL" if self.has_fail() else ("WARN" if self.has_warn() else "OK")
        print(f"RESULTADO FINAL: {final}")
        print(f"EXIT CODE: {self.exit_code()}")


def has_pypirc_credentials() -> bool:
    """
    Comprueba si existe ~/.pypirc con credenciales para el repositorio 'pypi'.

    Returns:
        True si se detecta username y password no vacíos en la sección [pypi], False en caso contrario.
    """
    pypirc_path = Path.home() / ".pypirc"
    if not pypirc_path.exists():
        return False

    config = configparser.RawConfigParser()
    try:
        config.read(pypirc_path, encoding="utf-8")
    except Exception:
        return False

    if not config.has_section("pypi"):
        return False

    username = (config.get("pypi", "username", fallback="") or "").strip()
    password = (config.get("pypi", "password", fallback="") or "").strip()

    return bool(username) and bool(password)


def has_keyring_credentials() -> bool:
    """
    Comprueba si keyring tiene un password guardado para el endpoint de subida de PyPI.

    Nota:
        Twine suele usar como servicio la URL legacy y como usuario '__token__' cuando se usa API token.

    Returns:
        True si keyring devuelve una credencial no vacía, False en caso contrario.
    """
    try:
        import keyring  # type: ignore
    except Exception:
        return False

    service = "https://upload.pypi.org/legacy/"
    username = "__token__"

    try:
        secret = keyring.get_password(service, username)
    except Exception:
        return False

    return bool(secret and secret.strip())


def check_pypi_credentials(report: DiagnosisReport) -> None:
    """
    Añade FAIL si no hay credenciales configuradas para subida a PyPI (keyring o ~/.pypirc).
    """
    if has_keyring_credentials():
        report.add_ok("Credenciales PyPI detectadas: keyring (sin mostrar secreto).")
        return

    if has_pypirc_credentials():
        report.add_ok("Credenciales PyPI detectadas: ~/.pypirc (sin mostrar secreto).")
        return

    report.add_fail(
        "No se detectan credenciales para subir a PyPI. "
        "Configura keyring (recomendado) o ~/.pypirc antes de continuar."
    )


def run_command(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """
    Ejecuta un comando y devuelve el CompletedProcess.

    Args:
        argv: Lista de argumentos (sin shell).
        cwd: Directorio de trabajo.

    Returns:
        CompletedProcess con stdout/stderr como texto.

    Raises:
        subprocess.CalledProcessError si el comando falla.
    """
    return subprocess.run(
        argv,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=True,
    )


def find_project_root(start_dir: Path) -> Path | None:
    """
    Localiza la raíz del proyecto subiendo por el árbol hasta encontrar marcadores.

    Args:
        start_dir: Directorio desde el que empezar.

    Returns:
        Ruta de la raíz del proyecto o None si no se encuentra.
    """
    current = start_dir.resolve()
    while True:
        if all((current / marker).exists() for marker in PROJECT_ROOT_MARKER_FILES):
            return current
        if current.parent == current:
            return None
        current = current.parent

def trace_env_state(tag: str) -> None:
    """
    Imprime trazas del estado del entorno para diagnóstico.

    Args:
        tag: Etiqueta corta para identificar el punto de traza.
    """
    venv_value = os.environ.get("VIRTUAL_ENV", "")
    conda_prefix = os.environ.get("CONDA_PREFIX", "")
    pythonhome = os.environ.get("PYTHONHOME", "")

    print(
        "TRAZA diagnose_pypi_readiness, trace_env_state, "
        f"tag={tag} | "
        f"sys.prefix={sys.prefix} | "
        f"sys.base_prefix={getattr(sys, 'base_prefix', '')} | "
        f"sys.executable={sys.executable} | "
        f"VIRTUAL_ENV={venv_value} | "
        f"CONDA_PREFIX={conda_prefix} | "
        f"PYTHONHOME={pythonhome}",
        file=sys.stderr,
    )

def is_expected_venv_active() -> bool:
    """
    Comprueba si el script se está ejecutando dentro del venv esperado.

    Regla robusta:
      - Debe estar activo un venv: sys.prefix != sys.base_prefix
      - El sys.prefix (realpath) o el propio sys.executable deben indicar el nombre del venv esperado.

    Returns:
        True si el venv esperado está activo; False en caso contrario.
    """
    trace_env_state("before_venv_check")    

    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if not in_venv:
        return False

    expected_name = EXPECTED_VENV_DIRNAME

    prefix_path = Path(sys.prefix).resolve()
    executable_path = Path(sys.executable).resolve()

    prefix_matches = prefix_path.name == expected_name or expected_name in prefix_path.parts
    executable_matches = (
        executable_path.parent.name == "bin"
        and (executable_path.parent.parent.name == expected_name or expected_name in executable_path.parts)
    )

    return prefix_matches or executable_matches



def parse_git_status_porcelain(output: str) -> list[str]:
    """
    Parseo mínimo de 'git status --porcelain' para extraer paths.

    Args:
        output: stdout de git status.

    Returns:
        Lista de rutas (strings) afectadas.
    """
    paths: list[str] = []
    for line in output.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue

        # Formato típico: "XY path" o "XY old -> new" en renames.
        # Tomamos el último path si hay "->".
        parts = line.split(maxsplit=2)
        if len(parts) < 2:
            continue

        path_part = parts[-1]
        if "->" in line:
            arrow_parts = line.split("->", maxsplit=1)
            path_part = arrow_parts[-1].strip()

        paths.append(path_part)
    return paths


def is_fatal_path(path_str: str) -> bool:
    """Determina si un path modificado se considera fatal según constantes."""
    normalized = path_str.replace("\\", "/")

    if normalized in FATAL_CHANGED_PATHS_EXACT:
        return True

    for prefix in FATAL_CHANGED_PATH_PREFIXES:
        if normalized.startswith(prefix):
            return True

    for pattern in FATAL_CHANGED_PATH_REGEXES:
        if re.match(pattern, normalized):
            return True

    return False


def read_local_version_from_pyproject(pyproject_path: Path) -> str:
    """
    Lee la versión local desde pyproject.toml (tabla [project] version).

    Args:
        pyproject_path: Ruta a pyproject.toml

    Returns:
        Versión como string.

    Raises:
        ValueError si no encuentra la versión.
    """
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    version = project.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("No se ha encontrado project.version en pyproject.toml.")
    return version.strip()


def version_to_tuple(version_str: str) -> tuple[int, ...]:
    """
    Convierte una versión tipo 'X.Y.Z' a tupla de enteros.

    Nota:
      - Para este proyecto asumimos versiones numéricas simples (p.ej. 0.1.2).
      - Si aparece algo no numérico (post/dev/rc), se considera no soportado y debe fallar.

    Args:
        version_str: Versión en formato string.

    Returns:
        Tupla de enteros.

    Raises:
        ValueError si el formato no es estrictamente numérico con puntos.
    """
    if not re.fullmatch(r"\d+(\.\d+)*", version_str):
        raise ValueError(f"Formato de versión no soportado para comparación: {version_str}")

    parts = version_str.split(".")
    return tuple(int(p) for p in parts)

def parse_pypi_versions_from_pip_index(output: str) -> list[str]:
    """
    Extrae versiones de la salida de 'pip index versions <pkg>'.

    IMPORTANTE:
      - Solo se consideran las versiones tras 'Available versions:'.
      - Se ignoran líneas tipo 'INSTALLED:' o 'LATEST:' para evitar falsos positivos.

    Args:
        output: stdout de pip index versions.

    Returns:
        Lista de versiones encontradas (strings). Si no se encuentra la línea esperada, devuelve [].
    """
    for line in output.splitlines():
        if "Available versions:" in line:
            tail = line.split("Available versions:", 1)[1]
            return re.findall(r"\b\d+(?:\.\d+)+\b", tail)

    return []


def max_version(versions: Iterable[str]) -> str:
    """
    Devuelve la versión máxima (numérica simple) dentro de un iterable.

    Args:
        versions: iterable de versiones

    Returns:
        Versión máxima (string)

    Raises:
        ValueError si no hay versiones o si alguna no es comparable.
    """
    version_list = list(versions)
    if not version_list:
        raise ValueError("No se han encontrado versiones en la salida.")

    comparable = [(v, version_to_tuple(v)) for v in version_list]
    comparable.sort(key=lambda x: x[1])
    return comparable[-1][0]


def ensure_dist_artifacts_exist(project_root: Path, report: DiagnosisReport) -> list[Path]:
    """
    Comprueba existencia de artefactos en dist/ tras build.

    Args:
        project_root: raíz del proyecto
        report: informe

    Returns:
        Lista de ficheros dist/* (si existen).
    """
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        report.add_fail("No existe el directorio dist/ tras el build.")
        return []

    dist_files = list(dist_dir.glob("*"))
    if not dist_files:
        report.add_fail("dist/ está vacío tras el build.")
        return []

    has_whl = any(p.suffix == ".whl" for p in dist_files)
    has_tgz = any(p.name.endswith(".tar.gz") for p in dist_files)

    if not has_whl:
        report.add_fail("No se ha generado ningún .whl en dist/.")
    if not has_tgz:
        report.add_fail("No se ha generado ningún .tar.gz (sdist) en dist/.")

    return dist_files


def wheel_list_paths(project_root: Path, report: DiagnosisReport) -> list[str]:
    """
    Lista los paths del wheel usando 'python -m zipfile -l' y devuelve las líneas de salida.

    Args:
        project_root: raíz del proyecto
        report: informe

    Returns:
        Lista de líneas stdout de zipfile -l, o [] si falla.
    """
    dist_dir = project_root / "dist"
    wheel_files = sorted(dist_dir.glob("*.whl"))
    if not wheel_files:
        report.add_fail("No se encontró ningún wheel (*.whl) en dist/ para inspección.")
        return []

    wheel_path = wheel_files[-1]
    try:
        proc = run_command([sys.executable, "-m", "zipfile", "-l", str(wheel_path)], cwd=project_root)
        return proc.stdout.splitlines()
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"Fallo al listar contenidos del wheel: {exc.stderr.strip() or exc.stdout.strip()}")
        return []


def check_required_wheel_paths(zip_list_lines: list[str], report: DiagnosisReport) -> None:
    """
    Verifica que el wheel contiene rutas críticas.

    Args:
        zip_list_lines: salida de zipfile -l (líneas)
        report: informe
    """
    text = "\n".join(zip_list_lines)
    for required in REQUIRED_WHEEL_PATH_SUBSTRINGS:
        if required not in text:
            report.add_fail(f"El wheel NO contiene la ruta esperada: {required}")


def remove_dir_tree(path: Path) -> None:
    """Borra recursivamente un directorio (sin usar dependencias externas)."""
    if not path.exists():
        return

    # Borrado manual y conservador
    for child in sorted(path.rglob("*"), reverse=True):
        try:
            if child.is_file() or child.is_symlink():
                child.unlink(missing_ok=True)
            elif child.is_dir():
                child.rmdir()
        except OSError:
            # Si algo no se puede borrar, se deja y fallará el venv re-creado; lo reportaremos arriba.
            pass

    try:
        path.rmdir()
    except OSError:
        pass


def main() -> int:
    report = DiagnosisReport()

    # 0.1) Venv esperado activo (FAIL si no)
    if not is_expected_venv_active():
        report.add_fail(
            f"No está activo el venv esperado '{EXPECTED_VENV_DIRNAME}'. "
            f"Actívalo con: source {EXPECTED_VENV_DIRNAME}/bin/activate"
        )
        report.print()
        return report.exit_code()

    report.add_ok(f"Venv esperado activo: {os.environ.get('VIRTUAL_ENV', '')}")

    # 0.2) Comprobar credenciales
    check_pypi_credentials(report)
    if report.has_fail():
        report.print()
        return report.exit_code()


    # 1) Raíz del proyecto
    project_root = find_project_root(Path.cwd())
    if project_root is None:
        report.add_fail("No se encontró la raíz del proyecto (no aparece pyproject.toml en los padres).")
        report.print()
        return report.exit_code()

    report.add_ok(f"Raíz del proyecto detectada: {project_root}")

    # 2) Git status (FAIL/WARN según rutas)
    try:
        proc = run_command(["git", "status", "--porcelain"], cwd=project_root)
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"Fallo ejecutando git status: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()

    changed_paths = parse_git_status_porcelain(proc.stdout)
    if not changed_paths:
        report.add_ok("Repo limpia: git status no detecta cambios.")
    else:
        fatal = [p for p in changed_paths if is_fatal_path(p)]
        warn = [p for p in changed_paths if p not in fatal]

        for p in fatal:
            report.add_fail(f"Cambio fatal detectado (no continuar): {p}")
        for p in warn:
            report.add_warn(f"Cambio fuera de zona fatal (aviso): {p}")

        # Si ya hay FAIL por cambios fatales, paramos aquí (según tu política).
        if report.has_fail():
            report.print()
            return report.exit_code()

    # 3) Versión local desde pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    try:
        local_version = read_local_version_from_pyproject(pyproject_path)
        report.add_ok(f"Versión local (pyproject.toml): {local_version}")
    except (OSError, ValueError) as exc:
        report.add_fail(f"No se pudo leer versión local: {exc}")
        report.print()
        return report.exit_code()

    # 4) Consultar versión máxima en PyPI (FAIL si no se puede o si local <= pypi)
    try:
        proc = run_command([sys.executable, "-m", "pip", "index", "versions", PYPI_PROJECT_NAME], cwd=project_root)
        pypi_versions = parse_pypi_versions_from_pip_index(proc.stdout)
        pypi_latest = max_version(pypi_versions)
        report.add_ok(f"Versión máxima detectada en PyPI para {PYPI_PROJECT_NAME}: {pypi_latest}")

        local_t = version_to_tuple(local_version)
        pypi_t = version_to_tuple(pypi_latest)
        if local_t <= pypi_t:
            report.add_fail(
                f"La versión local ({local_version}) NO es superior a la de PyPI ({pypi_latest}). "
                "PyPI rechazará la subida."
            )
            report.print()
            return report.exit_code()
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"Fallo consultando versiones en PyPI vía pip: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()
    except ValueError as exc:
        report.add_fail(f"No se pudo interpretar la salida de versiones (pip/PyPI): {exc}")
        report.print()
        return report.exit_code()

    # 5) Build (sdist + wheel)
    try:
        proc = run_command([sys.executable, "-m", "build"], cwd=project_root)
        report.add_ok("Build OK: python -m build finalizó correctamente.")
        if proc.stderr.strip():
            # build puede escribir en stderr sin ser error; lo dejamos como WARN por si interesa.
            report.add_warn(f"Salida stderr de build (revisar si procede): {proc.stderr.strip()}")
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"Build FAIL: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()

    dist_files = ensure_dist_artifacts_exist(project_root, report)
    if report.has_fail():
        report.print()
        return report.exit_code()

    report.add_ok(f"Artefactos generados en dist/: {', '.join(p.name for p in dist_files)}")

    # 6) twine check dist/*
    try:
        proc = run_command([sys.executable, "-m", "twine", "check", "dist/*"], cwd=project_root)
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        combined = "\n".join([s for s in (stdout, stderr) if s])
        if combined:
            # Clasificación: cualquier "ERROR" => FAIL; "warning" => WARN
            if re.search(r"\bERROR\b", combined, flags=re.IGNORECASE):
                report.add_fail(f"twine check reporta ERROR:\n{combined}")
                report.print()
                return report.exit_code()

            if re.search(r"\bwarning\b", combined, flags=re.IGNORECASE):
                report.add_warn(f"twine check reporta warning:\n{combined}")
            else:
                report.add_ok("twine check OK: sin errores.")
        else:
            report.add_ok("twine check OK: sin salida relevante.")
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"twine check FAIL: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()

    # 7) Inspección de wheel (zipfile -l)
    zip_lines = wheel_list_paths(project_root, report)
    if report.has_fail():
        report.print()
        return report.exit_code()

    check_required_wheel_paths(zip_lines, report)
    if report.has_fail():
        report.print()
        return report.exit_code()
    report.add_ok("Wheel contiene las rutas críticas esperadas.")

    # 8) Instalación limpia y lectura de versión instalada (metadata)
    remove_dir_tree(CLEAN_VENV_DIR)
    try:
        run_command([sys.executable, "-m", "venv", str(CLEAN_VENV_DIR)], cwd=project_root)
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"No se pudo crear venv limpio en {CLEAN_VENV_DIR}: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()

    clean_python = CLEAN_VENV_DIR / "bin" / "python"
    if not clean_python.exists():
        report.add_fail(f"No existe el intérprete esperado del venv limpio: {clean_python}")
        report.print()
        return report.exit_code()

    dist_dir = project_root / "dist"
    wheel_files = sorted(dist_dir.glob("*.whl"))
    if not wheel_files:
        report.add_fail("No hay wheel en dist/ para instalar en el venv limpio.")
        report.print()
        return report.exit_code()

    wheel_path = wheel_files[-1]

    try:
        run_command([str(clean_python), "-m", "pip", "install", "-U", "pip"], cwd=project_root)
        run_command([str(clean_python), "-m", "pip", "install", str(wheel_path)], cwd=project_root)
        proc = run_command(
            [
                str(clean_python),
                "-c",
                "import importlib.metadata as m; print(m.version('help-core-pygame'))",
            ],
            cwd=project_root,
        )
        installed_version = proc.stdout.strip()
        report.add_ok(f"Versión instalada (metadata) en venv limpio: {installed_version}")

        if installed_version != local_version:
            report.add_fail(
                f"La versión instalada ({installed_version}) NO coincide con pyproject.toml ({local_version})."
            )
            report.print()
            return report.exit_code()

        report.add_ok("Instalación limpia OK y versión coincide con pyproject.toml.")
    except subprocess.CalledProcessError as exc:
        report.add_fail(f"Fallo en instalación limpia o lectura de versión: {exc.stderr.strip() or exc.stdout.strip()}")
        report.print()
        return report.exit_code()

    report.print()

    input("PULSE <Intro> para terminar")
    Chuleta="""

CHULETA (Si todo es OK, para subir a PyPI faltaría hacer lo siguiente:)
=======================================================================

1) Limpiar artefactos antiguos (evitar confusiones) 
    Comando: rm -rf dist/ build/ *.egg-info 

2) Reconstruir sdist + wheel (artefactos definitivos) 
    Comando: python3 -m build 

3) Validar antes de subir a PyPI 
    Comando: python3 -m twine check dist/* 

4) Subir a PyPI (credenciales en ~/.pypirc) 
    Comando: python3 -m twine upload dist/* 

5) Verificar en PyPI que aparece la nueva versión 
    Acción: abre la página del proyecto y confirma que “Latest version” es la nueva y que el README

"""
    print(Chuleta)
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())

