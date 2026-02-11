# Tareas pendientes

- () Se han estandarizado las cabeceras de las librerías help_core_pygame/src/*.py

- Continuar con form_core_pygame para terminar pasándola a PyPI

- - commit -m 'Iniciando cambios para la futura versión v0.1.2'

# Tareas ya realizadas por orden cronológico

- (9-feb-2026) Repaso final a toda la documentación.
  
  - README_es.md y README.md
  - Crear índice general INDEX_es.md 
  - Retocar navegación de todos los documentos *_es.md añadiendo enlace al índice general. 
  - Crear las versiones de toda la documentacion en Inles *_en.md

- (8-feb-2026) Creamos los documentos OVERVIEW_es.md y MINIMARKDOWN_GUIDE_es.md

- (7-feb-2026) Creado el lanzador main.py. Hemos modificado las cabeceras de las demos.

- (6-feb-2026) Finalizado docs/API_REFERENC_es.md (con índice, con imagen, depurada)

- (5-feb-2026) Visualizador MarkDown + README de ejemplos
  
  - Desarrollo de examples/view_markdown_help_core.py para visualizar ficheros MarkDown
  
  - Crear examples/README_es.md

- (2-feb-2026 20:00) Se ha implementado la sección de tablas y ha quedado razonamblemente bie. Se ha incuido en la demo demo_mini_MarkDown_TEST.py

- (2-feb-2026) Se ha completado la demo_mini_MarkDown_TEST.py con la mejora de la sección de imágenes.
  
  - También se ha corregido un pequeño bug del parser para imágenes. (ya no exige separar un párrajo de una imagen con una línea en blanco)

- (1-feb-2026)  Varias pequeñas mejoras:
  
  - Corrección Bug visualizacion barra hr (quedaba corta) y aumento de grosor (de 1 a 3).
  - Mejorar ExitStack en varias demos.
  - Reordenación y mejoras en demo_mini_MarkDown_TEST.py

- (30-ene-2026) Ampliación: Soporte para imágenes. Funciona aunque admite pequeños retoques.

- (29-ene-2026 AM) Ampliación: Ahora hay soporte parcial para comentarios HTML dentro del texto MarkDown.

- (28-ene-2026) Se ha refactorizado. help_core.py  help_mini_markdown.py  help_viewer_impl.py  __init__.py

- (27-ene-2025) Amplición de soporte MarkDown para Links con acceso a web. links con acceso a cabeceras y a links con aceso anclas HTML tipo <a id="etiqueta"></a> .
  
  - Ampliamos el texto de prueba de la de examples/demo_help_standalone.py para poder probar nuevas funcionalidaddes MarkDown.
  - Ampliación del parser y del visualizador en src/help_core_pygame/help_core.py
  - Hemos mejorado src/help_core_pygame/__init__.py

- (25-ene-2026) Iniciando cambios para la futura versión v0.1.2
  
  - (25-ene) En src/help_core_pygame/help_core.py añado la función de conveniencia  ShowHelpOverlay()   
  - (25-ene) Añado una demo examples/demo_help_show_overlay_circles.py 
  - (24-ene) En .gitignore añado PRIVATE/  
  - (5-ene) Dos cambios en el [project] del fichero pyproject.toml
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
