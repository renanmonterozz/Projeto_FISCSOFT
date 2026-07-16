import _path  # noqa: F401 — garante que o root do projeto está no sys.path

import logging
import sys
from tkinter import messagebox
from PIL import Image
import os

import customtkinter as ctk

from config.styles import ASSETS_DIR, COLORS
from database.conexaodb import Database
from screens.sidebar import Sidebar
from screens.menu_inicial import MenuInicialPage
from screens.usuarios import UsuariosPage
from screens.itens import ItensPage
from screens.agente_mode.infratores import InfratoresPage
from screens.relatorios import RelatoriosPage
from screens.relatorio_entrega import RelatorioEntregaPage
from screens.locais import LocaisPage
from screens.historico import HistoricoPage
from utils import verify_password

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PERMISSOES_ADMIN = {"Menu Principal", "Itens", "Destinacao", "Agente", "Usuario Externo", "Locais Cadastrados", "Relatorio", "Historico"}
PERMISSOES_AGENTE = {"Menu Principal", "Itens", "Destinacao", "Agente", "Usuario Externo", "Locais Cadastrados", "Relatorio", "Historico"}


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FISCSOFT - Login")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["white"])
        self.mostrando_form = False

        try:
            self.img_bg = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "tela_de_login_adm.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "tela_de_login_adm.png")),
                size=(1000, 600),
            )
        except Exception:
            self.img_bg = None

        self.bg_label = ctk.CTkLabel(self, text="", image=self.img_bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.image = self.img_bg

        self.form_frame = None

        self.bg_label.bind("<Button-1>", self.clique_bg)

    def clique_bg(self, event):
        if self.mostrando_form:
            return
        x, y = event.x, event.y
        if 650 <= x <= 970 and 240 <= y <= 360:
            self.mostrar_formulario()
        elif 650 <= x <= 970 and 370 <= y <= 490:
            self.login_certificado()

    def mostrar_formulario(self):
        if self.mostrando_form:
            self.voltar_menu()
            return
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=300, height=270)
        self.form_frame.place(x=660, y=240)

        frame_user = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=8, border_width=1, border_color=COLORS["border"])
        frame_user.pack(pady=(10, 8), padx=25, fill="x")
        frame_user.pack_propagate(False)
        frame_user.configure(height=40)

        ctk.CTkLabel(frame_user, text="\U0001f464", font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]).pack(side="left", padx=(12, 5))
        self.entry_usuario = ctk.CTkEntry(
            frame_user,
            placeholder_text="Usuario",
            height=36,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_usuario.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        frame_senha = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=8, border_width=1, border_color=COLORS["border"])
        frame_senha.pack(pady=8, padx=25, fill="x")
        frame_senha.pack_propagate(False)
        frame_senha.configure(height=40)

        ctk.CTkLabel(frame_senha, text="\U0001f512", font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]).pack(side="left", padx=(12, 5))
        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Senha",
            show="*",
            height=36,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_senha.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        ctk.CTkButton(
            self.form_frame,
            text="Entrar",
            height=38,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.fazer_login,
        ).pack(pady=(18, 6), padx=25, fill="x")

        ctk.CTkButton(
            self.form_frame,
            text="Sair",
            height=28,
            corner_radius=6,
            fg_color=COLORS["dark"],
            hover_color=COLORS["dark_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=4, padx=25, fill="x")

    def voltar_menu(self):
        self.mostrando_form = False
        if self.form_frame:
            self.form_frame.destroy()
            self.form_frame = None

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showwarning("Atencao", "Preencha todos os campos!")
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                return

            sql = "SELECT nome_agente, senha, status, perfil FROM \"agente ibama\" WHERE login = ?"
            resultado = db.executar(sql, (usuario,))
            registro = resultado.fetchone() if resultado else None

        if not registro:
            messagebox.showerror("Erro", "Usuario ou senha incorretos!")
            return

        nome, hash_bd, status, perfil = registro

        if not verify_password(senha, hash_bd):
            messagebox.showerror("Erro", "Usuario ou senha incorretos!")
            return

        if status != "ativo":
            messagebox.showerror("Erro", "Usuario inativo! Contate o administrador.")
            return

        self.usuario_logado = nome
        self.perfil = (perfil or "agente").capitalize()

        if self.perfil == "Admin":
            self._abrir_tela_principal(perfil="admin")
        else:
            self._abrir_tela_principal(perfil="agente")

    def _abrir_tela_principal(self, perfil: str = "admin"):
        self.quit()
        self.destroy()

        main_app = ctk.CTk()
        main_app.title("FISCSOFT" if perfil == "admin" else "FISCSOFT - Usuario")
        main_app.geometry("1200x700")
        main_app.configure(fg_color=COLORS["white"])
        main_app.usuario_logado = self.usuario_logado
        main_app.perfil = perfil

        permissoes = PERMISSOES_ADMIN if perfil == "admin" else PERMISSOES_AGENTE

        def navegar(pagina: str):
            if pagina not in permissoes:
                messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar esta pagina.")
                return

            for w in content_frame.winfo_children():
                w.destroy()

            usuario_logado = main_app.usuario_logado if perfil == "agente" else None

            if pagina == "Menu Principal":
                MenuInicialPage(content_frame, usuario_logado=usuario_logado, perfil=perfil).pack(fill="both", expand=True)
            elif pagina == "Itens":
                ItensPage(content_frame, on_voltar=lambda: navegar("Menu Principal")).pack(fill="both", expand=True)
            elif pagina == "Destinacao":
                RelatorioEntregaPage(content_frame, on_voltar=lambda: navegar("Menu Principal")).pack(fill="both", expand=True)
            elif pagina == "Agente":
                UsuariosPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            elif pagina == "Usuario Externo":
                InfratoresPage(content_frame).pack(fill="both", expand=True)
            elif pagina == "Locais Cadastrados":
                LocaisPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            elif pagina == "Relatorio":
                RelatoriosPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            elif pagina == "Historico":
                HistoricoPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(
                    content_frame,
                    text=pagina,
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=COLORS["text"],
                ).pack(expand=True)

        def logout():
            main_app.quit()
            main_app.destroy()
            app = LoginApp()
            app.mainloop()

        sidebar = Sidebar(main_app, width=210, on_navigate=navegar, on_sair=logout)
        sidebar.pack(side="left", fill="y")

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        pagina_inicial = "Menu Principal"
        navegar(pagina_inicial)
        main_app.mainloop()

    def login_certificado(self):
        if self.mostrando_form:
            self.voltar_menu()
            return
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=300, height=270)
        self.form_frame.place(x=660, y=240)

        ctk.CTkLabel(
            self.form_frame,
            text="\U0001f510",
            font=ctk.CTkFont(size=40),
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            self.form_frame,
            text="Funcionalidade em\ndesenvolvimento",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_muted"],
        ).pack(pady=10)

        ctk.CTkButton(
            self.form_frame,
            text="Voltar",
            height=30,
            corner_radius=6,
            fg_color=COLORS["dark"],
            hover_color=COLORS["dark_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=(20, 10))


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
