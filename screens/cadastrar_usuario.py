import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from config.layout_system import LayoutSystem
from config.styles import COLORS, FONTS, ASSETS_DIR
from config.permissoes import normalizar_perfil
from screens.service.usuario_service import (
    RegraUsuarioError,
    UsuarioService,
    validar_dados_usuario,
)
from screens.widgets import ComboBoxComSeta


PERFIL_DISPLAY = {
    "admin": "Administrador",
    "agente": "Agente",
    "operador": "Operador",
}


class CadastrarUsuarioWindow(ctk.CTkToplevel):
    def __init__(self, master=None, usuario=None, usuario_logado=None):
        super().__init__(master)
        self.usuario_edicao = usuario
        self.usuario_logado = usuario_logado
        self.service = UsuarioService()
        self.title("FISCSOFT - Cadastrar Agente IBAMA")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.usuario_edicao:
            self.preencher_campos()

    def build_ui(self):
        container = LayoutSystem.panel(
            self,
            fill="both",
            expand=True,
            padding=(20, 20),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            header,
            text="Cadastro Agente IBAMA",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Informe os dados de acesso.",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(2, 0))

        form = LayoutSystem.panel(
            container,
            fill="both",
            expand=True,
            padding=(25, (15, 30)),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )

        ctk.CTkLabel(
            form, text="Dados Pessoais",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(18, 8))

        row1 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 10), columns=3)

        self.entry_nome = self._criar_campo(row1, "Nome Completo*", 0, weight=3)
        self.entry_cpf = self._criar_campo(row1, "CPF*", 1, weight=1)
        self.entry_email = self._criar_campo(row1, "E-mail*", 2, weight=2)

        row2 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 15), columns=2)

        self.entry_telefone = self._criar_campo(row2, "Telefone", 0, weight=2)
        self.entry_matricula = self._criar_campo(row2, "Matricula*", 1, weight=2)

        ctk.CTkLabel(
            form, text="Dados de Acesso",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(5, 8))

        row3 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 10), columns=3)

        self.entry_login = self._criar_campo(row3, "Login*", 0, weight=1)
        self.entry_senha = self._criar_campo(row3, "Senha*", 1, weight=1, show="*")
        self.entry_confirmar = self._criar_campo(row3, "Confirmar Senha*", 2, weight=1, show="*")

        row4 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 15), columns=1)

        self.combo_perfil = self._criar_combobox(row4, "Perfil*", 0,
                                                 ["Administrador", "Agente", "Operador"],
                                                 default="Agente")

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(25, 20))

        try:
            salvar_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "salvar.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "salvar.png")),
                size=(20, 20),
            )
        except Exception:
            salvar_icon = None

        ctk.CTkButton(
            btn_frame,
            image=salvar_icon,
            text="  Salvar Usuario",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            compound="left",
            command=self.salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40, corner_radius=4,
            fg_color=COLORS["border"], hover_color="#C8C8C8",
            text_color=COLORS["text"], border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.destroy,
        ).pack(side="right")

    def preencher_campos(self):
        u = self.usuario_edicao
        self.entry_nome.insert(0, u.get("nome") or "")
        self.entry_cpf.insert(0, u.get("cpf") or "")
        self.entry_email.insert(0, u.get("email") or "")
        self.entry_telefone.insert(0, u.get("telefone") or "")
        self.entry_matricula.insert(0, str(u.get("matricula") or ""))
        self.entry_matricula.configure(state="disabled")
        self.entry_login.insert(0, u.get("login") or "")
        perfil_atual = normalizar_perfil(u.get("perfil"))
        self.combo_perfil.set(PERFIL_DISPLAY.get(perfil_atual, "Operador"))

    def _criar_campo(self, parent, label, col, weight=1, show=None):
        label_text = label.rstrip("*")
        return LayoutSystem.field(
            parent,
            label_text,
            column=col,
            weight=weight,
            show=show,
            required=label.endswith("*"),
        )

    def _criar_combobox(self, parent, label, col, values, default=None):
        return LayoutSystem.combobox_field(
            parent,
            label.rstrip("*"),
            values,
            column=col,
            weight=1,
            default=default if default is not None else values[0],
            border_width=1,
            button_color=COLORS["border"],
            button_hover_color=COLORS["hover"],
            dropdown_fg_color=COLORS["white"],
            text_color=COLORS["text"],
        )

    def salvar(self):
        try:
            dados = validar_dados_usuario(
                self.entry_nome.get(),
                self.entry_cpf.get(),
                self.entry_email.get(),
                self.entry_telefone.get(),
                self.entry_matricula.get(),
                self.entry_login.get(),
                self.entry_senha.get(),
                self.entry_confirmar.get(),
                self.combo_perfil.get(),
                em_edicao=bool(self.usuario_edicao),
            )
        except RegraUsuarioError as exc:
            mensagem_erro = str(exc)
            if "senhas" in mensagem_erro or "Matricula" in mensagem_erro:
                messagebox.showerror("Erro", mensagem_erro)
            else:
                messagebox.showwarning("Atencao", mensagem_erro)
            return

        try:
            mensagem = self.service.salvar(
                dados,
                em_edicao=bool(self.usuario_edicao),
                usuario_logado=self.usuario_logado,
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Nao foi possivel salvar o usuario:\n{exc}")
            return

        messagebox.showinfo("Sucesso", mensagem)
        self.destroy()
