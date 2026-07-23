import _path  # noqa: F401

import os
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config.styles import ASSETS_DIR, COLORS, FONTS
from database.conexaodb import Database


class CadastrarTCCMPage(ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, usuario_logado=None, perfil="admin", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.perfil = perfil
        self.arquivo_selecionado = None

        self.agentes = []
        self.infratores = []
        self._carregar_dados_combobox()

        self._build_header()
        self._build_form()

    def _build_header(self):
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

        ctk.CTkLabel(
            left, text="Cadastrar TCCM",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        ctk.CTkLabel(
            left,
            text="  Informe os dados do TCCM para cadastro no sistema.",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(8, 0))

    def _build_form(self):
        form_container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=8,
            border_width=1, border_color=COLORS["border"],
        )
        form_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        form = ctk.CTkScrollableFrame(form_container, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=25)

        self.entries = {}

        campos = [
            ("processo", "Numero do Processo*", "entry", "ex: PROC-2026-005"),
            ("total_devido", "Total Devido (R$)*", "entry", "0,00"),
            ("total_validado", "Total Validado (R$)*", "entry", "0,00"),
            ("documento_sei", "Documento SEI", "entry", "Informe o numero do documento SEI"),
            ("cpf_cnpj", "CPF/CNPJ do Interessado", "entry", "Informe o CPF ou CNPJ"),
            ("nome_interessado", "Nome do Interessado", "entry", "Informe o nome do interessado"),
        ]

        for key, label, tipo, placeholder in campos:
            ctk.CTkLabel(
                form, text=label,
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                text_color=COLORS["text"],
            ).pack(anchor="w", pady=(15, 6))

            entry = ctk.CTkEntry(
                form, height=42, corner_radius=6,
                border_width=1, border_color=COLORS["border"],
                fg_color=COLORS["white"], text_color=COLORS["text"],
                placeholder_text=placeholder,
                placeholder_text_color=COLORS["text_muted"],
            )
            entry.pack(fill="x")
            if key == "total_validado":
                entry.insert(0, "0,00")
            self.entries[key] = entry

        row_frame = ctk.CTkFrame(form, fg_color="transparent")
        row_frame.pack(fill="x", pady=(15, 0))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        date_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        date_frame.grid(row=0, column=0, sticky="w", padx=(0, 15))

        ctk.CTkLabel(
            date_frame, text="Data Validade (AAAA-MM-DD)*",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 6))

        self.entries["data_validade"] = ctk.CTkEntry(
            date_frame, height=42, corner_radius=6,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="AAAA-MM-DD",
            placeholder_text_color=COLORS["text_muted"],
            width=200,
        )
        self.entries["data_validade"].pack(anchor="w")

        intervalo_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        intervalo_frame.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            intervalo_frame, text="Intervalo (meses)*",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 6))

        self.entries["intervalo"] = ctk.CTkEntry(
            intervalo_frame, height=42, corner_radius=6,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="ex: 6",
            placeholder_text_color=COLORS["text_muted"],
            width=200,
        )
        self.entries["intervalo"].pack(anchor="w")

        combo_frame = ctk.CTkFrame(form, fg_color="transparent")
        combo_frame.pack(fill="x", pady=(15, 0))
        combo_frame.grid_columnconfigure(0, weight=1)
        combo_frame.grid_columnconfigure(1, weight=1)

        agente_col = ctk.CTkFrame(combo_frame, fg_color="transparent")
        agente_col.grid(row=0, column=0, sticky="w", padx=(0, 15))

        ctk.CTkLabel(
            agente_col, text="Agente Responsavel*",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(15, 6))

        opcoes_agentes = [f"{a[0]} - {a[1]}" for a in self.agentes] if self.agentes else ["Nenhum agente"]
        self.combo_agente = ctk.CTkComboBox(
            agente_col, values=opcoes_agentes,
            height=42, corner_radius=6,
            fg_color=COLORS["white"], border_color=COLORS["border"],
            button_color=COLORS["primary"],
            dropdown_fg_color=COLORS["white"],
            border_width=1,
        )
        self.combo_agente.pack(fill="x")
        self.entries["agente_matricula"] = self.combo_agente

        infrator_col = ctk.CTkFrame(combo_frame, fg_color="transparent")
        infrator_col.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            infrator_col, text="Infrator*",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(15, 6))

        opcoes_infratores = [f"{i[0]} - {i[1]}" for i in self.infratores] if self.infratores else ["Nenhum infrator"]
        self.combo_infrator = ctk.CTkComboBox(
            infrator_col, values=opcoes_infratores,
            height=42, corner_radius=6,
            fg_color=COLORS["white"], border_color=COLORS["border"],
            button_color=COLORS["primary"],
            dropdown_fg_color=COLORS["white"],
            border_width=1,
        )
        self.combo_infrator.pack(fill="x")
        self.entries["infrator_id"] = self.combo_infrator

        unidade_frame = ctk.CTkFrame(form, fg_color="transparent")
        unidade_frame.pack(fill="x", pady=(15, 0))

        ctk.CTkLabel(
            unidade_frame, text="Unidade Responsavel",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(15, 6))

        self.combo_unidade = ctk.CTkComboBox(
            unidade_frame, values=self._carregar_unidades(),
            height=42, corner_radius=6,
            fg_color=COLORS["white"], border_color=COLORS["border"],
            button_color=COLORS["primary"],
            dropdown_fg_color=COLORS["white"],
            border_width=1,
        )
        self.combo_unidade.pack(fill="x")
        self.entries["unidade"] = self.combo_unidade

        file_frame = ctk.CTkFrame(form, fg_color="transparent")
        file_frame.pack(fill="x", pady=(15, 0))

        ctk.CTkLabel(
            file_frame, text="Anexo (opcional)",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 6))

        self.btn_arquivo = ctk.CTkButton(
            file_frame, text="Anexar arquivo (Excel)",
            height=42, corner_radius=6,
            fg_color=COLORS["white"], hover_color=COLORS["hover"],
            text_color=COLORS["text_muted"],
            border_width=1, border_color=COLORS["border"],
            width=220,
            command=self._selecionar_arquivo,
        )
        self.btn_arquivo.pack(anchor="w")

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))

        ctk.CTkButton(
            btn_frame, text="Cadastrar", height=45, corner_radius=8,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            command=self._cadastrar,
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            btn_frame, text="Limpar", height=45, corner_radius=8,
            fg_color=COLORS["dark"], hover_color=COLORS["dark_hover"],
            text_color="white", font=ctk.CTkFont(size=14),
            width=200,
            command=self._limpar_formulario,
        ).pack(side="left")

    def _carregar_unidades(self):
        return [
            "Selecione a unidade responsavel",
            "IBAMA - Sede",
            "IBAMA - Regional Norte",
            "IBAMA - Regional Nordeste",
            "IBAMA - Regional Sudeste",
            "IBAMA - Regional Sul",
            "IBAMA - Regional Centro-Oeste",
        ]

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

    def _selecionar_arquivo(self):
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")],
        )
        if arquivo:
            self.arquivo_selecionado = arquivo
            nome_arquivo = os.path.basename(arquivo)
            self.btn_arquivo.configure(text=nome_arquivo, text_color=COLORS["text"])

    def _cadastrar(self):
        processo = self.entries["processo"].get().strip()
        total_devido = self.entries["total_devido"].get().strip()
        total_validado = self.entries["total_validado"].get().strip()
        data_validade = self.entries["data_validade"].get().strip()
        intervalo = self.entries["intervalo"].get().strip()

        agente_str = self.entries["agente_matricula"].get().strip()
        infrator_str = self.entries["infrator_id"].get().strip()

        if not all([processo, total_devido, total_validado, data_validade, intervalo]):
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios!", parent=self)
            return

        if not " - " in agente_str or not " - " in infrator_str:
            messagebox.showwarning("Atencao", "Selecione agente e infrator!", parent=self)
            return

        try:
            total_devido_val = float(total_devido.replace(",", "."))
            total_validado_val = float(total_validado.replace(",", "."))
            intervalo_val = int(intervalo)
        except ValueError:
            messagebox.showerror("Erro", "Valores numericos invalidos!", parent=self)
            return

        try:
            datetime.strptime(data_validade, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data invalida! Use o formato AAAA-MM-DD.", parent=self)
            return

        agente_matricula = int(agente_str.split(" - ")[0])
        infrator_id = int(infrator_str.split(" - ")[0])

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco!", parent=self)
                return
            try:
                sql = """INSERT INTO tccm
                    (processo, total_pago, total_validado, data_validade,
                     intervalo, total_devido, status,
                     "agente ibama_matricula", "infrator_id_infrator")
                    VALUES (?, 0.00, ?, ?, ?, ?, 'pendente', ?, ?)"""
                db.executar(sql, (processo, total_validado_val, data_validade,
                                  intervalo_val, total_devido_val,
                                  agente_matricula, infrator_id))
                db.commitar()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar TCCM:\n{e}", parent=self)
                return

        messagebox.showinfo("Sucesso", "TCCM cadastrado com sucesso!", parent=self)
        self._limpar_formulario()

    def _limpar_formulario(self):
        for key, widget in self.entries.items():
            if hasattr(widget, "delete"):
                widget.delete(0, "end")
            elif hasattr(widget, "set"):
                widget.set(self._carregar_unidades()[0])

        self.arquivo_selecionado = None
        self.btn_arquivo.configure(text="Anexar arquivo (Excel)", text_color=COLORS["text_muted"])

    def _voltar(self):
        if self.on_voltar:
            self.on_voltar()
