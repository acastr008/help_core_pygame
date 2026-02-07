# Ejecutar con: python3 main.py
# Lanzador de demos para help_core_pygame. 
"""

El programa main.py es un lanzador de demos. Las busca resusivamente desde el directorios /examples/ y espera encontrar 
una línea dentro de las nueve primeras líneas del fichero con: "Descripción breve:" Seguida de la descripción.
(La expresión para 'Descripción breve admite cierta flexibilidad. vease: _DESC_PATTERN )
Solo incluirá ficheros '*.py' que tengan una línea 'Descripción breve:' cerca del inicio.
Ignorará una serie de directorios tales como SEG/","SEG_", "OLD/",  "OLD_", "VERS/", "VERS_" reservados para
almacenar demos temporales de prueba, copias de seguridad, demos obsoletas que ya no funcionan, etc. 
Las demos localizadas se listará y podrán ser lanzadas.

TIPOS DE RECURSOS:
    * Recursos compartidos (styles/, fonts/): siguen en la raíz del repo; las demos los referencian por ruta 
      absoluta (helper).
    * Recursos propios de la demo: viven dentro de la carpeta de la demo; se acceden vía Path(__file__).parent.
"""


import os
import sys
import time
import re
import pygame
from pathlib import Path

# --------------------------- Configuración ---------------------------
WINDOW_W, WINDOW_H = 1200, 950
PADDING = 20
BUTTON_H = 64
BUTTON_GAP = 10
FONT_SIZE = 22
DETAIL_FONT_SIZE = 24
TITLE = f"            LANZADOR DE EJEMPLOS PARA HELP-CORE-PYGAME  ({os.path.basename(os.getcwd())}/{(os.path.basename(sys.argv[0]))})"
DEMOS_DIR = "examples"


# Lista de prefijos de ruta (portables, con "/") que se consideran válidos.
# - Si está vacía, no filtra por ruta (solo por .py + "Descripción breve").
# - Se evalúa contra el path relativo desde la raíz del proyecto (p.ej. "examples/foo/bar.py").
PATH_INCLUDE = ["examples/"]
BG = (18, 18, 22)
PANEL = (28, 28, 34)
BTN = (46, 46, 56)
BTN_HOVER = (66, 66, 82)
TEXT = (235, 235, 235)
SUBTLE = (180, 180, 190)

SCROLL_SPEED = 60  # píxeles por rueda
# -------------------------------------------------------------------

MESES_ES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

def format_date_es(ts):
    """Devuelve fecha como dd-mmm-aaaa con meses en ES minúscula."""
    t = time.localtime(ts)
    dd = f"{t.tm_mday:02d}"
    mmm = MESES_ES[t.tm_mon - 1]
    yyyy = f"{t.tm_year:04d}"
    return f"{dd}-{mmm}-{yyyy}"

def is_valid_dir(name):
    return not name.startswith(".") and name != "__pycache__"


def _to_posix_relpath(path, start_dir):
    """Convierte una ruta a relativa portable con '/'."""
    rel = os.path.relpath(path, start_dir)
    return rel.replace(os.sep, "/")


def _path_is_included(rel_from_project):
    """Devuelve True si rel_from_project empieza por alguno de los prefijos de PATH_INCLUDE.

    - Si PATH_INCLUDE está vacío, no se aplica filtro.
    - Se espera rel_from_project con separadores '/'.
    """
    if not PATH_INCLUDE:
        return True
    for prefix in PATH_INCLUDE:
        if rel_from_project.startswith(prefix):
            return True
    return False


def is_valid_file(name):
    # Solo aceptamos ficheros Python
    return name.endswith('.py')


_DESC_PATTERN = re.compile(r"Descripci[oó]n\s+breve\s*:\s*(.*)", re.IGNORECASE)

_ORDER_PATTERN = re.compile(
    r"Orden\s+tutorial\s*:\s*(\d+)\s*\.\s*(\d+)",
    re.IGNORECASE,
)
# NOTA: Se aceptan variantes como "Orden tutorial: 01.02" o "Orden tutorial: 1.2".


