import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

COLORS = {
    "primary": "#16A34A",
    "primary_hover": "#15803D",
    "danger": "#DC2626",
    "danger_hover": "#D00E0E",
    "text": "#111111",
    "text_muted": "#666666",
    "border": "#D9D9D9",
    "bg": "#F5F5F5",
    "white": "#FFFFFF",
}

FONTS = {
    "family": "Inter",
    "size_title": 24,
    "size_subtitle": 13,
    "size_body": 13,
    "size_small": 12,
}
