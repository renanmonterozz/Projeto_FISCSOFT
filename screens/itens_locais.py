import _path  # noqa: F401

import customtkinter as ctk

from config.styles import COLORS
from screens.itens import ItensPage
from screens.locais import LocaisPage


class ItensLocaisPage(ctk.CTkScrollableFrame):
    """Tela unica que reune o cadastro de Itens e de Locais de destino."""

    def __init__(self, master, usuario_logado=None, perfil="admin",
                 processo_tccm=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        self.usuario_logado = usuario_logado
        self.perfil = perfil
        self.processo_tccm = processo_tccm

        itens_page = ItensPage(
            self, usuario_logado=usuario_logado, perfil=perfil,
            processo_tccm=processo_tccm, table_height=360,
        )
        itens_page.pack(fill="x", pady=(0, 10))

        locais_page = LocaisPage(
            self, usuario_logado=usuario_logado, perfil=perfil,
            table_height=360,
        )
        locais_page.pack(fill="x", pady=(0, 10))


if __name__ == "__main__":
    import _path  # noqa: F401
    import customtkinter as ctk
    app = ctk.CTk()
    app.title("Itens e Locais")
    app.geometry("1200x800")
    ItensLocaisPage(app).pack(fill="both", expand=True)
    app.mainloop()
