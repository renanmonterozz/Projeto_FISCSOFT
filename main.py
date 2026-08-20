import _path  # noqa: F401 — garante que o root do projeto está no sys.path

import logging
import os
import sys
from dataclasses import dataclass
from tkinter import TclError, messagebox

from PIL import Image, ImageTk

import customtkinter as ctk

from config.layout_system import LayoutSystem
from config.styles import ASSETS_DIR, COLORS, FONTS
from config.permissoes import PAGINAS_EXTERNO, normalizar_pagina, normalizar_perfil, paginas_do_perfil, pode_acao
from services.login_service import LoginService, RegraLoginError
from screens.sidebar import Sidebar
from screens.menu_inicial import MenuInicialPage
from screens.notas_fiscais import RelatoriosPage
from screens.destinacao import RelatorioEntregaPage
from screens.historico import HistoricoPage
from screens.auditoria import AuditoriaPage
from screens.itens_locais import ItensLocaisPage
from screens.usuarios_infratores import UsuariosInfratoresPage
from screens.tccm_dashboard import TccmDashboardPage, TccmDetalhesPage
from screens.cadastro_tccm_completo import CadastroTCCMCompleto
from utils import login_por_certificado
from screens.sidebar_externo import SidebarExterno
from screens.dashboard_externo import DashboardExterno
from screens.notas_fiscais_externo import NotasFiscaisExterno
from screens.relatorio_externo import RelatorioExterno

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


