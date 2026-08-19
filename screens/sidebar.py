import _path  # noqa: F401

import customtkinter as ctk
from PIL import Image
import os

from config.styles import ASSETS_DIR, COLORS, FONTS
from config.permissoes import paginas_do_perfil


def carregar_icone(caminho: str, tamanho_max: int = 20):
    try:
        img = Image.open(os.path.join(ASSETS_DIR, caminho))
        w, h = img.size
        ratio = min(tamanho_max / w, tamanho_max / h)
        novo_w = int(w * ratio)
        novo_h = int(h * ratio)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(novo_w, novo_h))
    except Exception:
        return None


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None, on_sair=None, on_voltar=None, perfil=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#FAFAFA", corner_radius=0)
        self.on_navigate = on_navigate
        self.on_sair = on_sair
        self.on_voltar = on_voltar
        self.pagina_atual = None
        self.btns_navegacao = {}

        # --- Topo: logo + botoes de navegacao ---
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(pady=(35, 45))

        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "logo_fiscsoft.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "logo_fiscsoft.png")),
                size=(130, 130),
            )
            ctk.CTkLabel(logo_frame, text="", image=logo_img).pack()
        except Exception:
            ctk.CTkLabel(logo_frame, text="FiscSoft", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1D4D21").pack()

        # Each entry: (display_text, icon_filename, page_name)
        # `page_name` is the identifier passed to the navigate handler
        self.nav_items = [
            ("Menu Principal", "casa.png", "Menu Principal"),
            ("Registros", "registro.png", "Itens"),
            ("Destinacao", "destinacao.png", "Destinacao"),
            ("Usuários", "usuarios.png", "Agente"),
            ("Notas Fiscais", "relatorios.png", "Notas Fiscais"),
            ("Historico", "relogio.png", "Historico"),
        ]

        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="x", padx=18, pady=(0, 10))

        paginas_permitidas = paginas_do_perfil(perfil) if perfil else None

        for entry in self.nav_items:
            display_text, img_path, page_name = entry
            # permissions check must use the page identifier (existing names)
            if paginas_permitidas is not None and page_name not in paginas_permitidas:
                continue

            btn_icon = carregar_icone(img_path)

            btn = ctk.CTkButton(
                nav_container,
                image=btn_icon,
                text=f"   {display_text}",
                anchor="w",
                compound="left",
                fg_color="transparent",
                hover_color=COLORS["nav_hover"],
                text_color=COLORS["nav_text"],
                height=42,
                corner_radius=6,
                font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_small"], weight="bold"),
                command=lambda p=page_name: self._navigate(p),
            )
            btn.pack(fill="x", pady=4)
            self.btns_navegacao[page_name] = btn

        # --- Fundo: sempre colado na parte inferior ---
        separador = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1, corner_radius=0)
        separador.pack(side="bottom", fill="x", padx=18, pady=(0, 12))

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=18, pady=(0, 22))

        sair_icon = None
        try:
            sair_img = Image.open(os.path.join(ASSETS_DIR, "sair.png"))
            sair_icon = ctk.CTkImage(
                light_image=sair_img,
                dark_image=sair_img,
                size=(20, 20),
            )
        except Exception:
            pass

        # Mostrar botão 'Voltar' no menu (por exemplo, voltar ao Dashboard TCCM)
        paginas_permitidas = paginas_do_perfil(perfil) if perfil else None
        if paginas_permitidas and "Dashboard TCCM" in paginas_permitidas:
            self.voltar_container = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=38)
            self.voltar_container.pack(fill="x", pady=(0, 8))

            ctk.CTkFrame(self.voltar_container, fg_color=COLORS["border"], corner_radius=8).place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2)

            ctk.CTkButton(
                self.voltar_container,
                text="   Voltar",
                anchor="w",
                compound="left",
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                text_color="white",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_small"], weight="bold"),
                command=self._voltar,
            ).place(relx=0, rely=0, relwidth=1, relheight=1)

        sair_container = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=38)
        sair_container.pack(fill="x")

        ctk.CTkFrame(sair_container, fg_color=COLORS["border"], corner_radius=8).place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2)

        ctk.CTkButton(
            sair_container,
            image=sair_icon,
            text="   Sair",
            anchor="w",
            compound="left",
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color="white",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_small"], weight="bold"),
            command=self._sair,
        ).place(relx=0, rely=0, relwidth=1, relheight=1)

    def _navigate(self, page_name: str):
        if self.pagina_atual and self.pagina_atual in self.btns_navegacao:
            btn_antigo = self.btns_navegacao[self.pagina_atual]
            btn_antigo.configure(fg_color="transparent", text_color=COLORS["nav_text"])

        self.pagina_atual = page_name
        if page_name in self.btns_navegacao:
            self.btns_navegacao[page_name].configure(fg_color="#00674F", text_color="#FFF9BE")

        if self.on_navigate:
            self.on_navigate(page_name)

        # Mostrar/ocultar o botão Voltar para páginas específicas
        try:
            if page_name == "Dashboard TCCM":
                if getattr(self, "voltar_container", None) is not None and not getattr(self.voltar_container, "_is_packed", False):
                    self.voltar_container.pack(fill="x")
                    self.voltar_container._is_packed = True
            else:
                if getattr(self, "voltar_container", None) is not None and getattr(self.voltar_container, "_is_packed", False):
                    self.voltar_container.pack_forget()
                    self.voltar_container._is_packed = False
        except Exception:
            pass

    def _voltar(self):
        if self.on_voltar:
            try:
                self.on_voltar()
                return
            except Exception:
                pass
        # fallback para navegar ao dashboard padrão
        if self.on_navigate:
            self.on_navigate("Dashboard TCCM")

    def _sair(self):
        if self.on_sair:
            self.on_sair()
