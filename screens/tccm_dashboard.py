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


class ModalCadastrarTCCM(ctk.CTkToplevel):
    def __init__(self, master, onSalvar=None):
        super().__init__(master)
        self.title("Cadastrar Novo TCCM")
        self.geometry("520x520")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.onSalvar = onSalvar

        self.agentes = []
        self.infratores = []

        self._carregar_dados_combobox()

        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Novo TCCM",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      text_color="white").pack(side="left", padx=20)

        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=16)

        self.entries = {}

        campos = [
            ("processo", "Processo (ex: PROC-2026-005)", "entry"),
            ("total_devido", "Total Devido (R$)", "entry"),
            ("total_validado", "Total Validado (R$)", "entry"),
            ("data_validade", "Data Validade (AAAA-MM-DD)", "entry"),
            ("intervalo", "Intervalo (meses)", "entry"),
            ("agente_matricula", "Agente Responsavel", "combo_agente"),
            ("infrator_id", "Infrator", "combo_infrator"),
        ]

        for key, label, tipo in campos:
            ctk.CTkLabel(form, text=label,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w", pady=(10, 2))

            if tipo == "entry":
                entry = ctk.CTkEntry(form, height=38, corner_radius=4,
                                     border_width=1, border_color=COLORS["border"],
                                     fg_color=COLORS["white"], text_color=COLORS["text"])
                entry.pack(fill="x")
                self.entries[key] = entry
            elif tipo == "combo_agente":
                opcoes = [f"{a[0]} - {a[1]}" for a in self.agentes]
                combo = ctk.CTkComboBox(form, values=opcoes if opcoes else ["Nenhum agente"],
                                        height=38, corner_radius=4,
                                        fg_color=COLORS["white"], border_color=COLORS["border"],
                                        button_color=COLORS["primary"],
                                        dropdown_fg_color=COLORS["white"])
                combo.pack(fill="x")
                self.entries[key] = combo
            elif tipo == "combo_infrator":
                opcoes = [f"{i[0]} - {i[1]}" for i in self.infratores]
                combo = ctk.CTkComboBox(form, values=opcoes if opcoes else ["Nenhum infrator"],
                                        height=38, corner_radius=4,
                                        fg_color=COLORS["white"], border_color=COLORS["border"],
                                        button_color=COLORS["primary"],
                                        dropdown_fg_color=COLORS["white"])
                combo.pack(fill="x")
                self.entries[key] = combo

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text="Salvar", height=40, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._salvar,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", height=40, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=14),
            command=self.destroy,
        ).pack(side="right")

    def _carregar_dados_combobox(self):
        with Database() as db:
            if not db.conexao:
                return
            try:
                r = db.executar('SELECT matricula, nome_agente FROM "agente ibama" WHERE status = "ativo"')
                if r:
                    self.agentes = [(row[0], row[1]) for row in r.fetchall()]
            except Exception:
                self.agentes = []
            try:
                r = db.executar('SELECT id_infrator, nome_infrator FROM infrator')
                if r:
                    self.infratores = [(row[0], row[1]) for row in r.fetchall()]
            except Exception:
                self.infratores = []

    def _salvar(self):
        processo = self.entries["processo"].get().strip()
        total_devido = self.entries["total_devido"].get().strip()
        total_validado = self.entries["total_validado"].get().strip()
        data_validade = self.entries["data_validade"].get().strip()
        intervalo = self.entries["intervalo"].get().strip()

        agente_str = self.entries["agente_matricula"].get().strip()
        infrator_str = self.entries["infrator_id"].get().strip()

        if not all([processo, total_devido, total_validado, intervalo]):
            from tkinter import messagebox
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios!", parent=self)
            return

        try:
            total_devido_val = float(total_devido.replace(",", "."))
            total_validado_val = float(total_validado.replace(",", "."))
            intervalo_val = int(intervalo)
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Erro", "Valores numericos invalidos!", parent=self)
            return

        agente_matricula = None
        if " - " in agente_str:
            agente_matricula = int(agente_str.split(" - ")[0])

        infrator_id = None
        if " - " in infrator_str:
            infrator_id = int(infrator_str.split(" - ")[0])

        if not agente_matricula or not infrator_id:
            from tkinter import messagebox
            messagebox.showwarning("Atencao", "Selecione agente e infrator!", parent=self)
            return

        data_val = data_validade if data_validade else None

        with Database() as db:
            if not db.conexao:
                from tkinter import messagebox
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco!", parent=self)
                return
            try:
                sql = """INSERT INTO tccm
                    (processo, total_pago, total_validado, data_validade,
                     intervalo, total_devido, status,
                     "agente ibama_matricula", "infrator_id_infrator")
                    VALUES (?, 0.00, ?, ?, ?, ?, 'pendente', ?, ?)"""
                db.executar(sql, (processo, total_validado_val, data_val,
                                  intervalo_val, total_devido_val,
                                  agente_matricula, infrator_id))
                db.commitar()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Erro", f"Falha ao cadastrar TCCM:\n{e}", parent=self)
                return

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

        ctk.CTkLabel(hdr, text=f"Notas Fiscais Vinculadas ({len(self.notas)})",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        columns = ["NF", "Data", "Chave Acesso", "Valor Total", "Status"]
        weights = [2, 2, 3, 2, 1]

        col_header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=36, corner_radius=0)
        col_header.pack(fill="x", padx=10)
        col_header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(col_header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(cols_frame, text=col,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=4)

        body = ctk.CTkScrollableFrame(section, fg_color=COLORS["white"], corner_radius=0, height=120)
        body.pack(fill="x", padx=10, pady=(5, 10))

        if not self.notas:
            ctk.CTkLabel(body, text="Nenhuma nota fiscal vinculada",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=15)
        else:
            for nota in self.notas:
                row = ctk.CTkFrame(body, fg_color="transparent", height=36)
                row.pack(fill="x")
                row.pack_propagate(False)

                ctk.CTkFrame(body, fg_color="#E0E0E0", height=1).pack(fill="x")

                cols = ctk.CTkFrame(row, fg_color="transparent")
                cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
                for i, w in enumerate(weights):
                    cols.grid_columnconfigure(i, weight=w)

                dados = [
                    nota["nota_fiscal"], nota["data"], nota["chave_acesso"],
                    _fmt_brl(nota["valor_total"])
                ]
                for i, valor in enumerate(dados):
                    cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                    ctk.CTkLabel(cols, text=valor,
                                  font=ctk.CTkFont(size=FONTS["size_small"]),
                                  text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=4)

                status_frame = ctk.CTkFrame(row, fg_color="transparent", width=80)
                status_frame.pack(side="right", padx=(0, 8))
                status_frame.pack_propagate(False)

                st = nota["status"]
                if st == "Aprovada":
                    st_cor = COLORS["success_dark"]
                elif st == "Rejeitada":
                    st_cor = COLORS["danger"]
                else:
                    st_cor = COLORS["warning"]

                ctk.CTkLabel(status_frame, text=st,
                              font=ctk.CTkFont(size=10, weight="bold"),
                              text_color=st_cor).pack(expand=True)

    def build_itens_section(self):
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 25))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["dark"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text=f"Itens ({len(self.itens)})",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        columns = ["Nome", "Quantidade", "Preco Unitario", "Subtotal", "NF"]
        weights = [3, 1, 2, 2, 2]

        col_header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=36, corner_radius=0)
        col_header.pack(fill="x", padx=10)
        col_header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(col_header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(cols_frame, text=col,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=4)

        body = ctk.CTkScrollableFrame(section, fg_color=COLORS["white"], corner_radius=0, height=120)
        body.pack(fill="x", padx=10, pady=(5, 10))

        if not self.itens:
            ctk.CTkLabel(body, text="Nenhum item vinculado",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=15)
        else:
            for item in self.itens:
                row = ctk.CTkFrame(body, fg_color="transparent", height=36)
                row.pack(fill="x")
                row.pack_propagate(False)

                ctk.CTkFrame(body, fg_color="#E0E0E0", height=1).pack(fill="x")

                cols = ctk.CTkFrame(row, fg_color="transparent")
                cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
                for i, w in enumerate(weights):
                    cols.grid_columnconfigure(i, weight=w)

                subtotal = item["quantidade"] * item["preco_unitario"]
                dados = [
                    item["nome_item"], str(item["quantidade"]),
                    _fmt_brl(item["preco_unitario"]), _fmt_brl(subtotal),
                    item["nota_fiscal"]
                ]
                for i, valor in enumerate(dados):
                    cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                    ctk.CTkLabel(cols, text=valor,
                                  font=ctk.CTkFont(size=FONTS["size_small"]),
                                  text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=4)

    def _carregar_dados(self):
        with Database() as db:
            if not db.conexao:
                return
            try:
                sql = """SELECT t.processo, t.total_pago, t.total_validado, t.data_validade,
                                t.intervalo, t.total_devido, t.status,
                                t."agente ibama_matricula", t."infrator_id_infrator"
                         FROM tccm t WHERE t.processo = ?"""
                r = db.executar(sql, (self.processo,))
                row = r.fetchone() if r else None
                if not row:
                    return

                self.tccm_data = {
                    "processo": row[0],
                    "total_pago": float(row[1]) if row[1] else 0,
                    "total_validado": float(row[2]) if row[2] else 0,
                    "data_validade": _fmt_date(row[3]),
                    "intervalo": row[4] or 0,
                    "total_devido": float(row[5]) if row[5] else 0,
                    "status": row[6] or "pendente",
                    "agente_matricula": row[7],
                    "infrator_id": row[8],
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
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.build_header_topo()
        self.build_stats_cards()
        self.build_progress_section()
        self.build_tables_section()

        self._atualizar_dados()

    def build_header_topo(self):
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(left, text="Painel Geral",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(left, text="Panorama completo do sistema FISCSOFT",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            header, text="+ Novo TCCM", height=40, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._abrir_modal_cadastro,
        ).pack(side="right")

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.stat_labels = {}
        card_data = [
            ("TCCMs", "Total de processos", "0", "\U0001f4cb", COLORS["primary"]),
            ("Notas Fiscais", "NFs cadastradas", "0", "\U0001f4c4", COLORS["success_dark"]),
            ("Itens", "Catalogo de itens", "0", "\U0001f4e6", COLORS["warning"]),
            ("Infratores", "Cadastrados", "0", "\U0001f464", COLORS["danger"]),
            ("Agentes", "Agentes IBAMA", "0", "\U0001f9d1\u200d\U0001f4bc", COLORS["dark"]),
        ]

        for i, (titulo, subtitulo, valor, icon, cor) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards_frame, fg_color=COLORS["white"], corner_radius=4,
                border_width=1, border_color=COLORS["border"]
            )
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=12)

            icon_circle = ctk.CTkFrame(
                inner, fg_color=COLORS["primary_light"],
                width=40, height=40, corner_radius=20
            )
            icon_circle.pack(side="left", padx=(0, 10))
            icon_circle.pack_propagate(False)

            ctk.CTkLabel(
                icon_circle, text=icon,
                font=ctk.CTkFont(size=16),
                text_color=cor
            ).pack(expand=True)

            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                text_frame, text=titulo,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text"], anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame, text=subtitulo,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            lbl_valor = ctk.CTkLabel(
                card, text=valor,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=COLORS["text"]
            )
            lbl_valor.pack(pady=(0, 10))
            self.stat_labels[titulo] = lbl_valor

    def build_progress_section(self):
        section = ctk.CTkFrame(self.scroll, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        inner = ctk.CTkFrame(section, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        self.progress_bar = CircularProgressBar(inner, size=150, thickness=14)
        self.progress_bar.pack(side="left", padx=(0, 25))

        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        self.lbl_total_devido = ctk.CTkLabel(
            info_frame, text="Total Devido: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"], anchor="w"
        )
        self.lbl_total_devido.pack(anchor="w")

        self.lbl_total_pago = ctk.CTkLabel(
            info_frame, text="Total Pago: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["success_dark"], anchor="w"
        )
        self.lbl_total_pago.pack(anchor="w", pady=(4, 0))

        self.lbl_total_pendente = ctk.CTkLabel(
            info_frame, text="Total Pendente: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["warning"], anchor="w"
        )
        self.lbl_total_pendente.pack(anchor="w", pady=(4, 0))

        self.lbl_total_nf = ctk.CTkLabel(
            info_frame, text="Valor em NFs: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"], anchor="w"
        )
        self.lbl_total_nf.pack(anchor="w", pady=(8, 0))

        right_frame = ctk.CTkFrame(inner, fg_color="transparent")
        right_frame.pack(side="right")

        stats_grid = ctk.CTkFrame(right_frame, fg_color="transparent")
        stats_grid.pack()

        self.status_labels = {}
        status_data = [
            ("Pendentes", "0", COLORS["warning"]),
            ("Pagos Parcial", "0", "#FF9800"),
            ("Concluidos", "0", COLORS["success_dark"]),
        ]

        for i, (titulo, valor, cor) in enumerate(status_data):
            card = ctk.CTkFrame(stats_grid, fg_color=COLORS["white"], corner_radius=6,
                                border_width=1, border_color=COLORS["border"], width=115, height=65)
            card.grid(row=0, column=i, padx=4, pady=2)
            card.pack_propagate(False)

            dot = ctk.CTkFrame(card, fg_color=cor, width=8, height=8, corner_radius=4)
            dot.pack(anchor="w", padx=10, pady=(8, 2))
            dot.pack_propagate(False)

            ctk.CTkLabel(card, text=titulo,
                          font=ctk.CTkFont(size=9),
                          text_color=COLORS["text_muted"]).pack(anchor="w", padx=10)

            lbl = ctk.CTkLabel(card, text=valor,
                                font=ctk.CTkFont(size=16, weight="bold"),
                                text_color=COLORS["text"])
            lbl.pack(anchor="w", padx=10)
            self.status_labels[titulo] = lbl

    def build_tables_section(self):
        tables_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        tables_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        tables_frame.grid_columnconfigure(0, weight=3)
        tables_frame.grid_columnconfigure(1, weight=2)
        tables_frame.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(tables_frame, fg_color=COLORS["white"], corner_radius=4,
                             border_width=1, border_color=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._build_tccm_table(left)

        right = ctk.CTkFrame(tables_frame, fg_color=COLORS["white"], corner_radius=4,
                              border_width=1, border_color=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._build_nf_table(right)

    def _build_tccm_table(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Todos os TCCMs",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        columns = ["Processo", "Infrator", "Devido", "Pago", "Status"]
        weights = [2, 2, 2, 2, 1]

        col_header = ctk.CTkFrame(parent, fg_color=COLORS["table_header"], height=36, corner_radius=0)
        col_header.pack(fill="x", padx=10)
        col_header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(col_header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(cols_frame, text=col,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=4)

        self.table_body_tccm = ctk.CTkScrollableFrame(parent, fg_color=COLORS["white"], corner_radius=0)
        self.table_body_tccm.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(0, 10))
        self.footer_tccm = ctk.CTkLabel(footer, text="Total: 0 | R$ 0,00",
                                         font=ctk.CTkFont(size=FONTS["size_small"]),
                                         text_color=COLORS["text_muted"])
        self.footer_tccm.pack(side="left")

    def _build_nf_table(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["success_dark"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Notas Fiscais Recentes",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        columns = ["NF", "Processo", "Valor", "Status"]
        weights = [2, 2, 2, 1]

        col_header = ctk.CTkFrame(parent, fg_color=COLORS["table_header"], height=36, corner_radius=0)
        col_header.pack(fill="x", padx=10)
        col_header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(col_header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(cols_frame, text=col,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=4)

        self.table_body_nf = ctk.CTkScrollableFrame(parent, fg_color=COLORS["white"], corner_radius=0)
        self.table_body_nf.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(0, 10))
        self.footer_nf = ctk.CTkLabel(footer, text="Total: 0 | R$ 0,00",
                                       font=ctk.CTkFont(size=FONTS["size_small"]),
                                       text_color=COLORS["text_muted"])
        self.footer_nf.pack(side="left")

    def _carregar_dados(self):
        tccms = []
        nfs = []
        counts = {"tccm": 0, "nf": 0, "itens": 0, "infratores": 0, "agentes": 0}
        totals = {"devido": 0, "pago": 0, "valor_nf": 0}

        with Database() as db:
            if not db.conexao:
                return tccms, nfs, counts, totals

            try:
                r = db.executar("SELECT COUNT(*) FROM tccm")
                counts["tccm"] = r.fetchone()[0] if r else 0
            except Exception:
                pass

            try:
                r = db.executar('SELECT COUNT(DISTINCT nota_fiscal) FROM "nota fiscal"')
                counts["nf"] = r.fetchone()[0] if r else 0
            except Exception:
                pass

            try:
                r = db.executar("SELECT COUNT(*) FROM itens")
                counts["itens"] = r.fetchone()[0] if r else 0
            except Exception:
                pass

            try:
                r = db.executar("SELECT COUNT(*) FROM infrator")
                counts["infratores"] = r.fetchone()[0] if r else 0
            except Exception:
                pass

            try:
                r = db.executar('SELECT COUNT(*) FROM "agente ibama" WHERE status = "ativo"')
                counts["agentes"] = r.fetchone()[0] if r else 0
            except Exception:
                pass

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
                        item = {
                            "processo": row[0] or "--",
                            "total_pago": float(row[1]) if row[1] else 0,
                            "total_devido": float(row[2]) if row[2] else 0,
                            "status": row[3] or "pendente",
                            "data_validade": _fmt_date(row[4]),
                            "intervalo": row[5] or 0,
                            "infrator": row[6] or "--",
                            "cpf": row[7] or "--",
                        }
                        totals["devido"] += item["total_devido"]
                        totals["pago"] += item["total_pago"]
                        tccms.append(item)
            except Exception:
                pass

            try:
                sql = """SELECT nf.nota_fiscal, nf.processo, nf.valor_total, nf.status_nota, nf.data
                         FROM "nota fiscal" nf
                         ORDER BY nf.data DESC LIMIT 10"""
                r = db.executar(sql)
                if r:
                    for row in r.fetchall():
                        nfs.append({
                            "nota_fiscal": row[0] or "--",
                            "processo": row[1] or "--",
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
                            "data": _fmt_date(row[4]),
                        })
                        totals["valor_nf"] += float(row[2]) if row[2] else 0
            except Exception:
                pass

        return tccms, nfs, counts, totals

    def _atualizar_dados(self):
        tccms, nfs, counts, totals = self._carregar_dados()

        self.stat_labels["TCCMs"].configure(text=str(counts["tccm"]))
        self.stat_labels["Notas Fiscais"].configure(text=str(counts["nf"]))
        self.stat_labels["Itens"].configure(text=str(counts["itens"]))
        self.stat_labels["Infratores"].configure(text=str(counts["infratores"]))
        self.stat_labels["Agentes"].configure(text=str(counts["agentes"]))

        pct = (totals["pago"] / totals["devido"] * 100) if totals["devido"] > 0 else 0
        self.progress_bar.set_progress(pct / 100, f"{pct:.0f}%", "arrecadado")

        self.lbl_total_devido.configure(text=f"Total Devido: {_fmt_brl(totals['devido'])}")
        self.lbl_total_pago.configure(text=f"Total Pago: {_fmt_brl(totals['pago'])}")
        pendente = totals["devido"] - totals["pago"]
        self.lbl_total_pendente.configure(text=f"Total Pendente: {_fmt_brl(max(0, pendente))}")
        self.lbl_total_nf.configure(text=f"Valor em NFs: {_fmt_brl(totals['valor_nf'])}")

        pendentes = len([t for t in tccms if t["status"] == "pendente"])
        parciais = len([t for t in tccms if t["status"] == "pago_parcial"])
        concluidos = len([t for t in tccms if t["status"] == "concluido"])

        self.status_labels["Pendentes"].configure(text=str(pendentes))
        self.status_labels["Pagos Parcial"].configure(text=str(parciais))
        self.status_labels["Concluidos"].configure(text=str(concluidos))

        self._render_tccm_table(tccms)
        self._render_nf_table(nfs)

    def _render_tccm_table(self, data):
        for w in self.table_body_tccm.winfo_children():
            w.destroy()

        if not data:
            ctk.CTkLabel(self.table_body_tccm, text="Nenhum TCCM cadastrado",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=25)
            return

        weights = [2, 2, 2, 2, 1]
        for item in data:
            row = ctk.CTkFrame(self.table_body_tccm, fg_color="transparent", height=38)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkFrame(self.table_body_tccm, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(row, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            status = item["status"]
            if status == "concluido":
                status_text = "Concluido"
                status_cor = COLORS["success_dark"]
            elif status == "pago_parcial":
                status_text = "Parcial"
                status_cor = "#FF9800"
            else:
                status_text = "Pendente"
                status_cor = COLORS["warning"]

            dados = [
                item["processo"], item["infrator"],
                _fmt_brl(item["total_devido"]), _fmt_brl(item["total_pago"])
            ]
            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(cols, text=valor,
                              font=ctk.CTkFont(size=FONTS["size_small"]),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=4)

            right_frame = ctk.CTkFrame(row, fg_color="transparent")
            right_frame.pack(side="right", padx=(0, 8))
            right_frame.pack_propagate(False)

            ctk.CTkLabel(right_frame, text=status_text,
                          font=ctk.CTkFont(size=9, weight="bold"),
                          text_color=status_cor, width=60).pack(side="left")

            ctk.CTkButton(
                right_frame, text="\u25b6", width=26, height=26,
                corner_radius=4, fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"], text_color="white",
                font=ctk.CTkFont(size=11),
                command=lambda p=item["processo"]: self._abrir_detalhes(p),
            ).pack(side="left", padx=(4, 0))

        valor_total = sum(t["total_devido"] for t in data)
        self.footer_tccm.configure(text=f"Total: {len(data)} | {_fmt_brl(valor_total)}")

    def _render_nf_table(self, data):
        for w in self.table_body_nf.winfo_children():
            w.destroy()

        if not data:
            ctk.CTkLabel(self.table_body_nf, text="Nenhuma nota fiscal",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=25)
            return

        weights = [2, 2, 2, 1]
        for item in data:
            row = ctk.CTkFrame(self.table_body_nf, fg_color="transparent", height=38)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkFrame(self.table_body_nf, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(row, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(8, 0))
            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            st = item["status"]
            if st == "Aprovada":
                st_cor = COLORS["success_dark"]
            elif st == "Rejeitada":
                st_cor = COLORS["danger"]
            else:
                st_cor = COLORS["warning"]

            dados = [item["nota_fiscal"], item["processo"], _fmt_brl(item["valor_total"])]
            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(cols, text=valor,
                              font=ctk.CTkFont(size=FONTS["size_small"]),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=4)

            st_frame = ctk.CTkFrame(row, fg_color="transparent", width=70)
            st_frame.pack(side="right", padx=(0, 8))
            st_frame.pack_propagate(False)

            ctk.CTkLabel(st_frame, text=st,
                          font=ctk.CTkFont(size=9, weight="bold"),
                          text_color=st_cor).pack(expand=True)

        valor_total = sum(n["valor_total"] for n in data)
        self.footer_nf.configure(text=f"Total: {len(data)} | {_fmt_brl(valor_total)}")

    def _abrir_detalhes(self, processo):
        if hasattr(self, '_abrir_menu_principal_cb') and self._abrir_menu_principal_cb:
            self._abrir_menu_principal_cb(processo)
        else:
            for w in self.master.winfo_children():
                w.destroy()
            TccmDetalhesPage(
                self.master, processo=processo,
                on_voltar=lambda: self._voltar_ao_dashboard(),
                usuario_logado=self.usuario_logado, perfil=self.perfil,
            ).pack(fill="both", expand=True)

    def _voltar_ao_dashboard(self):
        for w in self.master.winfo_children():
            w.destroy()
        TccmDashboardPage(
            self.master,
            usuario_logado=self.usuario_logado, perfil=self.perfil,
        ).pack(fill="both", expand=True)

    def _abrir_modal_cadastro(self):
        ModalCadastrarTCCM(self.winfo_toplevel(), onSalvar=self._atualizar_dados)
