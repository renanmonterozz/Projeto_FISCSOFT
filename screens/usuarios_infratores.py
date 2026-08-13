import _path  # noqa: F401

import customtkinter as ctk

from config.styles import COLORS
from screens.infratores import InfratoresPage
from screens.usuarios import UsuariosPage


class UsuariosInfratoresPage(ctk.CTkScrollableFrame):
    """Tela unica que reune o cadastro de Agentes IBAMA e de Usuarios Externos (infratores)."""

    def __init__(self, master, usuario_logado=None, perfil="admin", **kwargs):
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        usuarios_page = UsuariosPage(
            self, usuario_logado=usuario_logado, perfil=perfil,
            table_height=360,
        )
        usuarios_page.pack(fill="x", pady=(0, 10))

        infratores_page = InfratoresPage(
            self, usuario_logado=usuario_logado, perfil=perfil,
            table_height=360,
        )
        infratores_page.pack(fill="x", pady=(0, 10))


if __name__ == "__main__":
    import _path  # noqa: F401
    import customtkinter as ctk
    app = ctk.CTk()
    app.title("Usuarios e Infratores")
    app.geometry("1200x800")
    UsuariosInfratoresPage(app).pack(fill="both", expand=True)
    app.mainloop()
