import customtkinter as ctk
from tkinter import messagebox
from config.styles import COLORS, FONTS
from database.conexaodb import Database
from utils import hash_password


class CadastrarAgenteIbamaWindow(ctk.CTkToplevel):
    def __init__(self, master=None, agente=None):
        super().__init__(master)
        self.agente_edicao = agente
        self.title("FISCSOFT - Cadastrar Infrator")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.agente_edicao:
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
            text="Informe os dados do agente.",
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
            font=ctk.CTkFont(size=14, weight="bold"),
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
            font=ctk.CTkFont(size=14, weight="bold"),
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
            font=ctk.CTkFont(size=14, weight="bold"),
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
            font=ctk.CTkFont(size=14),
            command=self.destroy,
        ).pack(side="right")

    def preencher_campos(self):
        a = self.agente_edicao
        self.entry_nome.insert(0, a["nome"])
        self.entry_cpf.insert(0, a["cpf"])
        self.entry_email.insert(0, a["email"])
        self.entry_telefone.insert(0, a.get("telefone", ""))
        if "senha" in a:
            self.entry_senha.insert(0, a["senha"])
            self.entry_confirmar.insert(0, a["senha"])

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
            placeholder_text_color="#999999",
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

        db = Database()
        if db.conectar():
            senha_hash = hash_password(senha)
            if self.agente_edicao:
                db.executar(
                    "UPDATE infrator SET nome_infrator=%s, cpf=%s, email=%s, "
                    "telefone_infrator=%s, senha=%s WHERE id_infrator=%s",
                    (nome, cpf, email, telefone, senha_hash, self.agente_edicao["id"])
                )
                mensagem = f"Infrator '{nome}' atualizado com sucesso!"
            else:
                db.executar(
                    "INSERT INTO infrator (nome_infrator, cpf, email, telefone_infrator, senha) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (nome, cpf, email, telefone, senha_hash)
                )
                mensagem = f"Agente '{nome}' cadastrado com sucesso!"

            db.commitar()
            db.desconectar()

            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()
        else:
            messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
