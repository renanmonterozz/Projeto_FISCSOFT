import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from config.styles import ASSETS_DIR
from conexaodb import Database


class CadastrarUsuarioWindow(ctk.CTkToplevel):
    def __init__(self, master=None, usuario=None, usuario_logado=None):
        super().__init__(master)
        self.usuario_edicao = usuario
        self.usuario_logado = usuario_logado
        self.title("FISCSOFT - Cadastrar Usuário")
        self.geometry("820x700")
        self.resizable(False, False)
        self.configure(fg_color="#D0D0D0")
        self.grab_set()

        self.build_ui()

        if self.usuario_edicao:
            self.preencher_campos()

    def build_ui(self):
        container = ctk.CTkFrame(
            self, fg_color="white", corner_radius=10,
            border_width=1, border_color="#B0B0B0"
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Header ──
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))

        self.btn_fechar = ctk.CTkButton(
            header, text="X", width=30, height=30,
            corner_radius=6, fg_color="transparent",
            hover_color="#E0E0E0", text_color="#333333",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.destroy,
        )
        self.btn_fechar.pack(side="right")

        ctk.CTkLabel(
            header,
            text="Cadastro / Edição de Usuário",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#16A34A",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Informe os dados do usuário.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#111111",
        ).pack(anchor="w", pady=(2, 0))

        # ── Form Container ──
        form = ctk.CTkFrame(
            container, fg_color="white", corner_radius=8,
            border_width=1, border_color="#C8C8C8"
        )
        form.pack(fill="both", expand=True, padx=25, pady=(15, 30))

        # ── Dados Pessoais ──
        ctk.CTkLabel(
            form, text="Dados Pessoais",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#111111",
        ).pack(anchor="w", padx=20, pady=(18, 8))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_nome = self._criar_campo(row1, "Nome Completo*", 0, weight=3)
        self.entry_cpf = self._criar_campo(row1, "CPF*", 1, weight=1)
        self.entry_email = self._criar_campo(row1, "E-mail*", 2, weight=2)

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        self.entry_telefone = self._criar_campo(row2, "Telefone", 0, weight=2)
        self.entry_matricula = self._criar_campo(row2, "Matrícula*", 1, weight=2)

        # ── Dados de Acesso ──
        ctk.CTkLabel(
            form, text="Dados de Acesso",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#111111",
        ).pack(anchor="w", padx=20, pady=(5, 8))

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_login = self._criar_campo(row3, "Login*", 0, weight=1)
        self.entry_senha = self._criar_campo(row3, "Senha*", 1, weight=1, show="*")
        self.entry_confirmar = self._criar_campo(row3, "Confirmar Senha*", 2, weight=1, show="*")

        row4 = ctk.CTkFrame(form, fg_color="transparent")
        row4.pack(fill="x", padx=20, pady=(0, 15))

        self.combo_perfil = self._criar_combobox(row4, "Perfil*", 0, ["agente", "operador", "admin"])

        # ── Botões ──
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
            text="  Salvar Usuário",
            height=40, corner_radius=8,
            fg_color="#16A34A", hover_color="#15803D",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=14, weight="bold"),
            compound="left",
            command=self.salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40, corner_radius=8,
            fg_color="#E0E0E0", hover_color="#C8C8C8",
            text_color="#333333", border_width=1,
            border_color="#B0B0B0",
            font=ctk.CTkFont(size=14),
            command=self.destroy,
        ).pack(side="right")

    def preencher_campos(self):
        u = self.usuario_edicao
        self.entry_nome.insert(0, u["nome"])
        self.entry_cpf.insert(0, u["cpf"])
        self.entry_email.insert(0, u["email"])
        self.entry_telefone.insert(0, u.get("telefone", ""))
        self.entry_matricula.insert(0, str(u["matricula"]))
        self.entry_matricula.configure(state="disabled")
        self.entry_login.insert(0, u["login"])
        self.entry_senha.insert(0, u["senha"])
        self.entry_confirmar.insert(0, u["senha"])
        self.combo_perfil.set(u["perfil"].lower())

    def _criar_campo(self, parent, label, col, weight=1, show=None):
        parent.grid_columnconfigure(col, weight=weight)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=12),
            text_color="#333333",
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame, height=36, corner_radius=6,
            border_width=1, border_color="#B0B0B0",
            fg_color="white", text_color="#111111",
            placeholder_text_color="#999999",
            show=show,
        )
        entry.pack(fill="x")
        return entry

    def _criar_combobox(self, parent, label, col, values):
        parent.grid_columnconfigure(col, weight=1)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=12),
            text_color="#333333",
        ).pack(anchor="w", pady=(0, 4))

        combo = ctk.CTkComboBox(
            frame, values=values, height=36,
            corner_radius=6, border_width=1,
            border_color="#B0B0B0",
            fg_color="white", button_color="#E0E0E0",
            button_hover_color="#C8C8C8",
            dropdown_fg_color="white",
            text_color="#111111",
        )
        combo.pack(fill="x")
        combo.set(values[0])
        return combo

    def salvar(self):
        nome = self.entry_nome.get()
        cpf = self.entry_cpf.get()
        email = self.entry_email.get()
        telefone = self.entry_telefone.get()
        matricula = self.entry_matricula.get()
        login = self.entry_login.get()
        senha = self.entry_senha.get()
        confirmar = self.entry_confirmar.get()
        perfil = self.combo_perfil.get()

        if not all([nome, cpf, email, matricula, login, senha, confirmar, perfil]):
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
            return

        if senha != confirmar:
            messagebox.showerror("Erro", "As senhas não conferem!")
            return

        try:
            matricula_int = int(matricula)
        except ValueError:
            messagebox.showerror("Erro", "Matrícula deve ser um número!")
            return

        db = Database()
        if db.conectar():
            if self.usuario_edicao:
                sql = """UPDATE `agente ibama` SET
                         nome_agente=%s, cpf=%s, email=%s, telefone=%s,
                         login=%s, senha=%s, perfil=%s, atualizado_por=%s
                         WHERE matricula=%s"""
                params = (nome, cpf, email, telefone, login, senha, perfil, self.usuario_logado or "", matricula_int)
                mensagem = f"Usuário '{nome}' atualizado com sucesso!"
            else:
                sql = """INSERT INTO `agente ibama`
                         (matricula, nome_agente, cpf, email, telefone, login, senha, perfil, status, cadastrado_por)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ativo', %s)"""
                params = (matricula_int, nome, cpf, email, telefone, login, senha, perfil, self.usuario_logado or "")
                mensagem = f"Usuário '{nome}' cadastrado com sucesso!"

            db.executar(sql, params)
            db.commitar()
            db.desconectar()

            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()
        else:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
