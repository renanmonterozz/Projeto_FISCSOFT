import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.layout_system import LayoutSystem
from config.styles import COLORS, FONTS
from screens.service.infrator_service import (
    InfratorService,
    RegraInfratorError,
    validar_dados_infrator,
)


class CadastrarInfratorWindow(ctk.CTkToplevel):
    def __init__(self, master=None, infrator=None):
        super().__init__(master)
        self.infrator_edicao = infrator
        self.service = InfratorService()
        self.title("FISCSOFT - Cadastrar Infrator")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.infrator_edicao:
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
            text="Cadastro / Edicao de Infrator",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Informe os dados do infrator.",
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

        row2 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 15), columns=1)

        self.entry_telefone = self._criar_campo(row2, "Telefone", 0, weight=2)

        ctk.CTkLabel(
            form, text="Dados de Acesso",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(5, 8))

        row3 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 10), columns=2)

        self.entry_senha = self._criar_campo(row3, "Senha*", 0, weight=1, show="*")
        self.entry_confirmar = self._criar_campo(row3, "Confirmar Senha*", 1, weight=1, show="*")

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(25, 20))

        ctk.CTkButton(
            btn_frame,
            text="  Salvar Infrator",
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
            fg_color=COLORS["border"], hover_color=COLORS["hover"],
            text_color=COLORS["text"], border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.destroy,
        ).pack(side="right")

    def preencher_campos(self):
        i = self.infrator_edicao
        self.entry_nome.insert(0, i["nome"])
        self.entry_cpf.insert(0, i["cpf"])
        self.entry_email.insert(0, i["email"])
        self.entry_telefone.insert(0, i.get("telefone", ""))

    def _criar_campo(self, parent, label, col, weight=1, show=None):
        return LayoutSystem.field(
            parent,
            label.rstrip("*"),
            column=col,
            weight=weight,
            required=label.endswith("*"),
            show=show,
        )

    def salvar(self):
        try:
            dados = validar_dados_infrator(
                self.entry_nome.get(),
                self.entry_cpf.get(),
                self.entry_email.get(),
                self.entry_telefone.get(),
                self.entry_senha.get(),
                self.entry_confirmar.get(),
            )
        except RegraInfratorError as exc:
            if "senhas" in str(exc):
                messagebox.showerror("Erro", str(exc))
            else:
                messagebox.showwarning("Atencao", str(exc))
            return

        try:
            mensagem = self.service.salvar(
                dados,
                infrator_id=self.infrator_edicao["id"] if self.infrator_edicao else None,
                usuario_logado=getattr(self.master, "usuario_logado", None),
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Nao foi possivel salvar o infrator:\n{exc}")
            return

        messagebox.showinfo("Sucesso", mensagem)
        self.destroy()
