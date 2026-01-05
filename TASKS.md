# Tareas pendientes

- Continuar con form_core_pygame para terminar pasándola a PyPI
  
  - 


# Mejoras pendientes a más largo plazo

- Ampliar el parser del sistema de ayuda para detectar y representar tablas.
- Ampliar el parser del sistema de ayuda para detectar y representar Links con acceso a web. y link con acceso a cabeceras .

# Tareas ya realizadas por orden cronológico

- (5-ene-2026) Dos cambios en el [project] del fichero pyproject.toml

  - version = "0.1.2"       # Preparado ya para la próxima versión
  - authors = [ { name = "Antonio Castro Snurmacher", email = "acastro0841@gmail.com" }, ]  # Corrección errata


- (22-dic-2025)

  - Subir la version [0.1.1] a TestPyPI y a PyPI

- (19-dic-2025)
  
  - Se corrigió la forma en que el programa localiza los archivos de recursos internos (assets). para garantizar que el audio se cargue correctamente, tanto si el módulo se ejecuta desde un entorno de desarrollo como si se accede al paquete en PyPI.
  - Se ha incuido un directorio tools y en él tenemos diagnose_help_core_pygame_assets_v2.py
  - (Externamente al proyecto se han realizado pruebas en Escritorio/PRUEBAS y se ha corregido y ampliado el documento ~/Escritorio/PROYECTOS_PROGR_ACTIVOS/CODEX/TUTORIALES/Como_crear_y_subir_liberias_a _PyPI)

- (15-dic-2025)
  
  - Se ha pasado README_EN.md a README.md y se ha incluido un link en él 
    [Spanish README_ES.md is available](https://github.com/acastr008/help_core_pygame/blob/main/README_ES.md) 

- (3-dic-2025) 
  
  - Se ha subido la librería a TestPyPI
  - Se ha comprobado que funciona todo correctamente.
  - Creamos un documento temporal Lo_que_estoy_haciendo_ahora.txt
  - queda pendiente pasar lo de ese documento al documento help_core_pygame_tutorial_inacabado.md

- (2-dic-2025) 'cambios en help_core_pygame_tutorial.md y en debug_py_projet.py, Creo repositorio en GitHub y lo subo)
  
  - Creo el proyecto en GitHub
  - Hago cambios en help_core_pygame_tutorial.md
  - Hago algunas mejoras a debug_py_projet.py

- (2-dic-2025) "Versión inicial (fecha: 2-dic-2025)"
  
  - Hago cambios en help_core_pygame_tutorial.md

- (1-dic-2025)
  
  - Consigo tener una librería clara: help_core_pygame
  - Paquete en src/help_core_pygame/
  - API pública: open_help_standalone, HelpConfig, HelpViewer, etc.
  - Estructura de proyecto razonable y moderna con layout src/ y pyproject.toml.
  - Dos entornos bien diferenciados:
    - pyenv_dev_help → para desarrollo de la librería.
    - pyenv_goliat → tu entorno “general” para usar librerías (entre ellas, en el futuro, help-core-pygame desde PyPI).
  - He generado un tutorial en Markdown + script Python que lo reconstruye cuando quieras.

- (30-nov-2025)
  
  - Se ha perdido la librería ePyPI y la librería editable en local. Abandono el uso de Gemini y paso a ChatGpt.

- (28-nov-2025) 
  
  - Se ha creado pyproyect.toml y la librería pip.
  - Se han creado los README ES/EN) y se ha reestructurado el proyecto.
  - Se ha proporcionado AI_GUIDE.md, LICENSE.md, ARCHITECTURE y AI_EXCLUDE

- (27-nov-2025) Se ha creado pyproyect.toml y se crea la librería pip

- (26-nov-2025)
  
  - Se han vuelto a crear los README ES/EN) y se ha reestructurado el proyecto.

# Tareas fallidas o descartadas por orden cronológico

- (29-nov-2025)
  - Se ha subido la librería a PyPI.
  - Se continua trabajando en el tutorial.
  - SURGEN PROBLEMAS COMPLICADOS 
