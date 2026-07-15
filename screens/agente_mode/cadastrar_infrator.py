import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from utils import hash_password, registrar_log


class CadastrarInfratorWindow(ctk.CTkToplevel):
    def __init__(self, master=None, infrator=None):
        super().__init__(master)
        self.infrator_edicao = infrator
        self.title("FISCSOFT - Cadastrar Infrator")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.infrator_edicao:
            self.preencher_campos()

    def build_ui(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

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

        form = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        form.pack(fill="both", expand=True, padx=25, pady=(15, 30))

        ctk.CTkLabel(
            form, text="Dados Pessoais",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(18, 8))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_nome = self._criar_campo(row1, "Nome Completo*", 0, weight=3)
        self.entry_cpf = self._criar_campo(row1, "CPF*", 1, weight=1)
        self.entry_email = self._criar_campo(row1, "E-mail*", 2, weight=2)

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        self.entry_telefone = self._criar_campo(row2, "Telefone", 0, weight=2)

        ctk.CTkLabel(
            form, text="Dados de Acesso",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(5, 8))

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(0, 10))

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
        parent.grid_columnconfigure(col, weight=weight)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame, height=36, corner_radius=4,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
            show=show,
        )
        entry.pack(fill="x")
        return entry

    def salvar(self):
        nome = self.entry_nome.get()
        cpf = self.entry_cpf.get()
        email = self.entry_email.get()
        telefone = self.entry_telefone.get()
        senha = self.entry_senha.get()
        confirmar = self.entry_confirmar.get()

        if not all([nome, cpf, email, senha, confirmar]):
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios!")
            return

        if senha != confirmar:
            messagebox.showerror("Erro", "As senhas nao conferem!")
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                return

            senha_hash = hash_password(senha)
            if self.infrator_edicao:
                db.executar(
                    "UPDATE infrator SET nome_infrator=?, cpf=?, email=?, "
                    "telefone_infrator=?, senha=? WHERE id_infrator=?",
                    (nome, cpf, email, telefone, senha_hash, self.infrator_edicao["id"])
                )
                mensagem = f"Infrator '{nome}' atualizado com sucesso!"
            else:
                db.executar(
                    "INSERT INTO infrator (nome_infrator, cpf, email, telefone_infrator, senha) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (nome, cpf, email, telefone, senha_hash)
                )
                mensagem = f"Infrator '{nome}' cadastrado com sucesso!"

            db.commitar()

        registrar_log(
            getattr(self.master, 'usuario_logado', None) or "Sistema",
            "edicao" if self.infrator_edicao else "cadastro",
            "infrator",
            mensagem
        )

        messagebox.showinfo("Sucesso", mensagem)
        self.destroy()
