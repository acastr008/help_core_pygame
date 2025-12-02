TUTORIAL: Crear y publicar una librería en PyPI
===============================================

Ejemplo completo con **help_core_pygame**


# 1. Introducción

Este tutorial nació mientras creaba por primera vez una librería propia para publicarla en PyPI y poder instalarla con `pip` como cualquier otra librería externa.

El ejemplo real que vamos a usar es:

- Librería: `help_core_pygame`
- Función: sistema de ayudas y overlays de ayuda contextual para programas hechos con Pygame, donde los textos de ayuda están en Markdown.

Además de explicar los pasos genéricos, veremos cómo se aplican a un caso real usando dos entornos:

- `pyenv_goliat` → entorno grande que se usa para muchos proyectos distintos (uso diario / producción).
- `pyenv_dev_help` → entorno específico para desarrollar y probar la librería `help_core_pygame` antes de publicarla en PyPI.

La idea final es tener:

- En `pyenv_dev_help` → la librería en modo editable (`pip install -e .`) para desarrollarla.
- En `pyenv_goliat` → la versión estable desde PyPI (`pip install help-core-pygame`) para usarla como cualquier otra dependencia.


## 1.1. Objetivo del tutorial

El objetivo completo del tutorial es:

1. Crear una estructura de proyecto clara (con `src/`, `examples/`, `docs/`, etc.).
2. Configurar correctamente `pyproject.toml`.
3. Crear y usar un entorno virtual de desarrollo (`pyenv_dev_help`) con la librería instalada en modo editable.
4. Construir el paquete (sdist + wheel) con `python -m build`.
5. Publicar la librería en PyPI con `twine`.
6. Instalarla y usarla desde otro entorno (por ejemplo `pyenv_goliat`) como usuario final.

En esta guía todo se muestra usando `help_core_pygame` como ejemplo concreto.


# 2. Conceptos básicos que necesitamos

Antes de liarnos con comandos, aclaramos cuatro ideas: paquete, proyecto instalable, layout `src/` y entornos virtuales.


## 2.1. Paquete y proyecto instalable

- Un módulo es un archivo `.py`, por ejemplo `help_core.py`.
- Un paquete es un directorio con un `__init__.py` dentro, por ejemplo:

  ```text
  src/
    help_core_pygame/
      __init__.py
      help_core.py
  ```

- Un proyecto instalable es un conjunto de ficheros (código + metadatos) que se puede instalar con `pip`.
  Lo describimos con `pyproject.toml`.

Cuando alguien hace:

```bash
pip install help-core-pygame
```

lo que se instala es el proyecto con ese nombre en PyPI, que contiene el paquete `help_core_pygame` que luego importas en Python:

```python
from help_core_pygame import open_help_standalone, HelpConfig, HelpViewer
```


## 2.2. PyPI, pip y nombres con guiones y guiones bajos

- El nombre del proyecto en PyPI suele llevar guiones:

  ```toml
  [project]
  name = "help-core-pygame"
  ```

  Esto es lo que se usa con `pip`:

  ```bash
  pip install help-core-pygame
  ```

- El nombre del paquete importable en Python usa guiones bajos:

  ```python
  import help_core_pygame
  ```

Por eso:

- Proyecto → "help-core-pygame" (PyPI / `pip`).
- Paquete → `help_core_pygame` (import en Python).


## 2.3. Layout `src/` (estructura recomendada)

Usaremos el layout moderno con carpeta `src/`:

```text
help_core_pygame/
├── src/
│   └── help_core_pygame/
│       ├── __init__.py
│       └── help_core.py
└── pyproject.toml
```

Ventajas:

- Evita muchos problemas de import cuando se mezcla código del proyecto y código instalado.
- Obliga a pasar por la instalación (real o editable), lo que se parece más a cómo usará la librería otra gente.
- Es el patrón recomendado para proyectos nuevos.


## 2.4. Entornos virtuales: desarrollo vs global

Distinguimos dos tipos de entornos virtuales:

1. Entorno global multiuso (`pyenv_goliat`)
   - Se usa para muchos proyectos diferentes.
   - Aquí se instala la versión estable desde PyPI:
     ```bash
     source /home/antonio/pyenv_goliat/bin/activate
     python -m pip install help-core-pygame
     ```

2. Entorno específico de desarrollo (`pyenv_dev_help`)
   - Se usa solo para desarrollar y probar `help_core_pygame`.
   - Aquí se instala la librería en modo editable:
     ```bash
     python -m pip install -e .
     ```

Regla práctica importante:

