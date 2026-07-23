import _path  # noqa: F401

import math
from datetime import datetime as _dt

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


def _fmt_date(val):
    if not val:
        return "--"
    if hasattr(val, "strftime"):
        return val.strftime("%d/%m/%Y")
    try:
        return _dt.strptime(str(val), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(val)


def _fmt_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class CircularProgressBar(ctk.CTkFrame):
    def __init__(self, master, size=160, thickness=14, **kwargs):
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)
        self.pack_propagate(False)
        self.canvas = ctk.CTkCanvas(self, width=size, height=size, highlightthickness=0, bg=COLORS["white"])
        self.canvas.pack(expand=True)
        self.size = size
        self.thickness = thickness
        self.center = size // 2
        self.radius = (size - thickness) // 2
        self._pct = 0.0

    def set_progress(self, pct, text="0%", subtext=""):
        self._pct = max(0.0, min(1.0, pct))
        self.canvas.delete("all")
        c = self.center
        r = self.radius
        t = self.thickness

        self.canvas.create_oval(
            c - r, c - r, c + r, c + r,
            outline=COLORS["border"], width=t,
        )

        if self._pct > 0:
            start = -90
            extent = 360 * self._pct
            self.canvas.create_arc(
                c - r, c - r, c + r, c + r,
                start=start, extent=extent,
                outline=COLORS["primary"], width=t, style="arc",
            )

        self.canvas.create_text(c, c - 8, text=text, fill=COLORS["text"],
                                font=ctk.CTkFont(size=20, weight="bold"))
        self.canvas.create_text(c, c + 16, text=subtext, fill=COLORS["text_muted"],
                                font=ctk.CTkFont(size=10))