@dataclass
class SessaoUsuario:
    usuario_logado: str = ""
    perfil: str = "operador"
    id_infrator: int | None = None
    processo_tccm: str | None = None


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
        self.bg_label.lower()
        self.after(100, self._ajustar_imagem_fundo)

        # --- Texto "ACESSE O SISTEMA!" ---
        self.label_titulo = LayoutSystem.login_title(self)
        self.label_titulo.place(relx=0.5, rely=LayoutSystem.LOGIN_TITLE_REL_Y, anchor="center")

        # --- Botão 1: Entrar com Usuário e Senha ---
        self.btn_usuario = LayoutSystem.login_button(
            self,
            "Entrar com Usuário e Senha",
            command=self._mostrar_formulario_unificado,
        )
        self.btn_usuario.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_USER_REL_Y, anchor="center")

        # --- Botão 2: Entrar com Certificado Digital ---
        self.btn_certificado = LayoutSystem.login_button(
            self,
            "Entrar com Certificado Digital",
            command=self._login_certificado,
        )
        self.btn_certificado.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_CERT_REL_Y, anchor="center")

        self.login_service = LoginService()
    def _ajustar_imagem_fundo(self):
        try:
            if self._img_pil is None:
                return
            if not self.winfo_exists():
                return
            if not hasattr(self, "bg_label") or not self.bg_label.winfo_exists():
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
            self.bg_label.lower()
        except (TclError, RuntimeError):
            # A janela ja foi destruida ou o widget foi removido. Ignora sem derrubar o fluxo.
            return

    def _mostrar_formulario_unificado(self):
        self.btn_usuario.place_forget()
        self.btn_certificado.place_forget()

        self.frame_login = ctk.CTkFrame(
            self,
            width=LayoutSystem.LOGIN_FORM_WIDTH,
            height=LayoutSystem.LOGIN_FORM_HEIGHT,
            fg_color=LayoutSystem.LOGIN_FORM_COLOR,
            bg_color=LayoutSystem.LOGIN_FORM_COLOR,
            corner_radius=0,
            border_width=0,
        )
        self.frame_login.place(relx=0.5, rely=LayoutSystem.LOGIN_FORM_REL_Y, anchor="center")
        self.frame_login.pack_propagate(False)
        self.frame_login.lift()

        # --- Campo de credencial ---
        frame_cred = ctk.CTkFrame(self.frame_login, fg_color="transparent", width=586, height=45)
        frame_cred.pack(pady=(10, 10))
        frame_cred.pack_propagate(False)

        self.entry_credencial = ctk.CTkEntry(
            frame_cred,
            width=480, height=45, corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3", border_color="#16A34A", border_width=2,
            text_color="#213727", placeholder_text_color="#213727",
            placeholder_text="Digite seu usuário ou CPF"
        )
        self.entry_credencial.place(x=53, y=0)

        # --- Campo de senha com olho ---
        frame_senha = ctk.CTkFrame(self.frame_login, fg_color="transparent", width=586, height=45)
        frame_senha.pack(pady=(0, 10))
        frame_senha.pack_propagate(False)

        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            width=480, height=45, corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3", border_color="#16A34A", border_width=2,
            text_color="#213727", placeholder_text_color="#213727",
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
            fg_color="#202a15", bg_color="#202a15", hover_color="#354522",
            text_color=LayoutSystem.LOGIN_BUTTON_TEXT_COLOR, font=("Segoe UI", 16),
            border_width=2, border_color="#FFF48C",
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

    
    def _on_entrar_click(self):
        credencial = self.entry_credencial.get().strip()
        senha = self.entry_senha.get()

        if not credencial or not senha:
            messagebox.showwarning("Atencao", "Preencha todos os campos!")
            return

        # Detect CPF (digits, length 11) automatically; fallback to usuario
        only_digits = ''.join([c for c in credencial if c.isdigit()])
        if len(only_digits) == 11 and only_digits == credencial:
            self._login_cpf(credencial, senha)
        else:
            self._login_usuario(credencial, senha)

    def _login_usuario(self, usuario, senha):
        try:
            resultado = self.login_service.autenticar_credencial_unificada(usuario, senha)
        except RegraLoginError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        if resultado is None:
            messagebox.showerror("Erro", "Usuario ou senha incorretos!")
            return

        if resultado["tipo"] == "agente":
            self.usuario_logado = resultado["nome"]
            self.perfil = normalizar_perfil(resultado["perfil"])
            self._abrir_tela_principal(perfil=self.perfil)
        else:
            self.usuario_logado = resultado["nome"]
            self.id_infrator = resultado["id"]
            self._abrir_tela_externa()

    def _login_cpf(self, cpf, senha):
        try:
            resultado = self.login_service.autenticar_infrator_por_cpf(cpf, senha)
        except RegraLoginError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        if resultado is None:
            messagebox.showerror("Erro", "CPF ou senha incorretos!")
            return

        self.usuario_logado = resultado["nome"]
        self.id_infrator = resultado["id"]
        self._abrir_tela_externa()

    def _on_sair_click(self):
        if hasattr(self, "frame_login"):
            self.frame_login.place_forget()
        self.label_titulo.place(relx=0.5, rely=LayoutSystem.LOGIN_TITLE_REL_Y, anchor="center")
        self.btn_usuario.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_USER_REL_Y, anchor="center")
        self.btn_certificado.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_CERT_REL_Y, anchor="center")

    def _login_certificado(self):
        self.btn_usuario.place_forget()
        self.btn_certificado.place_forget()
        try:
            sucesso, mensagem, dados = login_por_certificado()

            if not sucesso:
                messagebox.showerror("Erro", mensagem)
                self.label_titulo.place(relx=0.5, rely=LayoutSystem.LOGIN_TITLE_REL_Y, anchor="center")
                self.btn_usuario.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_USER_REL_Y, anchor="center")
                self.btn_certificado.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_CERT_REL_Y, anchor="center")
                return

            self.usuario_logado = dados["nome"]
            perfil_db = (dados["perfil"] or "agente").lower()
            self.perfil = "admin" if perfil_db == "administrador" else "agente"

            if self.perfil == "admin":
                self._abrir_tela_principal(perfil="admin")
            else:
                self._abrir_tela_principal(perfil="agente")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao autenticar com certificado: {e}")
            self.label_titulo.place(relx=0.5, rely=LayoutSystem.LOGIN_TITLE_REL_Y, anchor="center")
            self.btn_usuario.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_USER_REL_Y, anchor="center")
            self.btn_certificado.place(relx=0.5, rely=LayoutSystem.LOGIN_BUTTON_CERT_REL_Y, anchor="center")

    def _toggle_senha(self):
        if self._senha_visivel:
            self.entry_senha.configure(show="*")
            self.btn_eye.configure(text="\U0001f441")
            self._senha_visivel = False
        else:
            self.entry_senha.configure(show="")
            self.btn_eye.configure(text="\U0001f441")
            self._senha_visivel = True

    @staticmethod
    def _fechar_janela(app):
        try:
            if app is None:
                return
            if hasattr(app, "winfo_exists") and app.winfo_exists():
                app.quit()
                app.destroy()
        except TclError:
            pass
        except RuntimeError:
            pass

    def _retornar_para_login(self, janela_atual=None):
        if janela_atual is not None:
            self._fechar_janela(janela_atual)
        self._fechar_janela(self)

        app = LoginApp()
        _suprimir_erro_tcl()
        app.mainloop()

    def _criar_sessao(self, *, usuario_logado=None, perfil=None, id_infrator=None, processo_tccm=None):
        return SessaoUsuario(
            usuario_logado=usuario_logado or "",
            perfil=perfil or "operador",
            id_infrator=id_infrator,
            processo_tccm=processo_tccm,
        )

    def _abrir_tela_externa(self):
        self._fechar_janela(self)

        main_app = ctk.CTk()
        main_app.title("FISCSOFT - Acesso Externo")
        main_app.configure(fg_color=COLORS["white"])
        main_app.after(0, main_app.state, "zoomed")
        main_app.usuario_logado = self.usuario_logado
        main_app.id_infrator = self.id_infrator

        def navegar(pagina: str):
            if pagina not in PAGINAS_EXTERNO:
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
            self._retornar_para_login(main_app)
 
        sidebar = SidebarExterno(main_app, width=210, on_navigate=navegar, on_sair=logout)
        sidebar.pack(side="left", fill="y")

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        navegar("Menu Inicial")
        _suprimir_erro_tcl()
        main_app.mainloop()

    def _abrir_tela_principal(self, perfil: str = "admin", processo_tccm: str = None):
        self._abrir_selecao_tccm(perfil=perfil, processo_tccm=processo_tccm)

    def _abrir_selecao_tccm(self, perfil: str = "admin", processo_tccm: str = None):
        self._fechar_janela(self)

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
            self._retornar_para_login(welcome_app)

        def _abrir_cadastro_tccm():
            if not pode_acao(perfil, "criar_tccm"):
                messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para cadastrar TCCM.")
                return
            win = ctk.CTkToplevel(welcome_app)
            win.title("Cadastro de TCCM")
            win.after(0, win.state, "zoomed")
            win.update_idletasks()
            win.state("zoomed")
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
        usuario_logado = self.usuario_logado
        self._fechar_janela(welcome_app)

        main_app = ctk.CTk()
        main_app.title("FISCSOFT" if perfil == "admin" else "FISCSOFT - Usuario")
        main_app.configure(fg_color=COLORS["white"])
        main_app.after(0, main_app.state, "zoomed")
        main_app.update_idletasks()
        main_app.state("zoomed")
        main_app.usuario_logado = usuario_logado
        main_app.perfil = perfil

        permissoes = paginas_do_perfil(perfil)

        _processo_tccm = processo_tccm

        def navegar(pagina: str, processo_tccm: str = None):
            if processo_tccm is None:
                processo_tccm = _processo_tccm

            pagina = normalizar_pagina(pagina)
            if pagina not in permissoes:
                messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar esta pagina.")
                return

            for w in content_frame.winfo_children():
                w.destroy()

            usuario_logado = main_app.usuario_logado

            if pagina == "Menu Principal":
                MenuInicialPage(content_frame, usuario_logado=usuario_logado, perfil=perfil,
                                processo_tccm=processo_tccm).pack(fill="both", expand=True)
            elif pagina in ("Itens", "Locais Cadastrados"):
                ItensLocaisPage(content_frame, usuario_logado=usuario_logado,
                                processo_tccm=processo_tccm, perfil=perfil).pack(fill="both", expand=True)
            elif pagina == "Destinacao":
                RelatorioEntregaPage(content_frame, on_voltar=lambda: navegar("Menu Principal"),
                                     usuario_logado=usuario_logado, processo_tccm=processo_tccm,
                                     perfil=perfil).pack(fill="both", expand=True)
            elif pagina in ("Agente", "Usuario Externo"):
                UsuariosInfratoresPage(content_frame, usuario_logado=usuario_logado,
                                       perfil=perfil).pack(fill="both", expand=True)
            elif pagina == "Notas Fiscais":
                if not processo_tccm:
                    messagebox.showwarning(
                        "TCCM obrigatorio",
                        "Selecione um TCCM antes de abrir as notas fiscais.",
                    )
                    return
                RelatoriosPage(
                    content_frame,
                    usuario_logado=usuario_logado,
                    perfil=perfil,
                    processo_tccm=processo_tccm,
                ).pack(fill="both", expand=True)
            elif pagina == "Historico":
                HistoricoPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            elif pagina == "Auditoria NF":
                AuditoriaPage(content_frame, usuario_logado=usuario_logado).pack(fill="both", expand=True)
            elif pagina == "Dashboard TCCM":
                if processo_tccm:
                    TccmDetalhesPage(
                        content_frame, processo=processo_tccm,
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
            self._retornar_para_login(main_app)

        sidebar = Sidebar(main_app, width=210, on_navigate=navegar, on_sair=logout, perfil=perfil)
        sidebar.pack(side="left", fill="y")

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        try:
            navegar("Menu Principal")
        except Exception as exc:
            logging.exception("Erro ao abrir o menu inicial")
            messagebox.showerror(
                "Erro ao abrir o menu inicial",
                f"Nao foi possivel carregar o menu inicial:\n{exc}",
                parent=main_app,
            )
        _suprimir_erro_tcl()
        main_app.mainloop()


if __name__ == "__main__":
    app = LoginApp()
    _suprimir_erro_tcl()
    app.mainloop()
