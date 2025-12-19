#!/usr/bin/python3
"""
Programa asistido por ChatGPT en fecha 18/Dec/2025 y hora 00:00
Titulo: Diagnóstico de assets empaquetados en help_core_pygame
Descripción: Comprueba si un asset existe dentro del paquete instalado, muestra
             desde qué Python/entorno se está ejecutando y devuelve códigos
             de salida útiles para automatización.
"""

from __future__ import annotations

from importlib import metadata, resources
from pathlib import Path
import sys


def safe_list_dir(traversable_dir) -> list[str]:
    """Lista nombres de un directorio Traversable sin fallar."""
    try:
        if not traversable_dir.exists() or not traversable_dir.is_dir():
            return []
        return sorted(item.name for item in traversable_dir.iterdir())
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO: No se pudo listar directorio: {type(exc).__name__}: {exc}")
        return []


def print_runtime_context(package_name: str) -> None:
    """Imprime datos del intérprete y del paquete instalado."""
    print("Python executable:", sys.executable)
    print("Python version   :", sys.version.split()[0])

    try:
        pkg_version = metadata.version("help-core-pygame")
        print("Package version :", pkg_version)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO: No se pudo leer versión del paquete: {type(exc).__name__}: {exc}")

    try:
        imported_pkg = __import__(package_name)
        pkg_file = getattr(imported_pkg, "__file__", "(desconocido)")
        print("Package __file__:", pkg_file)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO: No se pudo importar {package_name}: {type(exc).__name__}: {exc}")


def main() -> int:
    package_name = "help_core_pygame"
    asset_relpath = "assets/mp3/beep_scroll.mp3"
    assets_dir_relpath = "assets/mp3"

    print_runtime_context(package_name)
    print()

    try:
        package_root = resources.files(package_name)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: No se puede acceder a resources.files('{package_name}'): {type(exc).__name__}: {exc}")
        return 2

    asset_entry = package_root.joinpath(asset_relpath)

    print(f"Paquete: {package_name}")
    print(f"Recurso: {asset_relpath}")
    print(f"exists(): {asset_entry.exists()}")
    print(f"is_file(): {asset_entry.is_file()}")

    assets_dir = package_root.joinpath(assets_dir_relpath)
    names = safe_list_dir(assets_dir)
    print(f"Contenido de {assets_dir_relpath}:", names if names else "(vacío o no existe)")

    # Informativo: intentar obtener ruta física.
    try:
        with resources.as_file(package_root) as root_path:
            root_path = Path(root_path)
            print("Ruta física del paquete (si aplica):", root_path)
            print("Existe en disco esa ruta del recurso:", (root_path / asset_relpath).exists())
    except Exception as exc:  # noqa: BLE001
        print(f"Nota: no se pudo obtener ruta física con as_file(): {type(exc).__name__}: {exc}")

    print("\nSugerencia manual (shell):")
    print("  python -m pip show -f help-core-pygame | sed -n '/Files:/,$p' | grep -i beep_scroll")

    # Código de salida útil:
    # 0 = OK (asset existe en el paquete)
    # 1 = KO (asset no está)
    return 0 if asset_entry.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())

