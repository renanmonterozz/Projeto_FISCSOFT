import _path  # noqa: F401 — garante que o root do projeto está no sys.path

import pywinstyles

import logging
import os
import sys
from tkinter import TclError, messagebox

from PIL import Image

import customtkinter as ctk

from config.styles import ASSETS_DIR, COLORS, FONTS
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
from screens.tccm_dashboard import TccmDashboardPage, TccmDetalhesPage
from screens.cadastro_tccm_completo import CadastroTCCMCompleto
from fiscsoft_externo.main_externo import abrir_app_externo
from utils import verify_password
from fiscsoft_externo.telas.sidebar_externo import SidebarExterno
from fiscsoft_externo.telas.dashboard_externo import DashboardExterno
from fiscsoft_externo.telas.notas_fiscais_externo import NotasFiscaisExterno
from fiscsoft_externo.telas.relatorio_externo import RelatorioExterno

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def _suprimir_erro_tcl():
    try:
        import tkinter as _tk
        root = _tk._default_root
        if root is not None:
            root.tk.eval("proc bgerror {msg} {}")
    except Exception:
        pass

PERMISSOES_ADMIN = {"Menu Principal", "Itens", "Destinacao", "Agente", "Usuario Externo", "Locais Cadastrados", "Relatorio", "Historico", "Dashboard TCCM"}
PERMISSOES_AGENTE = {"Menu Principal", "Itens", "Destinacao", "Agente", "Usuario Externo", "Locais Cadastrados", "Relatorio", "Historico", "Dashboard TCCM"}
PERMISSOES_EXTERNO = {"Menu Inicial", "Cadastrar Notas", "Relatorio"}

