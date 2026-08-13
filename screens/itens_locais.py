import _path  # noqa: F401

import customtkinter as ctk

from config.styles import COLORS
from screens.itens import ItensPage
from screens.locais import LocaisPage


class ItensLocaisPage(ctk.CTkScrollableFrame):
    """Tela única que reúne Itens e Locais em abas (merge das telas)."""

    def __init__(self, master, usuario_logado=None, perfil="admin",
                 processo_tccm=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        self.usuario_logado = usuario_logado
        self.perfil = perfil
        self.processo_tccm = processo_tccm

        # Dividir a tela verticalmente: parte superior para `Itens`, inferior para `Locais`
        # Usamos grid com três linhas: top (itens), separator, bottom (locais)
        # Proporção 50% / 50% entre top e bottom
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        sep = ctk.CTkFrame(self, height=2, fg_color=COLORS["border"])  # visual separator
        sep.grid(row=1, column=0, sticky="ew", padx=10)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

        itens_page = ItensPage(
            top_frame, usuario_logado=usuario_logado, perfil=perfil,
            processo_tccm=processo_tccm, table_height=360,
        )
        itens_page.pack(fill="both", expand=True)

        locais_page = LocaisPage(
            bottom_frame, usuario_logado=usuario_logado, perfil=perfil,
            table_height=360,
        )
        locais_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    import _path  # noqa: F401
    import customtkinter as ctk
    app = ctk.CTk()
    app.title("Itens e Locais")
    # abrir maximizado (tamanho máximo permitido)
    app.after(0, app.state, "zoomed")
    ItensLocaisPage(app).pack(fill="both", expand=True)
    app.mainloop()