> No desarrolles una librería en el mismo entorno donde ejecutas tus proyectos normales.
> Crea un entorno de desarrollo aparte para esa librería.


# 3. Crear la estructura inicial del proyecto

Partimos de un directorio raíz para el proyecto, por ejemplo:

```text
help_core_pygame/
```

Una estructura razonable podría ser:

```text
help_core_pygame/
├── src/                     # Código de la librería
│   └── help_core_pygame/
│       ├── __init__.py
│       ├── help_core.py
│       └── assets/
│           └── mp3/
│               └── beep_scroll.mp3
├── examples/                # Scripts de ejemplo / demos
│   ├── demo_help_overlay_beep.py
│   └── demo_help_standalone.py
├── docs/                    # Documentación de la librería
│   ├── help_core_api_uso.md
│   ├── help_core_chuleta_rapida.md
│   └── help_core_doc_actualizado.md
├── tests/                   # (Opcional) Pruebas automáticas
│   └── test_basic.py
├── README_ES.md             # README en castellano
├── README_EN.md             # README en inglés (opcional)
├── LICENSE.md               # Licencia (por ejemplo MIT)
├── TASKS.md                 # Lista de tareas / TODO (opcional)
└── pyproject.toml           # Configuración del paquete
```

Para empezar, lo mínimo que necesitamos es:

```text
help_core_pygame/
├── src/
│   └── help_core_pygame/
│       ├── __init__.py
│       └── help_core.py
└── pyproject.toml
```


## 3.1. Crear la carpeta del paquete

Desde la raíz del proyecto:

```bash
mkdir -p src/help_core_pygame
```

Dentro de `src/help_core_pygame/` creamos los ficheros mínimos.


### 3.1.1. `src/help_core_pygame/__init__.py`

```python
# Paquete principal de la librería help_core_pygame.
# Aquí exponemos la API pública que queremos que usen los usuarios.

from .help_core import open_help_standalone, HelpConfig, HelpViewer

__all__ = ["open_help_standalone", "HelpConfig", "HelpViewer"]
```


### 3.1.2. `src/help_core_pygame/help_core.py` (versión mínima)

```python
from dataclasses import dataclass


@dataclass
class HelpConfig:
    # Configuración básica de la ayuda
    title: str = "Ayuda"
    width: int = 800
    height: int = 600


class HelpViewer:
    # Visor de ayuda principal (integrable en programas con Pygame)

    def __init__(self, config: HelpConfig | None = None):
        self.config = config or HelpConfig()

    def open(self):
        # Aquí irá la lógica real de abrir la ayuda usando Pygame
        print(f"Abrir ayuda: {self.config.title!r} ({self.config.width}x{self.config.height})")


def open_help_standalone():
    # Ejemplo de punto de entrada sencillo
    viewer = HelpViewer()
    viewer.open()
```

Más adelante puedes sustituir este código de ejemplo por tu implementación real.


## 3.2. Crear la carpeta de ejemplos

En la raíz del proyecto:

```bash
mkdir -p examples
```

Ejemplo de demo mínima:

`examples/demo_help_standalone.py`:

```python
from help_core_pygame import open_help_standalone

if __name__ == "__main__":
    open_help_standalone()
```

Si esto funciona (una vez instalada la librería en el entorno correspondiente), significa que el paquete está bien estructurado e importable.


# 4. Configurar `pyproject.toml`

`pyproject.toml` es el fichero donde declaramos:

- Qué backend de construcción usamos (`setuptools`).
- El nombre del proyecto, versión, descripción, dependencias, etc.

En la raíz de `help_core_pygame/`, crea `pyproject.toml` con un contenido similar a este:


```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "help-core-pygame"         # Nombre en PyPI (pip install help-core-pygame)
version = "0.1.0"
description = "Módulo de ayuda para overlays y ayuda contextual en Pygame"
readme = "README_ES.md"
requires-python = ">=3.9"
authors = [
  { name = "Antonio Castro Snurmacher", email = "acastro0841@gmail.com" },
]
license = "MIT"
dependencies = [
  "pygame>=2.0"
]

keywords = ["pygame", "help", "overlay", "games", "ayuda"]

classifiers = [
  "Programming Language :: Python :: 3",
  "Operating System :: OS Independent",
  "Topic :: Games/Entertainment",
]

[project.urls]
Homepage = "https://github.com/acastr008/help_core_pygame"
Source   = "https://github.com/acastr008/help_core_pygame"
Issues   = "https://github.com/acastr008/help_core_pygame/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"help_core_pygame" = ["assets/*.mp3"]
```


## 4.1. Qué significa cada sección

