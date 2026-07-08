import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from PIL import Image
import os

from config.styles import ASSETS_DIR, COLORS, FONTS


def carregar_icone(caminho, tamanho_max=20):
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
    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#FAFAFA", corner_radius=0)
        self.on_navigate = on_navigate
        self.pack_propagate(False)

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

        self.nav_items = [
            ("Menu Inicial", "casa.png"),
            ("Locais Cadastrados", "predios.png"),
            ("Itens", "caixa.png"),
            ("Relatorios", "relatorios.png"),
            ("Historico", "relogio.png"),
            ("Destinacao", "destinacao.png"),
            ("Agentes IBAMA", "usuarios.png"),
            ("Infratores", "Agente.png"),
        ]

        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="x", padx=18, pady=(0, 10))

        for text, img_path in self.nav_items:
            if text == "Agente Ibama":
                try:
                    img = Image.open(os.path.join(ASSETS_DIR, img_path))
                    img.thumbnail((16, 16))
                    padded = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
                    pad_x = (20 - img.width) // 2
                    pad_y = (20 - img.height) // 2
                    padded.paste(img, (pad_x, pad_y), img if img.mode == "RGBA" else None)
                    btn_icon = ctk.CTkImage(light_image=padded, dark_image=padded, size=(20, 20))
                except Exception:
                    btn_icon = None
            else:
                btn_icon = carregar_icone(img_path)

            btn = ctk.CTkButton(
                nav_container,
                image=btn_icon,
                text=f"   {text}",
                anchor="w",
                compound="left",
                fg_color="transparent",
                hover_color="#CFFFE3",
                text_color="#1F1F1F",
                height=42,
                corner_radius=6,
                font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_small"], weight="bold"),
                command=lambda t=text: self._navigate(t),
            )
            btn.pack(fill="x", pady=4)

        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        separador = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1, corner_radius=0)
        separador.pack(fill="x", padx=18, pady=(0, 12))

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=18, pady=(0, 22))

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

        sair_container = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=38)
        sair_container.pack(fill="x")

        ctk.CTkFrame(sair_container, fg_color="#C8C8C8", corner_radius=8).place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2)

        ctk.CTkButton(
            sair_container,
            image=sair_icon,
            text="   Sair",
            anchor="w",
            compound="left",
            fg_color="#FF1212",
            hover_color="#D00E0E",
            text_color="white",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_small"], weight="bold"),
        ).place(relx=0, rely=0, relwidth=1, relheight=1)

    def _navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)


# if __name__ == "__main__":
#     from screens.usuarios import UsuariosPage

#     ctk.set_appearance_mode("light")
#     ctk.set_default_color_theme("blue")

#     app = ctk.CTk()
#     app.title("FISCSOFT")
#     app.geometry("1200x700")
#     app.configure(fg_color=COLORS["white"])

#     content_frame = ctk.CTkFrame(app, fg_color=COLORS["bg"])
#     content_frame.pack(side="right", fill="both", expand=True)

#     def navegar(pagina):
#         for w in content_frame.winfo_children():
#             w.destroy()
#         if pagina == "Usuarios Externos":
#             UsuariosPage(content_frame).pack(fill="both", expand=True)
#         else:
#             ctk.CTkLabel(
#                 content_frame,
#                 text=pagina,
#                 font=ctk.CTkFont(size=24, weight="bold"),
#                 text_color=COLORS["text"],
#             ).pack(expand=True)

#     sidebar = Sidebar(app, width=210, on_navigate=navegar)
#     sidebar.pack(side="left", fill="y")

#     navegar("Usuarios Externos")

    # app.mainloop()