def extract_tutorial_order(path):
    """Extrae 'Orden tutorial: nn.nn' del encabezado del fichero.

    Se espera encontrarlo cerca del inicio del archivo, justo debajo del bloque:
        # Descripción breve:
        # Orden tutorial:  nn.nn

    Parámetros:
        path (str): Ruta del fichero demo.

    Retorna:
        tuple[int, int] | None: (major, minor) si existe el campo; None en caso contrario.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(25):
                line = f.readline()
                if not line:
                    break
                m = _ORDER_PATTERN.search(line)
                if m:
                    major = int(m.group(1))
                    minor = int(m.group(2))
                    return major, minor
    except Exception:
        pass
    return None


def find_demo_files_flat(root=DEMOS_DIR):
    """Localiza demos recursivamente sin imponer orden por directorio.

    Devuelve lista aplanada con: path, rel, mtime, desc, order
    """
    invalid_substrings = ["SEG", "OLD", "VERS"]
    norm_root = root.replace(os.sep, "/")
    for bad in invalid_substrings:
        if bad in norm_root:
            return []

    result = []
    if not os.path.isdir(root):
        return result

    try:
        entries = list(os.scandir(root))
    except OSError:
        return result

    for e in entries:
        if e.is_file() and is_valid_file(e.name):
            try:
                st = e.stat()
            except OSError:
                continue
            path = e.path
            mtime = st.st_mtime
            rel_examples = _to_posix_relpath(path, DEMOS_DIR)
            rel_project = f"{DEMOS_DIR}/" + rel_examples
            desc = extract_brief_description(path)
            # Filtro: requiere 'Descripción breve:'
            if not desc:
                continue
            rel_examples = _to_posix_relpath(path, DEMOS_DIR)
            rel_project = f"{DEMOS_DIR}/" + rel_examples
            # Filtro: PATH_INCLUDE (prefijos de ruta)
            if not _path_is_included(rel_project):
                continue
            # Filtro: requiere 'Descripción breve:'
            if not desc:
                continue
            # Filtro: PATH_INCLUDE (prefijos de ruta)
            if not _path_is_included(rel_project):
                continue
            order = extract_tutorial_order(path)
            result.append({"path": path, "rel": rel_examples, "mtime": mtime, "desc": desc, "order": order})

    for e in entries:
        if e.is_dir() and is_valid_dir(e.name):
            result.extend(find_demo_files_flat(e.path))

    return result


def find_demo_files(order_mode="tutorial", root=DEMOS_DIR):
    """Devuelve lista de demos según el modo de ordenación.

    Modos:
        - 'tutorial' (por defecto): Orden tutorial nn.nn; sin orden -> al final por basename.
        - 'mtime': Orden histórico (mtime) respetando el criterio jerárquico original.
    """
    if order_mode == "mtime":
        return find_demo_files_hierarchical(root)

    items = find_demo_files_flat(root)

    def sort_key(it):
        if it.get("order") is not None:
            major, minor = it["order"]
            return (0, major, minor, it["rel"].lower())
        basename = os.path.basename(it["path"]).lower()
        return (1, basename, it["rel"].lower())

    items.sort(key=sort_key)
    return items

# NOTA:  [oó] >>> una 'o' cono o sin acento, \s+ >>> Uno o mas espacios,    \s* >>> cero o más espacios.

def extract_brief_description(path):
    """Busca 'Descripción breve:' en las 5 primeras líneas del archivo y devuelve el texto tras los dos puntos."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(9):
                line = f.readline()
                if not line:
                    break
                m = _DESC_PATTERN.search(line)
                if m:
                    desc = m.group(1).strip()
                    return desc if desc else ""
    except Exception:
        pass
    return ""

