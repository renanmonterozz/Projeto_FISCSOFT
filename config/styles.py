import os
import sys


def _resolve_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        meipass = os.path.normpath(sys._MEIPASS)
        if os.path.isdir(os.path.join(meipass, "assets", "imagens")):
            return meipass
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        if os.path.isdir(os.path.join(exe_dir, "assets", "imagens")):
            return exe_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _resolve_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "imagens")
if not os.path.isdir(ASSETS_DIR):
    fallback = os.path.join(os.path.dirname(BASE_DIR), "assets", "imagens")
    if os.path.isdir(fallback):
        ASSETS_DIR = fallback

_LIGHT_COLORS = {
    "primary": "#16A34A",
    "primary_hover": "#15803D",
    "primary_light": "#E8F5E9",
    "primary_light_hover": "#C8E6C9",
    "success": "#A5D6A7",
    "success_hover": "#81C784",
    "success_dark": "#28a745",
    "success_dark_hover": "#218838",
    "warning": "#ffc107",
    "warning_hover": "#e0a800",
    "danger": "#DC2626",
    "danger_hover": "#D00E0E",
    "danger_light": "#FFEBEE",
    "dark": "#2c2c2c",
    "dark_hover": "#555555",
    "row_hover": "#F0F0F0",
    "text": "#111111",
    "text_muted": "#666666",
    "border": "#D9D9D9",
    "table_header": "#FAFAFA",
    "hover": "#F0F0F0",
    "bg": "#F5F5F5",
    "white": "#FFFFFF",
    "nav_hover": "#CFFFE3",
    "nav_text": "#1F1F1F",
    "login_black": "#000001",
    "login_title_text": "#FFF9BE",
    "login_btn_text": "#FFF48C",
    "login_btn_hover": "#211E1E",
    "login_field_bg": "#CFFFE3",
    "login_field_border": "#16A34A",
    "login_field_text": "#2D8A4E",
    "login_field_hover": "#b0e8c0",
    "login_btn_danger": "#8B0000",
    "login_btn_danger_hover": "#850202",
}

_DARK_COLORS = {
    "primary": "#22C55E",
    "primary_hover": "#16A34A",
    "primary_light": "#1A3A2A",
    "primary_light_hover": "#1E4D32",
    "success": "#22C55E",
    "success_hover": "#16A34A",
    "success_dark": "#22C55E",
    "success_dark_hover": "#16A34A",
    "warning": "#FBBF24",
    "warning_hover": "#F59E0B",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "danger_light": "#3A1A1A",
    "dark": "#E0E0E0",
    "dark_hover": "#CCCCCC",
    "row_hover": "#2A2A2A",
    "text": "#F0F0F0",
    "text_muted": "#A0A0A0",
    "border": "#333333",
    "table_header": "#1A1A1A",
    "hover": "#2A2A2A",
    "bg": "#121212",
    "white": "#1E1E1E",
    "nav_hover": "#253828",
    "nav_text": "#E0E0E0",
}

_current_theme = "light"

def get_colors() -> dict:
    """Retorna as cores do tema atual."""
    return _DARK_COLORS if _current_theme == "dark" else _LIGHT_COLORS

def get_theme() -> str:
    """Retorna o tema atual ('light' ou 'dark')."""
    return _current_theme

def toggle_theme() -> str:
    """Alterna entre tema claro e escuro. Retorna o novo tema."""
    global _current_theme
    _current_theme = "dark" if _current_theme == "light" else "light"
    return _current_theme

# Alias para compatibilidade - agora é uma referência dinâmica
COLORS = get_colors()

FONTS = {
    "family": "Inter",
    "size_title": 24,
    "size_subtitle": 13,
    "size_body": 13,
    "size_small": 12,
}