- `[build-system]`
  - Indica que usas `setuptools` como backend de construcción.
  - Permite que `python -m build` funcione.

- `[project]`
  - `name` → nombre del proyecto en PyPI (`pip install help-core-pygame`).
  - `version` → versión de la librería (`0.1.0`, `0.1.1`, etc.).
  - `description` → descripción corta.
  - `readme` → fichero que se muestra en PyPI (puede ser `README.md`, `README_ES.md`, etc.).
  - `requires-python` → versiones mínimas de Python soportadas.
  - `authors` → autores del proyecto.
  - `license` → tipo de licencia (p.ej. `MIT`).
  - `dependencies` → librerías externas que necesita tu paquete (p.ej. `pygame`).

- `[project.urls]`
  - Enlaces útiles: página principal, código fuente, issues.

- `[tool.setuptools.packages.find]`
  - Indica que busque los paquetes dentro de `src/`.
  - Detectará automáticamente `src/help_core_pygame`.

- `[tool.setuptools.package-data]`
  - Archivos no `.py` que deben incluirse en la instalación.
  - En este ejemplo, todos los `assets/*.mp3` dentro del paquete `help_core_pygame`.

Con esto, tu proyecto ya es teóricamente instalable.


# 5. Entorno de desarrollo y modo editable

Ahora vamos a crear el entorno de desarrollo `pyenv_dev_help` e instalar la librería en modo editable.


## 5.1. Crear y activar el entorno de desarrollo

Desde la raíz del proyecto (`help_core_pygame/`):

```bash
python -m venv pyenv_dev_help
source pyenv_dev_help/bin/activate
```

Si al crear el entorno ves un error tipo:

> The virtual environment was not created successfully because ensurepip is not available.
> On Debian/Ubuntu systems, you need to install the python3-venv package.

La solución típica en Debian/Ubuntu, fuera de cualquier venv, es:

```bash
sudo apt install python3.12-venv
```

Después vuelves a:

```bash
cd /ruta/a/help_core_pygame
python -m venv pyenv_dev_help
source pyenv_dev_help/bin/activate
```


## 5.2. Instalar dependencias y la librería en modo editable

Con `pyenv_dev_help` activo (deberías ver el prefijo `(pyenv_dev_help)` en tu prompt):

1. Instalar dependencias (por ahora `pygame`):

   ```bash
   python -m pip install --upgrade pip
   python -m pip install pygame
   ```

2. Instalar la librería en modo editable:

   ```bash
   python -m pip install -e .
   ```

Esto hace que:

- El entorno `pyenv_dev_help` crea que tiene instalado `help-core-pygame`.
- Pero en lugar de copiar archivos, crea un enlace hacia `src/help_core_pygame`.
- Cualquier cambio que hagas en el código se refleja inmediatamente.


## 5.3. Probar el import en el entorno de desarrollo

Con `pyenv_dev_help` activo:

```bash
python - << 'EOF'
from help_core_pygame import open_help_standalone, HelpConfig, HelpViewer

print("open_help_standalone:", open_help_standalone)
print("HelpConfig:", HelpConfig)
print("HelpViewer:", HelpViewer)
EOF
```

Si esto no da error y ves funciones y clases, entonces:

- `help_core_pygame` se importa correctamente.
- La API pública está bien expuesta desde `__init__.py`.


## 5.4. Ejecutar las demos desde el entorno de desarrollo

En `pyenv_dev_help`:

```bash
python examples/demo_help_standalone.py
```

Si la demo funciona usando `from help_core_pygame import ...`, significa que el layout `src/` y la instalación editable están correctos.


## 5.5. Problemas frecuentes en el entorno de desarrollo

- Error: `ModuleNotFoundError: No module named 'help_core_pygame'`
  - Comprueba el entorno:

    ```bash
    python - << 'EOF'
import sys, os
print("Python usado :", sys.executable)
print("VIRTUAL_ENV  :", os.environ.get("VIRTUAL_ENV"))
EOF
    ```

  - Asegúrate de haber hecho `python -m pip install -e .` en ese entorno.

- `pip` y `python` apuntan a sitios diferentes
  - Usa siempre `python -m pip ...` dentro de la venv.
  - Evita `pip` a secas si tienes alias o varios entornos.

- Entornos mezclados (editable + no editable)
  - Si sospechas mezcla:

    ```bash
    python -m pip uninstall help-core-pygame -y
    python -m pip uninstall help_core_pygame -y
    python -m pip install -e .
    ```

## 5.6. Después de todo esto lo ideal es subir la librería a PyPI y los pasos recomendables son:

- Crear cuenta en PyPI 
  - Web: pypi.org → Register.