def find_demo_files_hierarchical(root=DEMOS_DIR):
    """
    En cada directorio:
      1) Ficheros demo_*.py ordenados por mtime DESC
      2) Subdirectorios ordenados por mtime DESC y se repite
    Devuelve lista aplanada con: path, rel, mtime, desc
    """
    # Ignorar directorios prohibidos
    #invalid_substrings = ["SEG/","SEG_", "OLD/",  "OLD_", "VERS/", "VERS_"]
    invalid_substrings = ["SEG","OLD", "VERS"]
    norm_root = root.replace(os.sep, "/")
    for bad in invalid_substrings:
        if bad in norm_root:
            return []

    result = []
    if not os.path.isdir(root):
        return result

    try:
        entries = list(os.scandir(root))
    except OSError:
        return result

    # Ficheros primero (por mtime)
    files = []
    for e in entries:
        if e.is_file() and is_valid_file(e.name):
            try:
                st = e.stat()
            except OSError:
                continue
            files.append((e.path, st.st_mtime))
    files.sort(key=lambda x: x[1], reverse=True)

    for path, mtime in files:
        rel_examples = _to_posix_relpath(path, DEMOS_DIR)
        rel_project = f"{DEMOS_DIR}/" + rel_examples
        desc = extract_brief_description(path)
        result.append({"path": path, "rel": rel_examples, "mtime": mtime, "desc": desc})

    # Directorios después (por mtime)
    dirs = []
    for e in entries:
        if e.is_dir() and is_valid_dir(e.name):
            try:
                d_mtime = e.stat().st_mtime
            except OSError:
                continue
            dirs.append((e.path, d_mtime))
    dirs.sort(key=lambda x: x[1], reverse=True)

    for dpath, _ in dirs:
        result.extend(find_demo_files_hierarchical(dpath))

    return result


def run_demo_replace_process(path):
    """
    Reemplaza el proceso actual por el demo con dos modos:
    - MODO DIRECTO (demos/demo_*.py): NO hace chdir. CWD = raíz del proyecto.
    - MODO SUBDIRECTORIO (demos/<subdir>/demo_*.py): hace chdir al directorio del demo.
    Mantiene PYTHONPATH con la raíz del proyecto y (en subdir) el cwd del demo.
    """
    demo_path = Path(path).resolve()
    demo_dir = demo_path.parent
    project_root = Path(__file__).resolve().parent
    src_root = project_root / "src"

    # DIRECTO si el demo cuelga directamente de examples/
    is_direct_mode = (demo_dir == project_root / DEMOS_DIR)

    # Preparar entorno PYTHONPATH
    env = os.environ.copy()
    cur = env.get("PYTHONPATH", "")
    env["POPUP_PROY_ROOT"] = str(project_root)
    parts = [p for p in cur.split(os.pathsep) if p]

    # Siempre añadimos la raíz del proyecto al principio
    if str(project_root) not in parts:
        parts.insert(0, str(project_root))

    # Con layout src/, lo esencial es incluir <repo>/src
    if src_root.exists() and str(src_root) not in parts:
        parts.insert(0, str(src_root))
    # Opcional pero útil: raíz del repo (scripts, etc.)
    if str(project_root) not in parts:
        parts.insert(0, str(project_root))

    # En modo subdirectorio también añadimos el dir de la demo
    if not is_direct_mode and str(demo_dir) not in parts:
        parts.insert(0, str(demo_dir))
    env["PYTHONPATH"] = os.pathsep.join(parts) if parts else "."

    print("#"*133)
    print("#                            (Lanzador de demos  - main.py )")
    print("#                            -------------------------------")
    if is_direct_mode:
        # MODO DIRECTO: no cambiamos CWD (se asume que el lanzador se ejecuta desde la raíz)
        cwd_for_print = os.getcwd()
        print("#    ▶ MODO DIRECTO: ejecutando sin cambiar cwd.")
        print(f"#   - CWD actual: {cwd_for_print}")
    else:
        # MODO SUBDIRECTORIO: cambiamos a la carpeta de la demo y mostramos aviso
        os.chdir(demo_dir)
        print("#    ▶ MODO SUBDIRECTORIO: cambiando cwd al directorio de la demo.")
        print(f"#   - Nuevo CWD: {demo_dir}")
        print("#   - Aviso:")
        print("#     * Si tu demo asume recursos relativos a su propio script, funcionará tal cual.")
        print("#     * Si necesita recursos compartidos en la raíz (p. ej. styles/, Fonts/),")
        print("#       asegúrate de referenciarlos mediante una ruta robusta (por ejemplo, basada")
        print("#       en la raíz del proyecto o en la carpeta del paquete) o exporta POPUP_STYLES_DIR.")
    print(f"#   - PYTHONPATH: {env['PYTHONPATH']}")
    print(f"#   - POPUP_PROY_ROOT: {env['POPUP_PROY_ROOT']}")
    print("#"*133)
    pygame.quit()
    time.sleep(2)

    # Ejecutar
    argv = [sys.executable, str(demo_path)]
    print("Lanzando demo:", argv)
    os.execvpe(sys.executable, argv, env)

