import _path  # noqa: F401

from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.widgets import ComboBoxComSeta


class CadastroTCCMCompleto(ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, usuario_logado=None, perfil="admin", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        self.agentes = []
        self.infratores = []
        self.itens_lista = []

        self._carregar_dados_combobox()

        sidebar = ctk.CTkFrame(self, fg_color="#FAFAFA", width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Cadastro TCCM",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["primary"]).pack(pady=(25, 20), padx=15, anchor="w")

        self._botoes_sidebar = []
        self._paginas = [
            ("TCCM", "Dados do TCCM"),
            ("Agente", "Agente Responsavel"),
            ("Infrator", "Infrator"),
            ("Itens", "Itens"),
        ]

        for key, label in self._paginas:
            btn = ctk.CTkButton(
                sidebar, text=f"   {label}", anchor="w", height=40,
                corner_radius=6, fg_color="transparent",
                hover_color=COLORS["nav_hover"], text_color=COLORS["nav_text"],
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                command=lambda k=key: self._mostrar_pagina(k),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self._botoes_sidebar.append((key, btn))

        separador = ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1, corner_radius=0)
        separador.pack(side="bottom", fill="x", padx=12, pady=(0, 8))

        ctk.CTkButton(
            sidebar, text="   \u2190 Voltar", anchor="w", height=40,
            corner_radius=6, fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color="white",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._voltar,
        ).pack(side="bottom", fill="x", padx=12, pady=(0, 16))

        ctk.CTkButton(
            sidebar, text="   \u2714 Salvar TCCM", anchor="w", height=40,
            corner_radius=6, fg_color=COLORS["success_dark"],
            hover_color=COLORS["success_dark_hover"], text_color="white",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._salvar_tudo,
        ).pack(side="bottom", fill="x", padx=12, pady=(0, 6))

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True)

        self._paginas_widgets = {}
        self._criar_paginas()

        self._mostrar_pagina("TCCM")

    def _criar_paginas(self):
        self._criar_pagina_tccm()
        self._criar_pagina_agente()
        self._criar_pagina_infrator()
        self._criar_pagina_itens()

    def _criar_pagina_tccm(self):
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self._paginas_widgets["TCCM"] = container

        self.entries_tccm = {}

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        ctk.CTkLabel(header, text="Dados do Processo TCCM",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(header, text="Informe os dados basicos do Termo de Cooperação e Conversão de Multa.",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        form_card = ctk.CTkFrame(container, fg_color=COLORS["white"], corner_radius=8,
                                  border_width=1, border_color=COLORS["border"])
        form_card.pack(fill="x", padx=30, pady=(0, 20))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=30, pady=25)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        row0 = ctk.CTkFrame(form, fg_color="transparent")
        row0.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        row0.grid_columnconfigure(0, weight=1)
        row0.grid_columnconfigure(1, weight=1)

        col_a = ctk.CTkFrame(row0, fg_color="transparent")
        col_a.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ctk.CTkLabel(col_a, text="Numero do Processo*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(col_a, height=40, corner_radius=6,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: PROC-2026-005")
        entry.pack(fill="x")
        self.entries_tccm["processo"] = entry

        col_b = ctk.CTkFrame(row0, fg_color="transparent")
        col_b.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(col_b, text="Documento SEI (opcional)",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(col_b, height=40, corner_radius=6,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: SEI-001/2026")
        entry.pack(fill="x")
        self.entries_tccm["documento_sei"] = entry

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_columnconfigure(2, weight=1)

        col_c = ctk.CTkFrame(row1, fg_color="transparent")
        col_c.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ctk.CTkLabel(col_c, text="Data de Inicio*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(col_c, height=40, corner_radius=6,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="DD/MM/AAAA")
        entry.pack(fill="x")
        self.entries_tccm["data_inicio"] = entry

        col_d = ctk.CTkFrame(row1, fg_color="transparent")
        col_d.grid(row=0, column=1, sticky="ew", padx=(0, 15))

        ctk.CTkLabel(col_d, text="Semestres*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(col_d, height=40, corner_radius=6,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="ex: 4")
        entry.pack(fill="x")
        self.entries_tccm["semestres"] = entry

        col_e = ctk.CTkFrame(row1, fg_color="transparent")
        col_e.grid(row=0, column=2, sticky="ew")

        ctk.CTkLabel(col_e, text="Total a Ser Pago (R$)*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(col_e, height=40, corner_radius=6,
                             border_width=1, border_color=COLORS["border"],
                             fg_color=COLORS["white"], text_color=COLORS["text"],
                             placeholder_text="0,00")
        entry.pack(fill="x")
        self.entries_tccm["total_devido"] = entry

    def _criar_pagina_agente(self):
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self._paginas_widgets["Agente"] = container

        self.entries_agente = {}

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        ctk.CTkLabel(header, text="Agente Responsavel",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(header, text="Selecione um agente existente ou cadastre um novo.",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        select_card = ctk.CTkFrame(container, fg_color=COLORS["white"], corner_radius=8,
                                    border_width=1, border_color=COLORS["border"])
        select_card.pack(fill="x", padx=30, pady=(0, 15))

        inner = ctk.CTkFrame(select_card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(inner, text="Agente Responsavel*",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 6))

        agente_row = ctk.CTkFrame(inner, fg_color="transparent")
        agente_row.pack(fill="x")
        agente_row.grid_columnconfigure(0, weight=1)

        opcoes = [f"{a[0]} - {a[1]}" for a in self.agentes] if self.agentes else ["Nenhum agente"]
        combo = ComboBoxComSeta(agente_row, values=opcoes,
                                height=40, corner_radius=6,
                                fg_color=COLORS["white"], border_color=COLORS["border"],
                                button_color=COLORS["primary"],
                                dropdown_fg_color=COLORS["white"])
        combo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entries_agente["agente_matricula"] = combo

        ctk.CTkButton(
            agente_row, text="+ Novo Agente", height=40, width=130, corner_radius=6,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._abrir_cadastrar_agente,
        ).grid(row=0, column=1)

    def _criar_pagina_infrator(self):
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self._paginas_widgets["Infrator"] = container

        self.entries_infrator = {}

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        ctk.CTkLabel(header, text="Infrator",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(header, text="Selecione um infrator existente ou cadastre um novo.",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        select_card = ctk.CTkFrame(container, fg_color=COLORS["white"], corner_radius=8,
                                    border_width=1, border_color=COLORS["border"])
        select_card.pack(fill="x", padx=30, pady=(0, 15))

        inner = ctk.CTkFrame(select_card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(inner, text="Infrator*",
                      font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w", pady=(0, 6))

        infrator_row = ctk.CTkFrame(inner, fg_color="transparent")
        infrator_row.pack(fill="x")
        infrator_row.grid_columnconfigure(0, weight=1)

        opcoes = [f"{i[0]} - {i[1]}" for i in self.infratores] if self.infratores else ["Nenhum infrator"]
        combo = ComboBoxComSeta(infrator_row, values=opcoes,
                                height=40, corner_radius=6,
                                fg_color=COLORS["white"], border_color=COLORS["border"],
                                button_color=COLORS["primary"],
                                dropdown_fg_color=COLORS["white"])
        combo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entries_infrator["infrator_id"] = combo

        ctk.CTkButton(
            infrator_row, text="+ Novo Infrator", height=40, width=130, corner_radius=6,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._abrir_cadastrar_infrator,
        ).grid(row=0, column=1)

    def _criar_pagina_itens(self):
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self._paginas_widgets["Itens"] = container

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(side="left")

        ctk.CTkLabel(titulo_frame, text="Itens do TCCM",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(titulo_frame, text="Adicione os itens deste TCCM.",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            header, text="Exportar Planilha", height=36, corner_radius=6,
            fg_color=COLORS["dark"], hover_color=COLORS["dark_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._exportar_planilha,
        ).pack(side="right", padx=(10, 0))

        form_card = ctk.CTkFrame(container, fg_color=COLORS["white"], corner_radius=8,
                                  border_width=1, border_color=COLORS["border"])
        form_card.pack(fill="x", padx=30, pady=(0, 15))

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="x", padx=30, pady=20)
        form_inner.grid_columnconfigure(0, weight=2)
        form_inner.grid_columnconfigure(1, weight=2)
        form_inner.grid_columnconfigure(2, weight=1)
        form_inner.grid_columnconfigure(3, weight=2)
        form_inner.grid_columnconfigure(4, weight=1)
        form_inner.grid_columnconfigure(5, weight=1)
        form_inner.grid_columnconfigure(6, weight=0)

        ctk.CTkLabel(form_inner, text="Nome do Item*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.entry_item_nome = ctk.CTkEntry(form_inner, height=38, corner_radius=6,
                                            border_width=1, border_color=COLORS["border"],
                                            fg_color=COLORS["white"], text_color=COLORS["text"],
                                            placeholder_text="Nome do item")
        self.entry_item_nome.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form_inner, text="Descricao",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=1, sticky="w", padx=(0, 6))
        self.entry_item_desc = ctk.CTkEntry(form_inner, height=38, corner_radius=6,
                                            border_width=1, border_color=COLORS["border"],
                                            fg_color=COLORS["white"], text_color=COLORS["text"],
                                            placeholder_text="Descricao do item")
        self.entry_item_desc.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form_inner, text="Tipo de Material*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.entry_item_tipo = ComboBoxComSeta(form_inner, values=["Consumivel", "Permanente"],
                                               height=38, corner_radius=6, state="readonly",
                                               fg_color=COLORS["white"], border_color=COLORS["border"],
                                               button_color=COLORS["primary"],
                                               dropdown_fg_color=COLORS["white"])
        self.entry_item_tipo.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form_inner, text="Justificativa*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=3, sticky="w", padx=(0, 6))
        self.entry_item_just = ctk.CTkEntry(form_inner, height=38, corner_radius=6,
                                            border_width=1, border_color=COLORS["border"],
                                            fg_color=COLORS["white"], text_color=COLORS["text"],
                                            placeholder_text="Justificativa do item")
        self.entry_item_just.grid(row=1, column=3, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form_inner, text="Qtd.*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.entry_item_qtd = ctk.CTkEntry(form_inner, height=38, corner_radius=6,
                                           border_width=1, border_color=COLORS["border"],
                                           fg_color=COLORS["white"], text_color=COLORS["text"],
                                           placeholder_text="0")
        self.entry_item_qtd.grid(row=1, column=4, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(form_inner, text="Unidade de Medida*",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=0, column=5, sticky="w", padx=(0, 6))
        self.entry_item_unidade = ComboBoxComSeta(form_inner, values=["Unidade", "Caixa", "Litro", "Kg"],
                                                  height=38, corner_radius=6, state="readonly",
                                                  fg_color=COLORS["white"], border_color=COLORS["border"],
                                                  button_color=COLORS["primary"],
                                                  dropdown_fg_color=COLORS["white"])
        self.entry_item_unidade.grid(row=1, column=5, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            form_inner, text="+ Adicionar", height=38, width=110, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._adicionar_item,
        ).grid(row=1, column=6, padx=(6, 0))

        self.itens_container = ctk.CTkFrame(container, fg_color="transparent")
        self.itens_container.pack(fill="x", padx=30, pady=(0, 20))

        self._renderizar_itens()

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
        self.entries_agente["agente_matricula"].configure(
            values=[f"{a[0]} - {a[1]}" for a in self.agentes] if self.agentes else ["Nenhum agente"]
        )
        self.entries_infrator["infrator_id"].configure(
            values=[f"{i[0]} - {i[1]}" for i in self.infratores] if self.infratores else ["Nenhum infrator"]
        )

    def _abrir_cadastrar_agente(self):
        from screens.cadastrar_usuario import CadastrarUsuarioWindow
        janela = CadastrarUsuarioWindow(self, usuario_logado=self.usuario_logado)
        self.wait_window(janela)
        self._atualizar_combos()

    def _abrir_cadastrar_infrator(self):
        from screens.cadastrar_infrator import CadastrarInfratorWindow
        janela = CadastrarInfratorWindow(self)
        self.wait_window(janela)
        self._atualizar_combos()

    def _mostrar_pagina(self, key):
        for w in self.content_frame.winfo_children():
            w.pack_forget()

        for k, btn in self._botoes_sidebar:
            if k == key:
                btn.configure(fg_color=COLORS["primary_light"], text_color=COLORS["primary"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["nav_text"])

        widget = self._paginas_widgets.get(key)
        if widget:
            widget.pack(fill="both", expand=True)

    def _adicionar_item(self):
        nome = self.entry_item_nome.get().strip()
        desc = self.entry_item_desc.get().strip()
        tipo = self.entry_item_tipo.get().strip()
        just = self.entry_item_just.get().strip()
        qtd = self.entry_item_qtd.get().strip()
        unidade = self.entry_item_unidade.get().strip()

        if not all([nome, desc, just, qtd]):
            messagebox.showwarning("Atencao", "Preencha nome, descricao, justificativa e quantidade!", parent=self)
            return

        try:
            qtd_val = int(qtd)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um numero inteiro!", parent=self)
            return

        # determine number of semesters from TCCM data
        semestres_total = 1
        sem_field = self.entries_tccm.get("semestres")
        if sem_field:
            try:
                semestres_total = int(sem_field.get().strip()) if sem_field.get().strip() else 1
            except Exception:
                semestres_total = 1

        quantidades_sem = None
        if semestres_total > 1:
            quantidades_sem = self._abrir_definir_quantidades_modal(semestres_total, default_total=qtd_val)
            if quantidades_sem is None:
                return

        item_obj = {
            "nome": nome,
            "descricao": desc,
            "tipo": tipo or "Consumivel",
            "justificativa": just,
            "unidade_medida": unidade or "Unidade",
        }
        if quantidades_sem:
            item_obj["quantidades_semestre"] = quantidades_sem
            item_obj["quantidade"] = sum(quantidades_sem)
        else:
            item_obj["quantidade"] = qtd_val

        self.itens_lista.append(item_obj)

        self.entry_item_nome.delete(0, "end")
        self.entry_item_desc.delete(0, "end")
        self.entry_item_just.delete(0, "end")
        self.entry_item_qtd.delete(0, "end")
        self.entry_item_tipo.set("Consumivel")
        self.entry_item_unidade.set("Unidade")

        self._renderizar_itens()

    def _remover_item(self, idx):
        self.itens_lista.pop(idx)
        self._renderizar_itens()

    def _renderizar_itens(self):
        for w in self.itens_container.winfo_children():
            w.destroy()

        if not self.itens_lista:
            ctk.CTkLabel(self.itens_container, text="Nenhum item adicionado ainda.",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=30)
            return

        hdr = ctk.CTkFrame(self.itens_container, fg_color=COLORS["table_header"], height=36, corner_radius=6)
        hdr.pack(fill="x", pady=(0, 4))
        hdr.pack_propagate(False)
        hdr.grid_columnconfigure(0, weight=3)
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_columnconfigure(2, weight=2)
        hdr.grid_columnconfigure(3, weight=1)
        hdr.grid_columnconfigure(4, weight=1)
        hdr.grid_columnconfigure(5, weight=0)

        for i, col in enumerate(["Nome", "Tipo de Material", "Justificativa", "Qtd.", "Unidade de Medida", ""]):
            ctk.CTkLabel(hdr, text=col,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=10)

        for idx, item in enumerate(self.itens_lista):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row = ctk.CTkFrame(self.itens_container, fg_color=row_bg, height=36, corner_radius=0)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=1)
            row.grid_columnconfigure(4, weight=1)
            row.grid_columnconfigure(5, weight=0)

            total_q = item.get("quantidade") or 0
            dados = [item["nome"], item["tipo"], item["justificativa"],
                     str(total_q), item["unidade_medida"]]
            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(row, text=valor,
                              font=ctk.CTkFont(size=11),
                              text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=10)

            ctk.CTkButton(
                row, text="\u2715", width=28, height=26, corner_radius=4,
                fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                text_color="white", font=ctk.CTkFont(size=11),
                command=lambda idx=idx: self._remover_item(idx),
            ).grid(row=0, column=5, padx=(6, 10))
            # edit semestres (define quantities per semester)
            ctk.CTkButton(
                row, text="Semestres", width=100, height=26, corner_radius=4,
                fg_color=COLORS["border"], hover_color=COLORS["hover"],
                text_color=COLORS["text"], font=ctk.CTkFont(size=11),
                command=lambda idx=idx: self._abrir_editar_semestres(idx),
            ).grid(row=0, column=5, padx=(6, 10))

    def _exportar_planilha(self):
        """Exporta os itens (adicionados no formulario ou ja salvos no banco)
        para uma planilha Excel .xlsx com os cabecalhos padrao."""
        from tkinter import filedialog

        import openpyxl
        from openpyxl.styles import Font

        processo = self.entries_tccm["processo"].get().strip()
        itens = list(self.itens_lista)

        if processo:
            try:
                with Database() as db:
                    if db.conexao:
                        r = db.executar(
                            "SELECT nome, descricao, tipo, justificativa, quantidade_prevista, unidade_medida "
                            "FROM itens WHERE processo = ?",
                            (processo,),
                        )
                        if r:
                            rows = r.fetchall()
                            if rows:
                                itens = [
                                    {
                                        "nome": row[0],
                                        "descricao": row[1],
                                        "tipo": row[2],
                                        "justificativa": row[3],
                                        "quantidade": row[4],
                                        "unidade_medida": row[5],
                                    }
                                    for row in rows
                                ]
            except Exception:
                pass

        if not itens:
            messagebox.showwarning(
                "Atencao",
                "Nenhum item encontrado. Adicione os itens manualmente no formulario acima.",
                parent=self,
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar planilha de itens",
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            initialfile=f"itens_tccm_{processo or 'novo'}.xlsx",
        )
        if not caminho:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Itens"
            ws.append(["Nome do Item", "Descricao", "Tipo de Material",
                       "Justificativa", "Quantidade", "Unidade de Medida"])
            for celula in ws[1]:
                celula.font = Font(bold=True)
            for item in itens:
                ws.append([
                    item.get("nome") or "",
                    item.get("descricao") or "",
                    item.get("tipo") or item.get("tipo_material") or "",
                    item.get("justificativa") or "",
                    item.get("quantidade") or item.get("quantidade_prevista") or 0,
                    item.get("unidade_medida") or "",
                ])
            wb.save(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar planilha: {e}", parent=self)
            return

        messagebox.showinfo("Sucesso", f"Planilha exportada com {len(itens)} itens!", parent=self)

    def _salvar_tudo(self):
        processo = self.entries_tccm["processo"].get().strip()
        documento_sei = self.entries_tccm["documento_sei"].get().strip()
        data_inicio = self.entries_tccm["data_inicio"].get().strip()
        semestres = self.entries_tccm["semestres"].get().strip()
        total_devido = self.entries_tccm["total_devido"].get().strip()

        agente_str = self.entries_agente["agente_matricula"].get().strip()
        infrator_str = self.entries_infrator["infrator_id"].get().strip()

        if not all([processo, data_inicio, semestres, total_devido]):
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios na aba 'Dados do TCCM'!", parent=self)
            return

        if " - " not in agente_str:
            messagebox.showwarning("Atencao", "Selecione um agente na aba 'Agente Responsavel'!", parent=self)
            return

        if " - " not in infrator_str:
            messagebox.showwarning("Atencao", "Selecione um infrator na aba 'Infrator'!", parent=self)
            return

        try:
            semestres_val = int(semestres)
        except ValueError:
            messagebox.showerror("Erro", "Semestres deve ser um numero inteiro!", parent=self)
            return

        try:
            total_devido_val = float(total_devido.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Total a ser pago invalido!", parent=self)
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
                    VALUES (?, ?, ?, ?, 0.00, 0.00, ?,
                            NULL, ?, 'pendente', ?, ?)"""
                db.executar(sql, (processo, documento_sei or None, data_inicio_db,
                                  semestres_val, total_devido_val,
                                  semestres_val, agente_matricula, infrator_id))

                for item in self.itens_lista:
                    # insert item and per-semester quantities
                    total_prev = item.get("quantidade") or 0
                    sql_item = """INSERT INTO itens (nome, descricao, codigo_interno, tipo, justificativa,
                                                    unidade_medida, quantidade_prevista, status, processo)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, 'Ativo', ?)"""
                    db.executar(sql_item, (item["nome"], item["descricao"],
                                           f"{processo}-{item['nome'][:10].upper()}",
                                           item["tipo"], item["justificativa"],
                                           item["unidade_medida"], total_prev, processo))
                    # get last inserted item id
                    lr = db.executar("SELECT last_insert_rowid()").fetchone()
                    try:
                        item_id = int(lr[0]) if lr else None
                    except Exception:
                        item_id = None

                    # if item has per-semester quantities, store them
                    if item.get("quantidades_semestre"):
                        try:
                            # compute semester year/number based on data_inicio
                            start_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
                        except Exception:
                            start_dt = datetime.now()
                        start_sem = 1 if start_dt.month <= 6 else 2
                        for i, q in enumerate(item.get("quantidades_semestre")):
                            # sem offset
                            offset = (start_sem - 1) + i
                            ano = start_dt.year + (offset // 2)
                            sem_num = (offset % 2) + 1
                            try:
                                db.executar("INSERT OR REPLACE INTO item_semestre (itens_id, ano, semestre, quantidade_prevista, processo) VALUES (?, ?, ?, ?, ?)", (item_id, ano, sem_num, q, processo))
                            except Exception:
                                pass

                db.commitar()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar TCCM:\n{e}", parent=self)
                return

        messagebox.showinfo("Sucesso", "TCCM cadastrado com sucesso!", parent=self)

        if self.on_voltar:
            self.on_voltar()

    def _voltar(self):
        if self.on_voltar:
            self.on_voltar()

    def _abrir_definir_quantidades_modal(self, semestres_total, default_total=0):
        modal = ctk.CTkToplevel(self)
        modal.title("Definir Quantidades por Semestre")
        modal.geometry("480x320")
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color=COLORS["white"]) 
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        entries = []
        base = default_total // semestres_total if semestres_total else 0
        rem = default_total % semestres_total if semestres_total else 0
        for i in range(semestres_total):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"Semestre {i+1}", width=120, anchor="w").pack(side="left")
            val = base + (1 if i < rem else 0)
            e = ctk.CTkEntry(row, width=120)
            e.pack(side="left", padx=(8,0))
            e.insert(0, str(val))
            entries.append(e)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12,0))
        result = {"vals": None}

        def _confirm():
            vals = []
            try:
                for e in entries:
                    v = int(e.get().strip()) if e.get().strip() else 0
                    vals.append(v)
            except Exception:
                messagebox.showerror("Erro", "Quantidades devem ser inteiros.", parent=modal)
                return
            result["vals"] = vals
            modal.destroy()

        def _cancel():
            modal.destroy()

        ctk.CTkButton(btn_frame, text="Confirmar", command=_confirm, fg_color=COLORS["primary"]).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancelar", command=_cancel).pack(side="right", padx=6)

        self.wait_window(modal)
        return result["vals"]

    def _abrir_editar_semestres(self, idx):
        if idx < 0 or idx >= len(self.itens_lista):
            return
        item = self.itens_lista[idx]
        sem_field = self.entries_tccm.get("semestres")
        sem_total = 1
        if sem_field:
            try:
                sem_total = int(sem_field.get().strip()) if sem_field.get().strip() else 1
            except Exception:
                sem_total = 1

        existing = item.get("quantidades_semestre") or [0] * sem_total
        # adjust length
        if len(existing) < sem_total:
            existing = existing + [0] * (sem_total - len(existing))
        elif len(existing) > sem_total:
            existing = existing[:sem_total]

        # open modal prefilled
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Quantidades por Semestre")
        modal.geometry("480x320")
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color=COLORS["white"]) 
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        entries = []
        for i in range(sem_total):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"Semestre {i+1}", width=120, anchor="w").pack(side="left")
            e = ctk.CTkEntry(row, width=120)
            e.pack(side="left", padx=(8,0))
            e.insert(0, str(existing[i] if i < len(existing) else 0))
            entries.append(e)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12,0))

        def _confirm():
            vals = []
            try:
                for e in entries:
                    v = int(e.get().strip()) if e.get().strip() else 0
                    vals.append(v)
            except Exception:
                messagebox.showerror("Erro", "Quantidades devem ser inteiros.", parent=modal)
                return
            item["quantidades_semestre"] = vals
            item["quantidade"] = sum(vals)
            modal.destroy()
            self._renderizar_itens()

        def _cancel():
            modal.destroy()

        ctk.CTkButton(btn_frame, text="Confirmar", command=_confirm, fg_color=COLORS["primary"]).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancelar", command=_cancel).pack(side="right", padx=6)

        self.wait_window(modal)
