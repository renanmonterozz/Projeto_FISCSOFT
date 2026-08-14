# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files


# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(SPEC).parent
ASSETS_DIR = PROJECT_ROOT / "assets"

APP_NAME = "FISCSOFT"


# ============================================================
# ARQUIVOS DE DADOS
# ============================================================

datas = []

# ------------------------------------------------------------
# CustomTkinter
# ------------------------------------------------------------

datas += collect_data_files("customtkinter")


# ------------------------------------------------------------
# Assets do FISCSOFT
# ------------------------------------------------------------

if ASSETS_DIR.exists():
    datas.append(
        (
            str(ASSETS_DIR),
            "assets"
        )
    )


# ============================================================
# ANÁLISE DO PROJETO
# ============================================================

a = Analysis(
    ["main.py"],

    pathex=[
        str(PROJECT_ROOT)
    ],

    binaries=[],

    datas=datas,

    hiddenimports=[
        # ----------------------------------------------------
        # Bibliotecas externas
        # ----------------------------------------------------

        "customtkinter",
        "pywinstyles",
        "PIL",
        "PIL.Image",

        # ----------------------------------------------------
        # Configuração
        # ----------------------------------------------------

        "config",
        "config.styles",
        "config.permissoes",

        # ----------------------------------------------------
        # Banco de dados
        # ----------------------------------------------------

        "database",
        "database.conexaodb",

        # ----------------------------------------------------
        # Telas internas
        # ----------------------------------------------------

        "screens",
        "screens.sidebar",
        "screens.menu_inicial",
        "screens.notas_fiscais",
        "screens.destinacao",
        "screens.historico",
        "screens.itens_locais",
        "screens.usuarios_infratores",
        "screens.tccm_dashboard",
        "screens.cadastro_tccm_completo",

        # ----------------------------------------------------
        # Telas externas
        # ----------------------------------------------------

        "screens.sidebar_externo",
        "screens.dashboard_externo",
        "screens.notas_fiscais_externo",
        "screens.relatorio_externo",

        # ----------------------------------------------------
        # Utilitários
        # ----------------------------------------------------

        "utils",
    ],

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,
)


# ============================================================
# PYZ
# ============================================================

pyz = PYZ(
    a.pure
)


# ============================================================
# EXECUTÁVEL
# ============================================================

exe = EXE(
    pyz,

    a.scripts,

    a.binaries,

    a.datas,

    [],

    name=APP_NAME,

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=True,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,

    icon=(
        str(ASSETS_DIR / "icone.ico")
        if (ASSETS_DIR / "icone.ico").exists()
        else None
    ),
)