def text_ellipsize(font, text, max_width):
    if font.size(text)[0] <= max_width:
        return text
    ellipsis_w = font.size("…")[0]
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi) // 2
        if font.size(text[:mid])[0] + ellipsis_w <= max_width:
            lo = mid + 1
        else:
            hi = mid
    return text[:max(0, lo - 1)] + "…"

def main(order_mode="tutorial"):
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, FONT_SIZE)
    detail_font = pygame.font.SysFont(None, DETAIL_FONT_SIZE)
    title_font = pygame.font.SysFont(None, 28, bold=True)

    items = find_demo_files(order_mode=order_mode)
    scroll_y = 0
    selected_idx = 0 if items else None
    info_message = ""
    info_timer = 0

    def total_list_height():
        if not items:
            return 0
        return len(items) * (BUTTON_H + BUTTON_GAP) - BUTTON_GAP

    def list_rect():
        return pygame.Rect(PADDING, 100, WINDOW_W - PADDING*2, WINDOW_H - 120)

    def refresh():
        nonlocal items, scroll_y, selected_idx
        items = find_demo_files(order_mode=order_mode)
        scroll_y = 0
        selected_idx = 0 if items else None

    def draw_header():
        header_rect = pygame.Rect(0, 0, WINDOW_W, 80)
        pygame.draw.rect(screen, PANEL, header_rect)
        t_surf = title_font.render(TITLE, True, TEXT)
        #screen.blit(t_surf, (PADDING, header_rect.centery - t_surf.get_height()//2))
        screen.blit(t_surf, (PADDING, header_rect.centery - FONT_SIZE))
        hint = "        ( <Click mouse> o <Enter> Ejecuta  •  <R> Refresca  •  <mover rueda mouse>  •  Hace scroll )"
        hint_surf = detail_font.render(hint, True, SUBTLE)
        screen.blit(hint_surf, (PADDING, header_rect.bottom - hint_surf.get_height() - 10))

    def draw_list():
        lr = list_rect()
        pygame.draw.rect(screen, PANEL, lr, border_radius=12)

        surface = pygame.Surface((lr.w, lr.h))
        surface.fill(PANEL)

        y = -scroll_y
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_inside = lr.collidepoint(mouse_x, mouse_y)

        for idx, it in enumerate(items):
            rect = pygame.Rect(10, y + 10, lr.w - 20, BUTTON_H)
            if rect.bottom >= 0 and rect.top <= lr.h:
                is_hover = mouse_inside and rect.collidepoint(mouse_x - lr.x, mouse_y - lr.y)
                color = BTN_HOVER if is_hover or idx == selected_idx else BTN
                pygame.draw.rect(surface, color, rect, border_radius=10)

                left_pad = rect.x + 14
                right_pad = rect.right - 14
                max_text_w = right_pad - left_pad

                order_prefix = ""
                if it.get("order") is not None:
                    # Línea principal: n.n) + nombre + (fecha)
                    major, minor = it["order"]
                    order_prefix = f"{major}.{minor}) "
                    main_text = f"{order_prefix}{it['rel']} ({format_date_es(it['mtime'])})"
                else:
                    # Línea principal: nombre + (fecha)
                    main_text = f"{it['rel']} ({format_date_es(it['mtime'])})"
                
                main_text = text_ellipsize(font, main_text, max_text_w)
                t1 = font.render(main_text, True, TEXT)
                surface.blit(t1, (left_pad, rect.y + 10))

                # Línea inferior: Descripción breve (si existe)
                if it.get("desc"):
                    t2 = detail_font.render(it["desc"], True, SUBTLE)
                    surface.blit(t2, (left_pad, rect.y + 10 + t1.get_height() + 6))

            y += BUTTON_H + BUTTON_GAP

        # Barra de scroll
        content_h = total_list_height()
        if content_h > lr.h:
            track = pygame.Rect(lr.w - 8, 8, 15, lr.h - 16)
            pygame.draw.rect(surface, (70, 70, 80), track, border_radius=2)
            thumb_h = max(30, int((lr.h / content_h) * track.h))
            thumb_y = int((scroll_y / (content_h - lr.h)) * (track.h - thumb_h))
            thumb = pygame.Rect(track.x, track.y + thumb_y, track.w, thumb_h)
            pygame.draw.rect(surface, (150, 150, 170), thumb, border_radius=2)

        screen.blit(surface, lr.topleft)

    def clamp_scroll():
        nonlocal scroll_y
        lr = list_rect()
        max_scroll = max(0, total_list_height() - lr.h)
        scroll_y = max(0, min(scroll_y, max_scroll))

    def index_at_pos(mx, my):
        lr = list_rect()
        if not lr.collidepoint(mx, my):
            return None
        local_x, local_y = mx - lr.x, my - lr.y
        y = scroll_y + local_y - 10
        idx = int(y // (BUTTON_H + BUTTON_GAP))
        top_y = idx * (BUTTON_H + BUTTON_GAP) + 10
        rect = pygame.Rect(10, top_y - scroll_y, lr.w - 20, BUTTON_H)
        if 0 <= idx < len(items) and rect.collidepoint(local_x, local_y):
            return idx
        return None

    running = True

    while running:
        dt = clock.tick(60)
        screen.fill(BG)
        draw_header()
        draw_list()

        if info_message:
            info_timer -= dt
            if info_timer <= 0:
                info_message = ""

        if info_message:
            msg = detail_font.render(info_message, True, SUBTLE)
            screen.blit(msg, (PADDING, WINDOW_H - msg.get_height() - 8))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * SCROLL_SPEED
                clamp_scroll()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_y -= SCROLL_SPEED
                    clamp_scroll()
                elif event.button == 5:
                    scroll_y += SCROLL_SPEED
                    clamp_scroll()
                elif event.button == 1:
                    idx = index_at_pos(*event.pos)
                    if idx is not None:
                        run_demo_replace_process(items[idx]["path"])

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r:
                    refresh()
                    info_message = "Lista de demos actualizada."
                    info_timer = 1500
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    if items:
                        if selected_idx is None:
                            selected_idx = 0
                        else:
                            if event.key == pygame.K_UP:
                                selected_idx = max(0, selected_idx - 1)
                            else:
                                selected_idx = min(len(items) - 1, selected_idx + 1)
                        lr = list_rect()
                        item_top = selected_idx * (BUTTON_H + BUTTON_GAP)
                        item_bottom = item_top + BUTTON_H
                        if item_top < scroll_y:
                            scroll_y = item_top
                        elif item_bottom > scroll_y + lr.h:
                            scroll_y = item_bottom - lr.h
                        clamp_scroll()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected_idx is not None and 0 <= selected_idx < len(items):
                        run_demo_replace_process(items[selected_idx]["path"])


def parse_order_mode(argv):
    """Parsea --order=<modo> (tutorial|mtime).

    Por compatibilidad se aceptan las variantes:
        --order=mtime
        --order mtime

    Parámetros:
        argv (list[str]): Argumentos (sin el ejecutable).

    Retorna:
        str: 'tutorial' o 'mtime'.
    """
    order_mode = "tutorial"
    for i, arg in enumerate(argv):
        if arg.startswith("--order="):
            order_mode = arg.split("=", 1)[1].strip().lower()
            break
        if arg == "--order" and i + 1 < len(argv):
            order_mode = argv[i + 1].strip().lower()
            break

    if order_mode not in ("tutorial", "mtime"):
        print(f"⚠️  Valor no válido para --order: {order_mode!r}. Usando 'tutorial'.")
        order_mode = "tutorial"

    return order_mode


if __name__ == "__main__":
    if not os.path.isdir(DEMOS_DIR):
        print(f"⚠️ No se encontró el directorio '{DEMOS_DIR}'. Créalo y añade tus demos demo_*.py.")
    order_mode = parse_order_mode(sys.argv[1:])
    main(order_mode=order_mode)

