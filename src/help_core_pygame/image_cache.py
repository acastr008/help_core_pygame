from __future__ import annotations

"""
Programa asistido por ChatGPT en fecha 29/ene/2026 y hora 00:00
Titulo: ImageCache para help_core_pygame
Descripción: Resuelve rutas (base_dir), carga imágenes con pygame, escala al ancho objetivo
             y mantiene caché por (abs_path, target_width). Devuelve (surface, w, h) o None.
"""


from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

SurfaceInfo = Tuple[pygame.Surface, int, int]


@dataclass(frozen=True)
class _ImageKey:
    abs_path: str
    target_width: int


class ImageCache:
    """
    Caché de imágenes para evitar recargar/escalar cada frame.

    - Rutas absolutas: se usan tal cual.
    - Rutas relativas: se resuelven contra base_dir (si existe).
    - Si falla carga/resolución: devuelve None (no rompe el render).
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self._base_dir = Path(base_dir).resolve() if base_dir else None
        self._cache: Dict[_ImageKey, SurfaceInfo] = {}

    def set_base_dir(self, base_dir: Optional[str]) -> None:
        """Actualiza el base_dir (p.ej. si cambia la configuración)."""
        self._base_dir = Path(base_dir).resolve() if base_dir else None

    def resolve_src_to_abs_path(self, src: str) -> Optional[Path]:
        """
        Resuelve un src (relativo o absoluto) a Path absoluto.

        Returns
        -------
        Path absoluto o None si no se puede resolver.
        """
        src_stripped = (src or "").strip()
        if not src_stripped:
            return None

        candidate = Path(src_stripped)
        if candidate.is_absolute():
            return candidate

        if self._base_dir is None:
            return None

        return (self._base_dir / candidate).resolve()

    def get_scaled(self, src: str, target_width: int) -> Optional[SurfaceInfo]:
        """
        Carga y escala una imagen al ancho objetivo manteniendo aspecto.

        Returns
        -------
        (surface_scaled, w, h) o None si falla.
        """
        abs_path = self.resolve_src_to_abs_path(src)
        if abs_path is None:
            return None

        key = _ImageKey(str(abs_path), int(target_width))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        loaded = self._load_image(abs_path)
        if loaded is None:
            return None

        scaled = self._scale_to_width(loaded, target_width)
        if scaled is None:
            return None

        self._cache[key] = scaled
        return scaled

    def _load_image(self, abs_path: Path) -> Optional[pygame.Surface]:
        """Carga con pygame.image.load y convierte si el display está inicializado."""
        try:
            if not abs_path.exists():
                return None

            surface = pygame.image.load(str(abs_path))

            # convert()/convert_alpha() solo si hay display; si no, blit sigue funcionando.
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                try:
                    if surface.get_alpha() is not None or surface.get_flags() & pygame.SRCALPHA:
                        surface = surface.convert_alpha()
                    else:
                        surface = surface.convert()
                except pygame.error:
                    pass

            return surface

        except (pygame.error, OSError):
            return None

    def _scale_to_width(self, surface: pygame.Surface, target_width: int) -> Optional[SurfaceInfo]:
        """Escala al ancho objetivo manteniendo aspecto."""
        try:
            src_w, src_h = surface.get_size()
            if src_w <= 0 or src_h <= 0:
                return None

            max_w = max(1, int(target_width))
            if src_w <= max_w:
                return surface, src_w, src_h

            scale = max_w / float(src_w)
            dst_w = max(1, int(round(src_w * scale)))
            dst_h = max(1, int(round(src_h * scale)))

            try:
                scaled = pygame.transform.smoothscale(surface, (dst_w, dst_h))
            except pygame.error:
                scaled = pygame.transform.scale(surface, (dst_w, dst_h))

            return scaled, dst_w, dst_h

        except (ValueError, pygame.error):
            return None

