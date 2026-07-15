import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "imagens")

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
}

FONTS = {
    "family": "Inter",
    "size_title": 24,
    "size_subtitle": 13,
    "size_body": 13,
    "size_small": 12,
}
