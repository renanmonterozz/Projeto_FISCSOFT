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

COLORS = {
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

FONTS = {
    "family": "Inter",
    "size_title": 24,
    "size_subtitle": 13,
    "size_body": 13,
    "size_small": 12,
}

LAYOUT = {
    "base_width": 1920,
    "base_height": 1080,
    "page_padding_x": 30,
    "page_padding_y": 20,
    "panel_radius": 4,
    "panel_border": 1,
    "field_height": 38,
    "field_radius": 4,
    "table_header_height": 44,
    "row_height": 52,
    "section_spacing": 14,
    "card_padding": 20,
}