# Cores da tela de login
DOURADO = "#c8b464"
AMARELO_BOTAO = "#FFF48C"
VERDE_POLIGONO = "#302F2F"


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FISCSOFT - Login")
        self.configure(fg_color=COLORS["white"])
        self.after(0, self.state, "zoomed")

        # --- Imagem de fundo ---
        img_path = os.path.join(ASSETS_DIR, "Tela_Loginn.png")
        self._img_pil = None
        try:
            self._img_pil = Image.open(img_path)
        except Exception:
            self._img_pil = None

        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.after(100, self._ajustar_imagem_fundo)

        # --- Texto "ACESSE O SISTEMA!" ---
        self.label_titulo = ctk.CTkLabel(
            self,
            text="ACESSE O SISTEMA!",
            font=("Libre Baskerville", 36),
            text_color="#FFF9BE",
            fg_color="#000001",
            bg_color="#000001"
        )
        self.label_titulo.place(relx=0.5, rely=0.78, anchor="center")
        pywinstyles.set_opacity(self.label_titulo, color="#000001")

        # --- Botão único: Entrar no Sistema ---
        self.btn_entrar = ctk.CTkButton(
            self,
            text="Entrar no Sistema",
            width=480,
            height=50,
            corner_radius=16,
            fg_color=VERDE_POLIGONO,
            bg_color="#000001",
            hover_color="#211E1E",
            text_color=AMARELO_BOTAO,
            font=ctk.CTkFont(family="Segoe UI", size=19),
            border_width=2,
            border_color="#000001",
            command=self._mostrar_formulario_unificado
        )
        self.btn_entrar.place(relx=0.5, rely=0.88, anchor="center")
        pywinstyles.set_opacity(self.btn_entrar, color="#000001")

    def _ajustar_imagem_fundo(self):
        if self._img_pil is None:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            self.after(100, self._ajustar_imagem_fundo)
            return

        img_w, img_h = self._img_pil.size
        scale = max(w / img_w, h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized = self._img_pil.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        cropped = resized.crop((left, top, left + w, top + h))

        img = ctk.CTkImage(light_image=cropped, dark_image=cropped, size=(w, h))
        self.bg_label.configure(image=img)
        self.bg_label.image = img

    def _mostrar_formulario_unificado(self):
        self.btn_entrar.place_forget()

        self.frame_login = ctk.CTkFrame(self, fg_color="#000001", bg_color="#000001", corner_radius=0)
        self.frame_login.place(relx=0.5, rely=0.88, anchor="center")
        self.frame_login.lift()
        pywinstyles.set_opacity(self.frame_login, color="#000001")

        self._modo_login = "usuario"

        # --- Campo de credencial com icone de toggle ao lado ---
        frame_cred = ctk.CTkFrame(self.frame_login, fg_color="transparent", width=586, height=45)
        frame_cred.pack(pady=(10, 10))
        frame_cred.pack_propagate(False)

        self.entry_credencial = ctk.CTkEntry(
            frame_cred,
            width=480, height=45, corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3", border_color="#16A34A", border_width=2,
            text_color="#2D8A4E", placeholder_text_color="#2D8A4E",
            placeholder_text="Digite seu usuario"
        )
        self.entry_credencial.place(x=53, y=0)

        self.btn_modo = ctk.CTkButton(
            frame_cred, text="\U0001f464", width=45, height=45, corner_radius=8,
            fg_color="#CFFFE3", hover_color="#b0e8c0",
            text_color="#2D8A4E", font=("Segoe UI", 18),
            border_width=2, border_color="#16A34A",
            command=self._toggle_modo_login
        )
        self.btn_modo.place(x=541, y=0)

        # --- Campo de senha com olho ---
        frame_senha = ctk.CTkFrame(self.frame_login, fg_color="transparent", width=586, height=45)
        frame_senha.pack(pady=(0, 10))
        frame_senha.pack_propagate(False)

        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            width=480, height=45, corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3", border_color="#16A34A", border_width=2,
            text_color="#2D8A4E", placeholder_text_color="#2D8A4E",
            placeholder_text="Digite sua senha", show="*"
        )
        self.entry_senha.place(x=53, y=0)

        self.btn_eye = ctk.CTkButton(
            frame_senha, text="\U0001f441", width=45, height=45, corner_radius=8,
            fg_color="#CFFFE3", hover_color="#b0e8c0",
            text_color="#2D8A4E", font=("Segoe UI", 18),
            border_width=2, border_color="#16A34A",
            command=self._toggle_senha
        )
        self.btn_eye.place(x=541, y=0)

        self._senha_visivel = False

        # --- Botoes Entrar / Sair ---
        frame_botoes = ctk.CTkFrame(self.frame_login, fg_color="transparent")
        frame_botoes.pack(pady=(0, 10))

        ctk.CTkButton(
            frame_botoes, text="Entrar", width=100, height=40, corner_radius=12,
            fg_color=VERDE_POLIGONO, hover_color="#211E1E",
            text_color=AMARELO_BOTAO, font=("Segoe UI", 16),
            command=self._on_entrar_click
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes, text="Sair", width=100, height=40, corner_radius=12,
            fg_color="#8B0000", hover_color="#850202",
            text_color="white", font=("Segoe UI", 16),
            command=self._on_sair_click
        ).pack(side="left", padx=5)

        self.entry_credencial.bind("<Return>", lambda e: self._on_entrar_click())
        self.entry_senha.bind("<Return>", lambda e: self._on_entrar_click())

    def _toggle_modo_login(self):
        if self._modo_login == "usuario":
            self._modo_login = "cpf"
            self.btn_modo.configure(text="\U0001faaa")
            self.entry_credencial.configure(placeholder_text="Digite seu CPF")
        else:
            self._modo_login = "usuario"
            self.btn_modo.configure(text="\U0001f464")
            self.entry_credencial.configure(placeholder_text="Digite seu usuario")
        self.entry_credencial.delete(0, "end")

    def _on_entrar_click(self):
        credencial = self.entry_credencial.get().strip()
        senha = self.entry_senha.get()

        if not credencial or not senha:
            messagebox.showwarning("Atencao", "Preencha todos os campos!")
            return

        if self._modo_login == "usuario":
            self._login_usuario(credencial, senha)
        else:
            self._login_cpf(credencial, senha)

    def _login_usuario(self, usuario, senha):
        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                return
            sql = "SELECT nome_agente, senha, status, perfil FROM \"agente ibama\" WHERE login = ?"
            resultado = db.executar(sql, (usuario,))
            registro = resultado.fetchone() if resultado else None

        if registro:
            nome, hash_bd, status, perfil = registro

            if not verify_password(senha, hash_bd):
                messagebox.showerror("Erro", "Usuario ou senha incorretos!")
                return

            if status != "ativo":
                messagebox.showerror("Erro", "Usuario inativo! Contate o administrador.")
                return

            self.usuario_logado = nome
            perfil_db = (perfil or "agente").lower()
            self.perfil = "admin" if perfil_db == "administrador" else "agente"

            if self.perfil == "admin":
                self._abrir_tela_principal(perfil="admin")
            else:
                self._abrir_tela_principal(perfil="agente")
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                return

            sql_inf = "SELECT id_infrator, nome_infrator, senha FROM infrator WHERE cpf = ?"
            resultado_inf = db.executar(sql_inf, (usuario,))
            registro_inf = resultado_inf.fetchone() if resultado_inf else None

        if not registro_inf:
            messagebox.showerror("Erro", "Usuario ou senha incorretos!")
            return

        id_infrator, nome_inf, hash_bd_inf = registro_inf

        if not verify_password(senha, hash_bd_inf):
            messagebox.showerror("Erro", "Usuario ou senha incorretos!")
            return

        self.usuario_logado = nome_inf
        self.id_infrator = id_infrator
        self._abrir_app_externo()

    def _abrir_app_externo(self):
        self.quit()
        self.destroy()

        abrir_app_externo(
            self.usuario_logado,
            self.id_infrator,
            ao_sair=lambda: LoginApp().mainloop(),
        )

    def _login_cpf(self, cpf, senha):
        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                return
            sql = "SELECT id_infrator, nome_infrator, senha FROM infrator WHERE cpf = ?"
            resultado = db.executar(sql, (cpf,))
            registro = resultado.fetchone() if resultado else None

        if not registro:
            messagebox.showerror("Erro", "CPF ou senha incorretos!")
            return

        id_infrator, nome, hash_bd = registro

        if not verify_password(senha, hash_bd):
            messagebox.showerror("Erro", "CPF ou senha incorretos!")
            return

        self.usuario_logado = nome
        self.id_infrator = id_infrator
        self._abrir_tela_externa()

    def _on_sair_click(self):
        self.frame_login.place_forget()
        self.btn_entrar.place(relx=0.5, rely=0.88, anchor="center")

    def _toggle_senha(self):
        if self._senha_visivel:
            self.entry_senha.configure(show="*")
            self.btn_eye.configure(text="\U0001f441")
            self._senha_visivel = False
        else:
            self.entry_senha.configure(show="")
            self.btn_eye.configure(text="\U0001f441")
            self._senha_visivel = True

    def _abrir_tela_externa(self):
        try:
            self.quit()
            self.destroy()
        except TclError:
            pass

        main_app = ctk.CTk()
        main_app.title("FISCSOFT - Acesso Externo")
        main_app.configure(fg_color=COLORS["white"])
        main_app.after(0, main_app.state, "zoomed")
        main_app.usuario_logado = self.usuario_logado
        main_app.id_infrator = self.id_infrator

        def navegar(pagina: str):
            if pagina not in PERMISSOES_EXTERNO:
                messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar esta pagina.")
                return

            for w in content_frame.winfo_children():
                w.destroy()

            if pagina == "Menu Inicial":
                DashboardExterno(
                    content_frame,
                    usuario_logado=self.usuario_logado,
                    id_infrator=self.id_infrator
                ).pack(fill="both", expand=True)
            elif pagina == "Cadastrar Notas":
                NotasFiscaisExterno(
                    content_frame,
                    usuario_logado=self.usuario_logado,
                    id_infrator=self.id_infrator,
                    on_voltar=lambda: navegar("Menu Inicial"),
                ).pack(fill="both", expand=True)
            elif pagina == "Relatorio":
                RelatorioExterno(
                    content_frame,
                    usuario_logado=self.usuario_logado,
                    id_infrator=self.id_infrator
                ).pack(fill="both", expand=True)

        def logout():
            try:
                main_app.quit()
                main_app.destroy()
            except TclError:
                pass
            app = LoginApp()
            _suprimir_erro_tcl()
            app.mainloop()

        sidebar = SidebarExterno(main_app, width=210, on_navigate=navegar, on_sair=logout)
        sidebar.pack(side="left", fill="y")

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        navegar("Menu Inicial")
        _suprimir_erro_tcl()
        main_app.mainloop()

    def _abrir_tela_principal(self, perfil: str = "admin", processo_tccm: str = None):
        try:
            self.quit()
            self.destroy()
        except TclError:
            pass

        welcome_app = ctk.CTk()
        welcome_app.title("FISCSOFT - Bem-vindo")
        welcome_app.configure(fg_color=COLORS["bg"])
        welcome_app.after(0, welcome_app.state, "zoomed")
        welcome_app.usuario_logado = self.usuario_logado
        welcome_app.perfil = perfil
        welcome_app.processo_tccm = processo_tccm

        header = ctk.CTkFrame(welcome_app, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 0))

        ctk.CTkLabel(
            header,
            text=f"Bem-vindo, {self.usuario_logado}",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        content = ctk.CTkFrame(welcome_app, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(15, 20))

        def _logout_welcome():
            try:
                welcome_app.quit()
                welcome_app.destroy()
            except TclError:
                pass
            app = LoginApp()
            _suprimir_erro_tcl()
            app.mainloop()

        def _abrir_cadastro_tccm():
            win = ctk.CTkToplevel(welcome_app)
            win.title("Cadastro de TCCM")
            win.geometry("900x650")
            win.configure(fg_color=COLORS["bg"])
            win.transient(welcome_app)
            win.grab_set()
            CadastroTCCMCompleto(
                win,
                on_voltar=win.destroy,
                usuario_logado=self.usuario_logado, perfil=perfil,
            ).pack(fill="both", expand=True)
            win.wait_window()
            dashboard._recarregar()

        dashboard = TccmDashboardPage(
            content, usuario_logado=self.usuario_logado, perfil=perfil,
            on_selecionar=lambda proc: self._abrir_menu_principal(welcome_app, perfil, processo_tccm=proc),
            on_sair=_logout_welcome,
            on_cadastrar=_abrir_cadastro_tccm,
        )
        dashboard.pack(fill="both", expand=True)
        dashboard._welcome_app = welcome_app
        dashboard._perfil = perfil
        dashboard._abrir_menu_principal_cb = lambda proc: self._abrir_menu_principal(welcome_app, perfil, processo_tccm=proc)

        if processo_tccm:
            welcome_app.after(100, lambda: self._abrir_menu_principal(welcome_app, perfil, processo_tccm=processo_tccm))

        _suprimir_erro_tcl()
        welcome_app.mainloop()

    def _abrir_menu_principal(self, welcome_app, perfil: str, processo_tccm: str = None):
        try:
            welcome_app.quit()
            welcome_app.destroy()
        except TclError:
            pass

        main_app = ctk.CTk()
        main_app.title("FISCSOFT" if perfil == "admin" else "FISCSOFT - Usuario")
        main_app.configure(fg_color=COLORS["white"])
        main_app.after(0, main_app.state, "zoomed")
        main_app.usuario_logado = self.usuario_logado
        main_app.perfil = perfil

        permissoes = PERMISSOES_ADMIN if perfil == "admin" else PERMISSOES_AGENTE

        _processo_tccm = processo_tccm

        def navegar(pagina: str, processo_tccm: str = None):
            if processo_tccm is None:
                processo_tccm = _processo_tccm

            if pagina not in permissoes:
                messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar esta pagina.")
                return

            for w in content_frame.winfo_children():
                w.destroy()

            usuario_logado = main_app.usuario_logado if perfil == "agente" else None

            if pagina == "Menu Principal":
                MenuInicialPage(content_frame, usuario_logado=usuario_logado, perfil=perfil,
                                processo_tccm=processo_tccm).pack(fill="both", expand=True)
            elif pagina == "Itens":
                ItensPage(content_frame, on_voltar=lambda: navegar("Menu Principal"),
                          processo_tccm=processo_tccm).pack(fill="both", expand=True)
            elif pagina == "Destinacao":
                RelatorioEntregaPage(content_frame, on_voltar=lambda: navegar("Menu Principal"),
                                     usuario_logado=usuario_logado, processo_tccm=processo_tccm).pack(fill="both", expand=True)
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
            elif pagina == "Dashboard TCCM":
                if processo_tccm:
                    TccmDetalhesPage(
                        content_frame, processo=processo_tccm,
                        on_voltar=lambda: navegar("Dashboard TCCM"),
                        usuario_logado=usuario_logado, perfil=perfil,
                    ).pack(fill="both", expand=True)
                else:
                    TccmDashboardPage(
                        content_frame, usuario_logado=usuario_logado, perfil=perfil,
                        on_cadastrar=lambda: navegar("Cadastro TCCM"),
                    ).pack(fill="both", expand=True)
            elif pagina == "Cadastro TCCM":
                CadastroTCCMCompleto(
                    content_frame,
                    on_voltar=lambda: navegar("Dashboard TCCM"),
                    usuario_logado=usuario_logado, perfil=perfil,
                ).pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(
                    content_frame,
                    text=pagina,
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=COLORS["text"],
                ).pack(expand=True)

        def logout():
            try:
                main_app.quit()
                main_app.destroy()
            except TclError:
                pass
            app = LoginApp()
            _suprimir_erro_tcl()
            app.mainloop()

        sidebar = Sidebar(main_app, width=210, on_navigate=navegar, on_sair=logout)
        sidebar.pack(side="left", fill="y")

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        navegar("Menu Principal")
        _suprimir_erro_tcl()
        main_app.mainloop()


if __name__ == "__main__":
    app = LoginApp()
    _suprimir_erro_tcl()
    app.mainloop()