- (Opcional pero muy recomendable) Crear cuenta en TestPyPI
  - Web: test.pypi.org → Register.

- Crear un API token en PyPI
  - En tu cuenta de PyPI → “Account settings” → “API tokens”.
  - Crea un token para este proyecto (por ejemplo help_core_pygame_token).
  - Copia el token y guárdalo en un sitio seguro.

- (Opcional) Crear un API token en TestPyPI
  - Misma idea pero en test.pypi.org.

- Instalar las herramientas en tu entorno de desarrollo (pyenv_dev_help)

## 5.7. ¿Que es TestPyPI?
 
- TestPyPI es una instancia separada del Python Package Index (PyPI), que es el repositorio oficial de paquetes de Python.
- Su principal propósito es servir como un entorno de prueba para los desarrolladores de paquetes de Python.
- 🔑 Propósito de TestPyPI:
  - Probar el Proceso de Distribución: Te permite practicar y verificar que tu proceso de empaquetado y subida (utilizando herramientas como twine y wheel) funciona correctamente antes de lanzarlo al repositorio principal de PyPI.
  - Experimentación Segura: Puedes experimentar con tu paquete, probar la instalación y asegurarte de que la metadata es correcta sin afectar ni contaminar el índice real de PyPI. Es ideal para la primera vez que subes un paquete o para probar actualizaciones significativas.
  - Pruebas de Instalación: Los usuarios pueden descargar e instalar tus paquetes desde TestPyPI usando un índice URL específico (por ejemplo, con pip install --index-url https://test.pypi.org/simple/ <nombre_paquete>) para confirmar que la instalación es exitosa.

**Es muy recomendable usarlo y nosotros lo incluiremos en nuestra lista de tareas.**

# 6. Construir el paquete (sdist + wheel) y 

El siguiente paso es construir el paquete distribuible con `python -m build`.

Con `pyenv_dev_help` activo y desde la raíz del proyecto:


## 6.1. Instalar la herramienta `build`

```bash
source pyenv_dev_help/bin/activate
python -m pip install --upgrade pip
python -m pip install build
```


## 6.2. Limpiar directorios antiguos (opcional)

```bash
rm -rf dist build ./*.egg-info src/*.egg-info
```

Si quieres ir con cuidado, puedes empezar borrando solo `dist` y `build`:

```bash
rm -rf dist build
```


## 6.3. Ejecutar la construcción

```bash
python -m build
```

Esto generará:

- Un sdist: `dist/help-core-pygame-0.1.0.tar.gz`
- Un wheel: `dist/help_core_pygame-0.1.0-py3-none-any.whl`

Comprueba:

```bash
ls dist
```


## 6.4. Probar el wheel en un entorno limpio (opcional)

```bash
python -m venv /tmp/venv_test_help
source /tmp/venv_test_help/bin/activate

python -m pip install --upgrade pip
python -m pip install dist/help_core_pygame-0.1.0-py3-none-any.whl
```

Prueba el import:

```bash
python - << 'EOF'
from help_core_pygame import open_help_standalone
print("IMPORT OK:", open_help_standalone)
EOF
```


# 7. Publicar en PyPI (y TestPyPI)

Usaremos `twine` para subir los paquetes.


## 7.1. Instalar `twine`

En `pyenv_dev_help`:

```bash
python -m pip install --upgrade twine
```


## 7.2. Crear cuenta y token

Pasos generales:

1. Crear cuenta en PyPI: https://pypi.org/account/register/
2. (Opcional) Crear cuenta en TestPyPI: https://test.pypi.org/account/register/
3. Crear un API token en tu cuenta de PyPI:
   - Account settings → API tokens.
   - Copiar el token (empieza por algo tipo `pypi-...`).


## 7.3. Subir a TestPyPI (opcional)

```bash
python -m twine upload   --repository-url https://test.pypi.org/legacy/   dist/*
```

En el prompt de credenciales:

- `username`: `__token__`
- `password`: tu API token de TestPyPI.


## 7.4. Subir al PyPI real

```bash
python -m twine upload dist/*
```

Igual:

- `username`: `__token__`
- `password`: tu API token de PyPI.

Si vuelves a subir una versión nueva, recuerda cambiar el campo `version` en `pyproject.toml` antes de construir y subir.


# 8. Usar la librería desde otro entorno (pyenv_goliat)

Ahora pasamos al uso como usuario final.


## 8.1. Activar el entorno global y limpiar restos

```bash
source /home/antonio/pyenv_goliat/bin/activate

python -m pip uninstall help-core-pygame -y
python -m pip uninstall help_core_pygame -y
```


## 8.2. Instalar desde PyPI

```bash
python -m pip install --upgrade pip
python -m pip install help-core-pygame
```

Comprueba:

```bash
python -m pip show help-core-pygame
```


## 8.3. Probar import y uso básico

```bash
python - << 'EOF'
from help_core_pygame import open_help_standalone
print("open_help_standalone:", open_help_standalone)
EOF
```

O crea un script sencillo en otra carpeta:

```python
# test_uso_help_core.py
from help_core_pygame import open_help_standalone

if __name__ == "__main__":
    open_help_standalone()
```

Y ejecútalo:

```bash
python test_uso_help_core.py
```


# 9. Problemas frecuentes de publicación


## 9.1. Error “File already exists” al subir con twine

Significa que ya subiste esa versión (`version` en `pyproject.toml`).

Solución:

1. Incrementa `version` (por ejemplo `0.1.0` → `0.1.1`).
2. Limpia y reconstruye:

   ```bash
   rm -rf dist build ./*.egg-info src/*.egg-info
   python -m build
   ```

3. Sube de nuevo con `twine upload dist/*`.


## 9.2. Problemas de credenciales con twine

Asegúrate de usar:

- `username`: `__token__`
- `password`: el API token completo.

Si usas `.pypirc`, revisa que las entradas `pypi` y/o `testpypi` estén correctamente configuradas.


## 9.3. Funciona en el entorno de desarrollo pero no en el global

La causa más habitual: estás en otro entorno que no tiene la librería instalada.

Comprueba:

```bash
python - << 'EOF'
import sys, os
print("Python usado :", sys.executable)
print("VIRTUAL_ENV  :", os.environ.get("VIRTUAL_ENV"))
EOF
```

Y reinstala si hace falta:

```bash
python -m pip uninstall help-core-pygame -y
python -m pip uninstall help_core_pygame -y
python -m pip install help-core-pygame
```


## 9.4. Assets que no se instalan (mp3, imágenes…)

Comprueba:

1. Que los assets están dentro del paquete, por ejemplo:

   ```text
   src/help_core_pygame/assets/mp3/beep_scroll.mp3
   ```

2. Que `pyproject.toml` contiene:

   ```toml
   [tool.setuptools.package-data]
   "help_core_pygame" = ["assets/*.mp3"]
   ```

3. Que has reconstruido y subido una versión nueva.


## 9.5. Script de depuración rápido

Un script simple te puede ahorrar tiempo:

```python
# debug_help_env.py
import sys
import os

print("Python executable :", sys.executable)
print("Python version    :", sys.version.split()[0])
print("VIRTUAL_ENV       :", os.environ.get("VIRTUAL_ENV"))
print()

try:
    import help_core_pygame
    print("help_core_pygame import OK")
    print("help_core_pygame.__file__:", help_core_pygame.__file__)
except Exception as e:
    print("Error importando help_core_pygame:", repr(e))
```


# 10. Resumen del flujo de trabajo

## 10.1. Modo autor (desarrollo de la librería)

1. Entrar al proyecto:

   ```bash
   cd ~/Escritorio/PROYECTOS_PROGR_ACTIVOS/CODEX/help_core_pygame
   ```

2. Activar entorno de desarrollo:

   ```bash
   source pyenv_dev_help/bin/activate
   ```

3. Confirmar que es el Python correcto:

   ```bash
   python -c "import sys; print(sys.executable)"
   ```

4. Instalar en modo editable (primera vez o tras cambios fuertes):

   ```bash
   python -m pip install -e .
   ```

5. Trabajar en `src/`, `examples/`, `docs/` y probar con:

   ```bash
   python examples/demo_help_standalone.py
   ```

6. Para sacar una versión nueva:

   - Actualizar `version` en `pyproject.toml`.
   - Ejecutar `python -m build`.
   - Ejecutar `python -m twine upload dist/*`.


## 10.2. Modo usuario (usar la librería en otros proyectos)

1. Activar el entorno global:

   ```bash
   source /home/antonio/pyenv_goliat/bin/activate
   ```

2. Instalar o actualizar la librería:

   ```bash
   python -m pip install --upgrade help-core-pygame
   ```

3. Usarla en otros proyectos:

   ```python
   from help_core_pygame import HelpViewer, HelpConfig, open_help_standalone
   ```

Si algo falla, usar el script de depuración y comprobar `sys.executable`, `VIRTUAL_ENV` y `pip show help-core-pygame`.


---

Con esto tienes el tutorial completo en un único texto, listo para guardar como markdown y adaptar a tus necesidades.
