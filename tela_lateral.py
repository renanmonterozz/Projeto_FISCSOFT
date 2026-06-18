import customtkinter as ctk
from PIL import Image


def carregar_icone(caminho, tamanho_max=20):
    try:
        img = Image.open(caminho)
        w, h = img.size
        ratio = min(tamanho_max / w, tamanho_max / h)
        novo_w = int(w * ratio)
        novo_h = int(h * ratio)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(novo_w, novo_h))
    except Exception:
        return None

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#FAFAFA", corner_radius=0)
        self.pack_propagate(False)

        linha_direita = ctk.CTkFrame(self, fg_color="#C8C8C8", width=2, corner_radius=0)
        linha_direita.pack(side="right", fill="y")

        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(pady=(35, 45))

        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open("assets/logo_fiscsoft.png"),
                dark_image=Image.open("assets/logo_fiscsoft.png"),
                size=(130, 130),
            )
            ctk.CTkLabel(logo_frame, text="", image=logo_img).pack()
        except Exception:
            ctk.CTkLabel(logo_frame, text="FiscSoft", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1D4D21").pack()

        self.nav_items = [
            ("Menu Inicial", "assets/casa.png"),
            ("Locais Cadastrados", "assets/predios.png"),
            ("Itens", "assets/caixa.png"),
            ("Relatórios", "assets/relatorios.png"),
            ("Histórico", "assets/relogio.png"),
            ("Destinação", "assets/caminhão.png"),
            ("Usuários", "assets/usuarios.png"),
        ]

        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="x", padx=18, pady=(0, 10))

        for text, img_path in self.nav_items:
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
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            )
            btn.pack(fill="x", pady=4)

        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        separador = ctk.CTkFrame(self, fg_color="#D9D9D9", height=1, corner_radius=0)
        separador.pack(fill="x", padx=18, pady=(0, 12))

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=18, pady=(0, 22))

        tema_escuro_icon = carregar_icone("assets/lua.png")

        tema_container = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=38)
        tema_container.pack(fill="x", pady=(0, 8))

        ctk.CTkFrame(tema_container, fg_color="#C8C8C8", corner_radius=8).place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2)

        ctk.CTkButton(
            tema_container,
            image=tema_escuro_icon,
            text="   Tema Escuro",
            anchor="w",
            compound="left",
            fg_color="#D2D2D2",
            hover_color="#BEBEBE",
            text_color="white",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            state="disabled",
        ).place(relx=0, rely=0, relwidth=1, relheight=1)

        sair_icon = None
        try:
            sair_img = Image.open("assets/sair.png")
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
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
        ).place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT")
    app.geometry("1200x700")
    app.configure(fg_color="#FFFFFF")

    sidebar = Sidebar(app, width=210)
    sidebar.pack(side="left", fill="y")

    app.mainloop()