class ModalCadastrarInfrator(ctk.CTkToplevel):
    def __init__(self, master, onSalvar=None):
        super().__init__(master)
        self.title("Cadastrar Infrator")
        self.geometry("420x380")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.onSalvar = onSalvar

        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=50, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Novo Infrator",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color="white").pack(side="left", padx=20)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=16)

        self.entries = {}
        campos = [
            ("nome", "Nome Completo"),
            ("cpf", "CPF (11 digitos)"),
            ("email", "E-mail"),
            ("telefone", "Telefone"),
        ]

        for key, label in campos:
            ctk.CTkLabel(form, text=label,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w", pady=(10, 2))
            entry = ctk.CTkEntry(form, height=38, corner_radius=4,
                                 border_width=1, border_color=COLORS["border"],
                                 fg_color=COLORS["white"], text_color=COLORS["text"])
            entry.pack(fill="x")
            self.entries[key] = entry

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text="Salvar", height=36, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._salvar,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", height=36, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).pack(side="right")

    def _salvar(self):
        from tkinter import messagebox

        nome = self.entries["nome"].get().strip()
        cpf = self.entries["cpf"].get().strip()
        email = self.entries["email"].get().strip()
        telefone = self.entries["telefone"].get().strip()

        if not all([nome, cpf, email]):
            messagebox.showwarning("Atencao", "Preencha nome, CPF e email!", parent=self)
            return

        if len(cpf) != 11 or not cpf.isdigit():
            messagebox.showerror("Erro", "CPF deve conter 11 digitos!", parent=self)
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco!", parent=self)
                return
            try:
                db.executar(
                    "INSERT INTO infrator (cpf, email, senha, nome_infrator, telefone_infrator) VALUES (?, ?, '', ?, ?)",
                    (cpf, email, nome, telefone or None),
                )
                db.commitar()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar infrator:\n{e}", parent=self)
                return

        messagebox.showinfo("Sucesso", "Infrator cadastrado com sucesso!", parent=self)
        if self.onSalvar:
            self.onSalvar()
        self.destroy()


class ModalCadastrarAgente(ctk.CTkToplevel):
    def __init__(self, master, onSalvar=None):
        super().__init__(master)
        self.title("Cadastrar Agente IBAMA")
        self.geometry("420x420")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.onSalvar = onSalvar

        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=50, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Novo Agente IBAMA",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color="white").pack(side="left", padx=20)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=16)

        self.entries = {}
        campos = [
            ("matricula", "Matricula"),
            ("nome", "Nome Completo"),
            ("cpf", "CPF (11 digitos)"),
            ("email", "E-mail"),
            ("login", "Login"),
            ("senha", "Senha"),
        ]

        for key, label in campos:
            ctk.CTkLabel(form, text=label,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, corner_radius=4,
                                 border_width=1, border_color=COLORS["border"],
                                 fg_color=COLORS["white"], text_color=COLORS["text"],
                                 show="*" if key == "senha" else "")
            entry.pack(fill="x")
            self.entries[key] = entry

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text="Salvar", height=36, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._salvar,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", height=36, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).pack(side="right")

    def _salvar(self):
        from tkinter import messagebox
        import hashlib

        matricula = self.entries["matricula"].get().strip()
        nome = self.entries["nome"].get().strip()
        cpf = self.entries["cpf"].get().strip()
        email = self.entries["email"].get().strip()
        login = self.entries["login"].get().strip()
        senha = self.entries["senha"].get().strip()

        if not all([matricula, nome, cpf, email, login, senha]):
            messagebox.showwarning("Atencao", "Preencha todos os campos!", parent=self)
            return

        if len(cpf) != 11 or not cpf.isdigit():
            messagebox.showerror("Erro", "CPF deve conter 11 digitos!", parent=self)
            return

        try:
            matricula_val = int(matricula)
        except ValueError:
            messagebox.showerror("Erro", "Matricula deve ser um numero!", parent=self)
            return

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco!", parent=self)
                return
            try:
                db.executar(
                    """INSERT INTO "agente ibama"
                       (matricula, login, senha, email, nome_agente, cpf, perfil, status)
                       VALUES (?, ?, ?, ?, ?, ?, 'agente', 'ativo')""",
                    (matricula_val, login, senha_hash, email, nome, cpf),
                )
                db.commitar()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar agente:\n{e}", parent=self)
                return

        messagebox.showinfo("Sucesso", "Agente cadastrado com sucesso!", parent=self)
        if self.onSalvar:
            self.onSalvar()
        self.destroy()


class ModalCadastrarTCCM(ctk.CTkToplevel):
    def __init__(self, master, onSalvar=None):
        super().__init__(master)
        self.title("Cadastrar Novo TCCM")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()
        self.onSalvar = onSalvar

        self.agentes = []
        self.infratores = []
        self.itens_lista = []

        self._carregar_dados_combobox()

        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Cadastrar Novo TCCM",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      text_color="white").pack(side="left", padx=20)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=(12, 0))

        left_panel = ctk.CTkScrollableFrame(body, fg_color="transparent", width=480)
        left_panel.pack(side="left", fill="y", padx=(0, 16))
        left_panel.pack_propagate(False)

        right_panel = ctk.CTkFrame(body, fg_color="transparent")
        right_panel.pack(side="left", fill="both", expand=True)

        self.entries = {}

        ctk.CTkLabel(left_panel, text="Dados do Processo",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(left_panel, text="Processo*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        entry = ctk.CTkEntry(left_panel, height=38, corner_radius=4,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: PROC-2026-005")
        entry.pack(fill="x")
        self.entries["processo"] = entry

        ctk.CTkLabel(left_panel, text="Documento SEI (opcional)",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        entry = ctk.CTkEntry(left_panel, height=38, corner_radius=4,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: SEI-001/2026")
        entry.pack(fill="x")
        self.entries["documento_sei"] = entry

        row = ctk.CTkFrame(left_panel, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=(0, 10))

        ctk.CTkLabel(left, text="Data de Inicio*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")
        entry = ctk.CTkEntry(left, height=38, corner_radius=4,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="DD/MM/AAAA", width=200)
        entry.pack(anchor="w")
        self.entries["data_inicio"] = entry

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(right, text="Semestres*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")
        entry = ctk.CTkEntry(right, height=38, corner_radius=4,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: 4", width=200)
        entry.pack(anchor="w")
        self.entries["semestres"] = entry

        ctk.CTkLabel(left_panel, text="Agente Responsavel*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(8, 2))

        agente_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        agente_row.pack(fill="x")
        agente_row.grid_columnconfigure(0, weight=1)

        opcoes_agentes = [f"{a[0]} - {a[1]}" for a in self.agentes] if self.agentes else ["Nenhum agente"]
        combo = ctk.CTkComboBox(agente_row, values=opcoes_agentes,
                                height=38, corner_radius=4,
                                fg_color=COLORS["white"], border_color=COLORS["border"],
                                button_color=COLORS["primary"],
                                dropdown_fg_color=COLORS["white"])
        combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entries["agente_matricula"] = combo

        ctk.CTkButton(
            agente_row, text="+ Cadastrar", height=38, width=100, corner_radius=4,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", font=ctk.CTkFont(size=11, weight="bold"),
            command=self._abrir_cadastrar_agente,
        ).grid(row=0, column=1)

        ctk.CTkLabel(left_panel, text="Infrator*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(8, 2))

        infrator_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        infrator_row.pack(fill="x")
        infrator_row.grid_columnconfigure(0, weight=1)

        opcoes_infratores = [f"{i[0]} - {i[1]}" for i in self.infratores] if self.infratores else ["Nenhum infrator"]
        combo = ctk.CTkComboBox(infrator_row, values=opcoes_infratores,
                                height=38, corner_radius=4,
                                fg_color=COLORS["white"], border_color=COLORS["border"],
                                button_color=COLORS["primary"],
                                dropdown_fg_color=COLORS["white"])
        combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entries["infrator_id"] = combo

        ctk.CTkButton(
            infrator_row, text="+ Cadastrar", height=38, width=100, corner_radius=4,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", font=ctk.CTkFont(size=11, weight="bold"),
            command=self._abrir_cadastrar_infrator,
        ).grid(row=0, column=1)

        ctk.CTkLabel(right_panel, text="Itens do TCCM",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", pady=(0, 8))

        itens_form = ctk.CTkFrame(right_panel, fg_color=COLORS["white"], corner_radius=6,
                                   border_width=1, border_color=COLORS["border"])
        itens_form.pack(fill="x", pady=(0, 8))

        itens_inner = ctk.CTkFrame(itens_form, fg_color="transparent")
        itens_inner.pack(fill="x", padx=12, pady=10)
        itens_inner.grid_columnconfigure(0, weight=2)
        itens_inner.grid_columnconfigure(1, weight=2)
        itens_inner.grid_columnconfigure(2, weight=1)
        itens_inner.grid_columnconfigure(3, weight=1)
        itens_inner.grid_columnconfigure(4, weight=0)

        ctk.CTkLabel(itens_inner, text="Nome*",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.entry_item_nome = ctk.CTkEntry(itens_inner, height=32, corner_radius=4,
                                            border_width=1, border_color=COLORS["border"],
                                            fg_color=COLORS["white"], text_color=COLORS["text"],
                                            placeholder_text="Nome do item")
        self.entry_item_nome.grid(row=1, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkLabel(itens_inner, text="Descricao*",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(0, 4))
        self.entry_item_desc = ctk.CTkEntry(itens_inner, height=32, corner_radius=4,
                                            border_width=1, border_color=COLORS["border"],
                                            fg_color=COLORS["white"], text_color=COLORS["text"],
                                            placeholder_text="Descricao")
        self.entry_item_desc.grid(row=1, column=1, sticky="ew", padx=(0, 4))

        ctk.CTkLabel(itens_inner, text="Qtd.*",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.entry_item_qtd = ctk.CTkEntry(itens_inner, height=32, corner_radius=4,
                                           border_width=1, border_color=COLORS["border"],
                                           fg_color=COLORS["white"], text_color=COLORS["text"],
                                           placeholder_text="0", width=70)
        self.entry_item_qtd.grid(row=1, column=2, sticky="ew", padx=(0, 4))

        ctk.CTkLabel(itens_inner, text="Unidade",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=3, sticky="w", padx=(0, 4))
        self.entry_item_unidade = ctk.CTkEntry(itens_inner, height=32, corner_radius=4,
                                               border_width=1, border_color=COLORS["border"],
                                               fg_color=COLORS["white"], text_color=COLORS["text"],
                                               placeholder_text="Unidade", width=90)
        self.entry_item_unidade.grid(row=1, column=3, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            itens_inner, text="+", width=32, height=32, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=16, weight="bold"),
            command=self._adicionar_item,
        ).grid(row=1, column=4, padx=(4, 0))

        self.itens_container = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.itens_container.pack(fill="both", expand=True)

        self._renderizar_itens()

        btn_frame = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=0,
                                  border_width=1, border_color=COLORS["border"])
        btn_frame.pack(fill="x", padx=0, pady=0, side="bottom")

        inner_btn = ctk.CTkFrame(btn_frame, fg_color="transparent")
        inner_btn.pack(fill="x", padx=24, pady=12)

        ctk.CTkButton(
            inner_btn, text="Salvar TCCM", height=42, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._salvar,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            inner_btn, text="Cancelar", height=42, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=14),
            command=self.destroy,
        ).pack(side="right")

    def _carregar_dados_combobox(self):
        with Database() as db:
            if not db.conexao:
                return
            try:
                r = db.executar("SELECT matricula, nome_agente FROM \"agente ibama\" WHERE status = 'ativo'")
                if r:
                    self.agentes = [(row[0], row[1]) for row in r.fetchall()]
            except Exception:
                self.agentes = []
            try:
                r = db.executar("SELECT id_infrator, nome_infrator FROM infrator")
                if r:
                    self.infratores = [(row[0], row[1]) for row in r.fetchall()]
            except Exception:
                self.infratores = []

    def _atualizar_combos(self):
        self._carregar_dados_combobox()
        self.entries["agente_matricula"].configure(
            values=[f"{a[0]} - {a[1]}" for a in self.agentes] if self.agentes else ["Nenhum agente"]
        )
        self.entries["infrator_id"].configure(
            values=[f"{i[0]} - {i[1]}" for i in self.infratores] if self.infratores else ["Nenhum infrator"]
        )

    def _abrir_cadastrar_agente(self):
        ModalCadastrarAgente(self, onSalvar=self._atualizar_combos)

    def _abrir_cadastrar_infrator(self):
        ModalCadastrarInfrator(self, onSalvar=self._atualizar_combos)

    def _adicionar_item(self):
        from tkinter import messagebox

        nome = self.entry_item_nome.get().strip()
        desc = self.entry_item_desc.get().strip()
        qtd = self.entry_item_qtd.get().strip()
        unidade = self.entry_item_unidade.get().strip()

        if not all([nome, desc, qtd]):
            messagebox.showwarning("Atencao", "Preencha nome, descricao e quantidade do item!", parent=self)
            return

        try:
            qtd_val = int(qtd)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um numero inteiro!", parent=self)
            return

        self.itens_lista.append({
            "nome": nome,
            "descricao": desc,
            "quantidade": qtd_val,
            "unidade": unidade or "Unidade",
        })

        self.entry_item_nome.delete(0, "end")
        self.entry_item_desc.delete(0, "end")
        self.entry_item_qtd.delete(0, "end")
        self.entry_item_unidade.delete(0, "end")

        self._renderizar_itens()

    def _remover_item(self, idx):
        self.itens_lista.pop(idx)
        self._renderizar_itens()

    def _renderizar_itens(self):
        for w in self.itens_container.winfo_children():
            w.destroy()

        if not self.itens_lista:
            ctk.CTkLabel(self.itens_container, text="Nenhum item adicionado",
                          font=ctk.CTkFont(size=FONTS["size_small"]),
                          text_color=COLORS["text_muted"]).pack(pady=20)
            return

        hdr = ctk.CTkFrame(self.itens_container, fg_color=COLORS["table_header"], height=30, corner_radius=4)
        hdr.pack(fill="x", pady=(0, 4))
        hdr.pack_propagate(False)
        hdr.grid_columnconfigure(0, weight=2)
        hdr.grid_columnconfigure(1, weight=2)
        hdr.grid_columnconfigure(2, weight=1)
        hdr.grid_columnconfigure(3, weight=1)
        hdr.grid_columnconfigure(4, weight=0)

        for i, col in enumerate(["Nome", "Descricao", "Qtd.", "Unidade", ""]):
            ctk.CTkLabel(hdr, text=col,
                          font=ctk.CTkFont(size=10, weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=8)

        for idx, item in enumerate(self.itens_lista):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row = ctk.CTkFrame(self.itens_container, fg_color=row_bg, height=32, corner_radius=0)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, weight=1)
            row.grid_columnconfigure(4, weight=0)

            dados = [item["nome"], item["descricao"], str(item["quantidade"]), item["unidade"]]
            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(row, text=valor,
                              font=ctk.CTkFont(size=11),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=8)

            ctk.CTkButton(
                row, text="\u2715", width=28, height=24, corner_radius=4,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color="white", font=ctk.CTkFont(size=11),
                command=lambda idx=idx: self._remover_item(idx),
            ).grid(row=0, column=4, padx=(4, 8))

    def _salvar(self):
        from tkinter import messagebox
        from datetime import datetime

        processo = self.entries["processo"].get().strip()
        documento_sei = self.entries["documento_sei"].get().strip()
        data_inicio = self.entries["data_inicio"].get().strip()
        semestres = self.entries["semestres"].get().strip()

        agente_str = self.entries["agente_matricula"].get().strip()
        infrator_str = self.entries["infrator_id"].get().strip()

        if not all([processo, data_inicio, semestres]):
            messagebox.showwarning("Atencao", "Preencha processo, data de inicio e semestres!", parent=self)
            return

        if " - " not in agente_str or " - " not in infrator_str:
            messagebox.showwarning("Atencao", "Selecione agente e infrator!", parent=self)
            return

        try:
            semestres_val = int(semestres)
        except ValueError:
            messagebox.showerror("Erro", "Semestres deve ser um numero inteiro!", parent=self)
            return

        try:
            data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
            data_inicio_db = data_inicio_dt.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data invalida! Use o formato DD/MM/AAAA.", parent=self)
            return

        agente_matricula = int(agente_str.split(" - ")[0])
        infrator_id = int(infrator_str.split(" - ")[0])

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco!", parent=self)
                return
            try:
                sql = """INSERT INTO tccm
                    (processo, documento_sei, data_inicio, semestres,
                     total_pago, total_validado, total_devido,
                     data_validade, intervalo, status,
                     "agente ibama_matricula", "infrator_id_infrator")
                    VALUES (?, ?, ?, ?, 0.00, 0.00, 0.00,
                            NULL, ?, 'pendente', ?, ?)"""
                db.executar(sql, (processo, documento_sei or None, data_inicio_db,
                                  semestres_val, semestres_val,
                                  agente_matricula, infrator_id))

                for item in self.itens_lista:
                    sql_item = """INSERT INTO itens (nome, descricao, codigo_interno, unidade_medida,
                                                    quantidade_prevista, status)
                                  VALUES (?, ?, ?, ?, ?, 'Ativo')"""
                    db.executar(sql_item, (item["nome"], item["descricao"],
                                           f"{processo}-{item['nome'][:10].upper()}",
                                           item["unidade"], item["quantidade"]))

                db.commitar()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar TCCM:\n{e}", parent=self)
                return

        messagebox.showinfo("Sucesso", "TCCM cadastrado com sucesso!", parent=self)

        if self.onSalvar:
            self.onSalvar()
        self.destroy()


class TccmDetalhesPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, processo, on_voltar=None, usuario_logado=None, perfil="admin", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.processo = processo
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        self.tccm_data = None
        self.notas = []
        self.itens = []

        self._carregar_dados()

        self.build_header_detalhes()
        self.build_info_section()
        self.build_pessoas_section()
        self.build_notas_section()
        self.build_itens_section()

    def build_header_detalhes(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkButton(
            left, text="\u2190 Voltar", height=36, corner_radius=6,
            fg_color=COLORS["dark"], hover_color=COLORS["dark_hover"],
            text_color="white", font=ctk.CTkFont(size=12),
            command=self._voltar,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(left, text=f"Detalhes TCCM - {self.processo}",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

    def build_info_section(self):
        if not self.tccm_data:
            return

        t = self.tccm_data
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Informacoes do TCCM",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        pct = (t["total_pago"] / t["total_devido"] * 100) if t["total_devido"] > 0 else 0
        progress_frame = ctk.CTkFrame(section, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 12))

        progress_bar_bg = ctk.CTkFrame(progress_frame, fg_color=COLORS["border"], height=8, corner_radius=4)
        progress_bar_bg.pack(fill="x")

        bar_width = max(1, int(pct / 100 * 1000))
        progress_bar_fg = ctk.CTkFrame(progress_bar_bg, fg_color=COLORS["primary"], height=8, corner_radius=4)
        progress_bar_fg.place(x=0, y=0, relwidth=pct / 100, relheight=1)

        ctk.CTkLabel(progress_frame, text=f"{pct:.1f}% pago",
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(anchor="e", pady=(4, 0))

        info_grid = ctk.CTkFrame(section, fg_color="transparent")
        info_grid.pack(fill="x", padx=15, pady=(0, 15))
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)
        info_grid.grid_columnconfigure(2, weight=1)
        info_grid.grid_columnconfigure(3, weight=1)

        campos = [
            ("Processo", t["processo"]),
            ("Status", t["status"].capitalize()),
            ("Documento SEI", t.get("documento_sei", "--")),
            ("Data Inicio", t.get("data_inicio", "--")),
            ("Semestres", f"{t.get('semestres', 0)}"),
            ("Data Validade", t["data_validade"]),
            ("Intervalo", f"{t['intervalo']} meses"),
            ("Total Devido", _fmt_brl(t["total_devido"])),
            ("Total Pago", _fmt_brl(t["total_pago"])),
            ("Total Validado", _fmt_brl(t["total_validado"])),
            ("Total Pendente", _fmt_brl(max(0, t["total_devido"] - t["total_pago"]))),
        ]

        for i, (label, valor) in enumerate(campos):
            row = i // 4
            col = i % 4
            frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            frame.grid(row=row, column=col, padx=5, pady=4, sticky="w")

            ctk.CTkLabel(frame, text=label,
                          font=ctk.CTkFont(size=10),
                          text_color=COLORS["text_muted"]).pack(anchor="w")
            ctk.CTkLabel(frame, text=valor,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w")

    def build_pessoas_section(self):
        if not self.tccm_data:
            return

        t = self.tccm_data
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["warning"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Pessoas Envolvidas",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 15))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        inf_frame = ctk.CTkFrame(grid, fg_color=COLORS["bg"], corner_radius=6)
        inf_frame.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

        ctk.CTkLabel(inf_frame, text="Infrator",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", padx=12, pady=(10, 2))

        campos_inf = [
            ("Nome", t.get("infrator_nome", "--")),
            ("CPF", t.get("infrator_cpf", "--")),
            ("Email", t.get("infrator_email", "--")),
            ("Telefone", t.get("infrator_telefone", "--")),
        ]
        for label, valor in campos_inf:
            ctk.CTkLabel(inf_frame, text=f"{label}: {valor}",
                          font=ctk.CTkFont(size=FONTS["size_small"]),
                          text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=1)
        ctk.CTkFrame(inf_frame, fg_color="transparent").pack(pady=(0, 8))

        age_frame = ctk.CTkFrame(grid, fg_color=COLORS["bg"], corner_radius=6)
        age_frame.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")

        ctk.CTkLabel(age_frame, text="Agente IBAMA",
                      font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", padx=12, pady=(10, 2))

        campos_age = [
            ("Nome", t.get("agente_nome", "--")),
            ("Matricula", str(t.get("agente_matricula", "--"))),
            ("CPF", t.get("agente_cpf", "--")),
            ("Email", t.get("agente_email", "--")),
        ]
        for label, valor in campos_age:
            ctk.CTkLabel(age_frame, text=f"{label}: {valor}",
                          font=ctk.CTkFont(size=FONTS["size_small"]),
                          text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=1)
        ctk.CTkFrame(age_frame, fg_color="transparent").pack(pady=(0, 8))

    def build_notas_section(self):
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["success_dark"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text=f"Notas Fiscais ({len(self.notas)})",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        if not self.notas:
            ctk.CTkLabel(section, text="Nenhuma nota fiscal vinculada a este TCCM",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=25)
            return

        table_frame = ctk.CTkFrame(section, fg_color="transparent")
        table_frame.pack(fill="x", padx=15, pady=(0, 15))

        colunas = ["Nota Fiscal", "Data", "Valor Total", "Status"]
        col_weights = [3, 2, 2, 2]

        col_header = ctk.CTkFrame(table_frame, fg_color=COLORS["table_header"], height=32, corner_radius=0)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        cols = ctk.CTkFrame(col_header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(col_weights):
            cols.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(colunas):
            ctk.CTkLabel(cols, text=col,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=8)

        for idx, nota in enumerate(self.notas):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_bg, height=36)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)

            row_cols = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
            for i, w in enumerate(col_weights):
                row_cols.grid_columnconfigure(i, weight=w)

            st = nota["status"]
            if st == "Aprovada":
                st_cor = COLORS["success_dark"]
            elif st == "Rejeitada":
                st_cor = COLORS["danger"]
            else:
                st_cor = COLORS["warning"]

            dados = [
                (nota["nota_fiscal"], COLORS["text"]),
                (nota["data"], COLORS["text_muted"]),
                (_fmt_brl(nota["valor_total"]), COLORS["text"]),
            ]
            for i, (valor, cor) in enumerate(dados):
                ctk.CTkLabel(row_cols, text=valor,
                              font=ctk.CTkFont(size=11),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=8)

            st_frame = ctk.CTkFrame(row_cols, fg_color="transparent")
            st_frame.grid(row=0, column=3, sticky="w", padx=8)

            ctk.CTkLabel(st_frame, text=st,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=st_cor).pack(side="left")

    def build_itens_section(self):
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 25))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["warning"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text=f"Itens ({len(self.itens)})",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        if not self.itens:
            ctk.CTkLabel(section, text="Nenhum item vinculado a este TCCM",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=25)
            return

        table_frame = ctk.CTkFrame(section, fg_color="transparent")
        table_frame.pack(fill="x", padx=15, pady=(0, 15))

        colunas = ["Item", "Nota Fiscal", "Qtd.", "Preco Unit.", "Subtotal"]
        col_weights = [4, 3, 1, 2, 2]

        col_header = ctk.CTkFrame(table_frame, fg_color=COLORS["table_header"], height=32, corner_radius=0)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        cols = ctk.CTkFrame(col_header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(col_weights):
            cols.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(colunas):
            ctk.CTkLabel(cols, text=col,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=8)

        for idx, item in enumerate(self.itens):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_bg, height=32)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)

            row_cols = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
            for i, w in enumerate(col_weights):
                row_cols.grid_columnconfigure(i, weight=w)

            subtotal = item["quantidade"] * item["preco_unitario"]
            dados = [
                (item["nome_item"], COLORS["text"]),
                (item["nota_fiscal"], COLORS["text_muted"]),
                (str(item["quantidade"]), COLORS["text_muted"]),
                (_fmt_brl(item["preco_unitario"]), COLORS["text_muted"]),
                (_fmt_brl(subtotal), COLORS["text"]),
            ]
            for i, (valor, cor) in enumerate(dados):
                ctk.CTkLabel(row_cols, text=valor,
                              font=ctk.CTkFont(size=11),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=8)

    def _carregar_dados(self):
        with Database() as db:
            if not db.conexao:
                return
            try:
                sql = """SELECT t.processo, t.documento_sei, t.data_inicio, t.semestres,
                                t.total_pago, t.total_validado, t.data_validade,
                                t.intervalo, t.total_devido, t.status,
                                t."agente ibama_matricula", t."infrator_id_infrator"
                         FROM tccm t WHERE t.processo = ?"""
                r = db.executar(sql, (self.processo,))
                row = r.fetchone() if r else None
                if not row:
                    return

                self.tccm_data = {
                    "processo": row[0],
                    "documento_sei": row[1] or "--",
                    "data_inicio": _fmt_date(row[2]),
                    "semestres": row[3] or 0,
                    "total_pago": float(row[4]) if row[4] else 0,
                    "total_validado": float(row[5]) if row[5] else 0,
                    "data_validade": _fmt_date(row[6]),
                    "intervalo": row[7] or 0,
                    "total_devido": float(row[8]) if row[8] else 0,
                    "status": row[9] or "pendente",
                    "agente_matricula": row[10],
                    "infrator_id": row[11],
                }

                try:
                    r = db.executar('SELECT nome_infrator, cpf, email, telefone_infrator FROM infrator WHERE id_infrator = ?',
                                    (self.tccm_data["infrator_id"],))
                    inf = r.fetchone() if r else None
                    if inf:
                        self.tccm_data["infrator_nome"] = inf[0] or "--"
                        self.tccm_data["infrator_cpf"] = inf[1] or "--"
                        self.tccm_data["infrator_email"] = inf[2] or "--"
                        self.tccm_data["infrator_telefone"] = inf[3] or "--"
                except Exception:
                    self.tccm_data["infrator_nome"] = "--"

                try:
                    r = db.executar('SELECT nome_agente, cpf, email FROM "agente ibama" WHERE matricula = ?',
                                    (self.tccm_data["agente_matricula"],))
                    age = r.fetchone() if r else None
                    if age:
                        self.tccm_data["agente_nome"] = age[0] or "--"
                        self.tccm_data["agente_cpf"] = age[1] or "--"
                        self.tccm_data["agente_email"] = age[2] or "--"
                except Exception:
                    self.tccm_data["agente_nome"] = "--"

            except Exception:
                self.tccm_data = None

            try:
                sql = """SELECT nf.nota_fiscal, nf.data, nf.chave_de_acesso,
                                nf.valor_total, nf.status_nota
                         FROM "nota fiscal" nf
                         WHERE nf.processo = ?
                         ORDER BY nf.data DESC"""
                r = db.executar(sql, (self.processo,))
                if r:
                    for row in r.fetchall():
                        self.notas.append({
                            "nota_fiscal": row[0] or "--",
                            "data": _fmt_date(row[1]),
                            "chave_acesso": row[2] or "--",
                            "valor_total": float(row[3]) if row[3] else 0,
                            "status": row[4] or "Pendente",
                        })
            except Exception:
                pass

            try:
                sql = """SELECT p.nome_item, p.quantidade, p.preco_unitario,
                                p."nota fiscal_nota_fiscal"
                         FROM produtos p
                         WHERE p."nota fiscal_nota_fiscal" IN (
                             SELECT nf.nota_fiscal FROM "nota fiscal" nf WHERE nf.processo = ?
                         )"""
                r = db.executar(sql, (self.processo,))
                if r:
                    for row in r.fetchall():
                        self.itens.append({
                            "nome_item": row[0] or "--",
                            "quantidade": row[1] or 0,
                            "preco_unitario": float(row[2]) if row[2] else 0,
                            "nota_fiscal": row[3] or "--",
                        })
            except Exception:
                pass

    def _voltar(self):
        if self.on_voltar:
            self.on_voltar()


class TccmDashboardPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, perfil="admin", **kwargs):
        self.on_selecionar = kwargs.pop("on_selecionar", None)
        self.on_sair = kwargs.pop("on_sair", None)
        self.on_cadastrar = kwargs.pop("on_cadastrar", None)
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        self.tccms_todos = []

        self._build_header_custom()
        self._build_status_cards()
        self._build_lista_tccms()

    def _build_header_custom(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(left, text="Painel Geral",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        ctk.CTkLabel(left, text="  Visao consolidada dos Termos de Coordenacao e Controle de Material",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(side="left", padx=(8, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(
            right, text="+ Novo TCCM", height=36, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._navegar_cadastro,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right, text="Sair", height=36, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._sair,
        ).pack(side="left")

    def _build_status_cards(self):
        self._cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._cards_frame.pack(fill="x", padx=30, pady=(0, 15))

        for i in range(2):
            self._cards_frame.grid_columnconfigure(i, weight=1)

        self._card_pendentes = self._criar_card_status(self._cards_frame, "Pendentes", "0", COLORS["warning"], 0)
        self._card_concluidos = self._criar_card_status(self._cards_frame, "Concluidos", "0", COLORS["success_dark"], 1)

    def _criar_card_status(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=6,
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=0, column=col, padx=5, sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 4))

        dot = ctk.CTkFrame(top, fg_color=cor, width=8, height=8, corner_radius=4)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(top, text=titulo,
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(side="left")

        lbl = ctk.CTkLabel(card, text=valor,
                           font=ctk.CTkFont(size=28, weight="bold"),
                           text_color=COLORS["text"])
        lbl.pack(anchor="w", padx=14, pady=(0, 12))

        return card, lbl

    def _build_progress_section(self):
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=6,
                               border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 4))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=8, height=8, corner_radius=4)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Progresso Geral de Arrecadacao",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        self._lbl_pct = ctk.CTkLabel(hdr, text="0%",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color=COLORS["primary"])
        self._lbl_pct.pack(side="right")

        bar_frame = ctk.CTkFrame(section, fg_color="transparent")
        bar_frame.pack(fill="x", padx=15, pady=(4, 4))

        self._bar_bg = ctk.CTkFrame(bar_frame, fg_color=COLORS["border"], height=12, corner_radius=6)
        self._bar_bg.pack(fill="x")
        self._bar_bg.pack_propagate(False)

        self._bar_fg = ctk.CTkFrame(self._bar_bg, fg_color=COLORS["primary"], height=12, corner_radius=6)
        self._bar_fg.place(x=0, y=0, relwidth=0, relheight=1)

        totals_frame = ctk.CTkFrame(section, fg_color="transparent")
        totals_frame.pack(fill="x", padx=15, pady=(4, 12))
        totals_frame.grid_columnconfigure(0, weight=1)
        totals_frame.grid_columnconfigure(1, weight=1)
        totals_frame.grid_columnconfigure(2, weight=1)

        self._lbl_devido = ctk.CTkLabel(totals_frame, text="Total Devido: R$ 0,00",
                                         font=ctk.CTkFont(size=FONTS["size_small"]),
                                         text_color=COLORS["text_muted"])
        self._lbl_devido.grid(row=0, column=0, sticky="w")

        self._lbl_pago = ctk.CTkLabel(totals_frame, text="Total Pago: R$ 0,00",
                                       font=ctk.CTkFont(size=FONTS["size_small"]),
                                       text_color=COLORS["text_muted"])
        self._lbl_pago.grid(row=0, column=1, sticky="w")

        self._lbl_pendente = ctk.CTkLabel(totals_frame, text="Pendente: R$ 0,00",
                                           font=ctk.CTkFont(size=FONTS["size_small"]),
                                           text_color=COLORS["text_muted"])
        self._lbl_pendente.grid(row=0, column=2, sticky="w")

    def _build_lista_tccms(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header_row,
            text="Todos os TCCMs",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            header_row, text="",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["primary"],
        )
        self.lbl_count.pack(side="right", padx=(0, 12))

        filter_frame = ctk.CTkFrame(header_row, fg_color="transparent")
        filter_frame.pack(side="right")

        ctk.CTkLabel(filter_frame, text="Filtrar:",
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 6))

        self.entry_filtro = ctk.CTkEntry(
            filter_frame, height=32, width=220, corner_radius=6,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="Processo, infrator ou status...",
        )
        self.entry_filtro.pack(side="left")
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tccms())

        col_header = ctk.CTkFrame(container, fg_color=COLORS["table_header"], height=36, corner_radius=4)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        cols = ctk.CTkFrame(col_header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(15, 0))
        weights = [2, 3, 2, 2, 2, 2, 1]
        for w in weights:
            cols.grid_columnconfigure(cols.grid_size()[1], weight=w)

        for i, col in enumerate(["Processo", "Infrator", "Total Devido", "Total Pago", "Validade", "Status", ""]):
            ctk.CTkLabel(cols, text=col,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=8)

        self.table_body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True)

        self._carregar_tccms()

    def _carregar_tccms(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        tccms = []
        qtd_pendentes = 0
        qtd_concluidos = 0

        with Database() as db:
            if not db.conexao:
                return
            try:
                sql = """SELECT t.processo, t.total_pago, t.total_devido, t.status,
                                t.data_validade, t.intervalo,
                                i.nome_infrator, i.cpf
                         FROM tccm t
                         LEFT JOIN infrator i ON i.id_infrator = t."infrator_id_infrator"
                         ORDER BY t.processo"""
                r = db.executar(sql)
                if r:
                    for row in r.fetchall():
                        status = row[3] or "pendente"
                        td = float(row[2]) if row[2] else 0
                        tp = float(row[1]) if row[1] else 0

                        if status == "concluido":
                            qtd_concluidos += 1
                        else:
                            qtd_pendentes += 1

                        tccms.append({
                            "processo": row[0] or "--",
                            "total_pago": tp,
                            "total_devido": td,
                            "status": status,
                            "data_validade": _fmt_date(row[4]),
                            "intervalo": row[5] or 0,
                            "infrator": row[6] or "--",
                            "cpf": row[7] or "--",
                        })
            except Exception:
                pass

        self.tccms_todos = tccms
        self.lbl_count.configure(text=f"{len(tccms)} TCCM(s)")

        self._card_pendentes[1].configure(text=str(qtd_pendentes))
        self._card_concluidos[1].configure(text=str(qtd_concluidos))

        self._filtrar_tccms()

    def _filtrar_tccms(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        termo = self.entry_filtro.get().strip().lower()
        filtrados = self.tccms_todos
        if termo:
            filtrados = [t for t in self.tccms_todos
                         if termo in t["processo"].lower()
                         or termo in t["infrator"].lower()
                         or termo in t["status"].lower()
                         or termo in t["cpf"].lower()]

        self.lbl_count.configure(text=f"{len(filtrados)} TCCM(s)")

        if not filtrados:
            ctk.CTkLabel(self.table_body, text="Nenhum TCCM encontrado",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=40)
            return

        for idx, t in enumerate(filtrados):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row = ctk.CTkFrame(self.table_body, fg_color=row_bg, height=40,
                                corner_radius=0, cursor="hand2")
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            row.bind("<Button-1>", lambda e, proc=t["processo"]: self._selecionar(proc))

            cols = ctk.CTkFrame(row, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(15, 0))
            weights = [2, 3, 2, 2, 2, 2, 1]
            for w in weights:
                cols.grid_columnconfigure(cols.grid_size()[1], weight=w)

            if t["status"] == "concluido":
                st_text = "Concluido"
                st_cor = COLORS["success_dark"]
            elif t["status"] == "pago_parcial":
                st_text = "Parcial"
                st_cor = "#FF9800"
            else:
                st_text = "Pendente"
                st_cor = COLORS["warning"]

            dados = [
                t["processo"], t["infrator"],
                _fmt_brl(t["total_devido"]), _fmt_brl(t["total_pago"]),
                t["data_validade"], st_text,
            ]
            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else (st_cor if i == 5 else COLORS["text_muted"])
                weight = "bold" if i == 0 or i == 5 else "normal"
                ctk.CTkLabel(cols, text=valor,
                              font=ctk.CTkFont(size=FONTS["size_small"], weight=weight),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=8)

            ctk.CTkButton(
                row, text="\u25b6", width=32, height=28,
                corner_radius=4, fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"], text_color="white",
                font=ctk.CTkFont(size=12),
                command=lambda proc=t["processo"]: self._selecionar(proc),
            ).pack(side="right", padx=(0, 15))

    def _selecionar(self, processo):
        if self.on_selecionar:
            self.on_selecionar(processo)

    def _navegar_cadastro(self):
        if self.on_cadastrar:
            self.on_cadastrar()
        else:
            ModalCadastrarTCCM(self, onSalvar=self._recarregar)

    def _recarregar(self):
        for w in self.table_body.winfo_children():
            w.destroy()
        self._carregar_tccms()

    def _sair(self):
        if self.on_sair:
            self.on_sair()
