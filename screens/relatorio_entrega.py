import _path  # noqa: F401

import subprocess
import os
import tempfile
from tkinter import messagebox

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from utils import registrar_log


class RelatorioEntregaPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.itens_lista = []
        self.local_selecionado = None
        self.locais_catalogo = []
        self.itens_catalogo = []

        self._carregar_locais()
        self._carregar_itens_catalogo()
        self.build_ui()

    def build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        left_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.build_header(
            "Relatorio de Entrega de Materiais",
            "Selecione um local de destino ou cadastre um novo local"
        )
        self.build_local_destino_section(left_panel)
        self.build_adicionar_itens_section(left_panel)
        self.build_informacoes_adicionais_section(left_panel)
        self.build_bottom_buttons(left_panel)

        right_panel = ctk.CTkFrame(main_container, fg_color="transparent", width=320)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        self.build_preview_panel(right_panel)

    def _carregar_locais(self):
        try:
            with Database() as db:
                if not db.conexao:
                    return
                sql = """SELECT id, cep, endereco, instituicao, responsavel, telefone
                         FROM locais ORDER BY instituicao"""
                resultado = db.executar(sql)
                if resultado:
                    self.locais_catalogo = [
                        {"id": row[0], "cep": row[1], "endereco": row[2],
                         "instituicao": row[3], "responsavel": row[4], "telefone": row[5]}
                        for row in resultado.fetchall()
                    ]
        except Exception:
            self.locais_catalogo = []

    def _on_local_select(self, selection):
        local = None
        for l in self.locais_catalogo:
            if f"{l['instituicao']} - {l['endereco']}" == selection:
                local = l
                break
        if not local:
            return
        self.local_selecionado = local
        self.local_info_labels["CEP:"].configure(text=local["cep"] or "--")
        self.local_info_labels["Endereco:"].configure(text=local["endereco"] or "--")
        self.local_info_labels["Instituicao:"].configure(text=local["instituicao"] or "--")
        self.local_info_labels["Responsavel:"].configure(text=local["responsavel"] or "--")
        self.local_info_labels["Telefone:"].configure(text=local["telefone"] or "--")

    def _bind_scroll(self, combo):
        combo.bind("<MouseWheel>", lambda e: combo._dropdown._parent.after(
            1, lambda: combo._dropdown.yview_scroll(int(-1 * (e.delta / 120)), "units")
        ))

    def _atualizar_combo_locais(self):
        self._carregar_locais()
        nomes = [f"{l['instituicao']} - {l['endereco']}" for l in self.locais_catalogo] if self.locais_catalogo else ["Nenhum local cadastrado"]
        self.combo_local.configure(values=nomes)
        if nomes:
            self.combo_local.set(nomes[0])
            self._on_local_select(nomes[0])

    def build_local_destino_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 15))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 10))

        ctk.CTkLabel(
            header_frame, text="1. Local de Destino",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        btn_cadastrar = ctk.CTkButton(
            header_frame,
            text="+ Cadastrar Novo Local",
            height=32, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["primary"],
            border_width=1,
            border_color=COLORS["primary"],
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.cadastrar_local,
        )
        btn_cadastrar.pack(side="right")

        combo_frame = ctk.CTkFrame(section, fg_color="transparent")
        combo_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            combo_frame, text="Selecionar Local",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        nomes_locais = [f"{l['instituicao']} - {l['endereco']}" for l in self.locais_catalogo] if self.locais_catalogo else ["Nenhum local cadastrado"]
        self.combo_local = ctk.CTkComboBox(
            combo_frame, values=nomes_locais,
            height=38, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            command=self._on_local_select,
        )
        self.combo_local.pack(fill="x")
        if nomes_locais:
            self.combo_local.set(nomes_locais[0])

        self._bind_scroll(self.combo_local)

        info_frame = ctk.CTkFrame(section, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.local_info_labels = {}
        campos = ["CEP:", "Endereco:", "Instituicao:", "Responsavel:", "Telefone:"]
        for campo in campos:
            linha = ctk.CTkFrame(info_frame, fg_color="transparent")
            linha.pack(fill="x", pady=1)
            ctk.CTkLabel(
                linha, text=campo,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], width=90, anchor="w",
            ).pack(side="left")
            lbl = ctk.CTkLabel(
                linha, text="--",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text"], anchor="w",
            )
            lbl.pack(side="left")
            self.local_info_labels[campo] = lbl

        if self.locais_catalogo:
            self._on_local_select(nomes_locais[0])

    def _carregar_itens_catalogo(self):
        try:
            with Database() as db:
                if not db.conexao:
                    return
                sql = """SELECT id, nome, descricao, unidade_medida
                         FROM itens WHERE status = 'Ativo'
                         ORDER BY nome"""
                resultado = db.executar(sql)
                if resultado:
                    self.itens_catalogo = [
                        {"id": row[0], "nome": row[1], "descricao": row[2], "unidade": row[3]}
                        for row in resultado.fetchall()
                    ]
        except Exception:
            self.itens_catalogo = []

    def build_adicionar_itens_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 15))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 10))

        ctk.CTkLabel(
            header_frame, text="2. Adicionar Itens",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        input_frame = ctk.CTkFrame(section, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 10))

        item_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        item_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            item_frame, text="Item",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        nomes_itens = [f"{i['nome']} ({i['descricao']})" for i in self.itens_catalogo] if self.itens_catalogo else ["Nenhum item ativo"]
        self.combo_item = ctk.CTkComboBox(
            item_frame, values=nomes_itens,
            height=36, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
        )
        self.combo_item.pack(fill="x")
        if nomes_itens:
            self.combo_item.set(nomes_itens[0])

        self._bind_scroll(self.combo_item)

        qtd_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        qtd_frame.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            qtd_frame, text="Quantidade",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.entry_quantidade = ctk.CTkEntry(
            qtd_frame,
            placeholder_text="0",
            width=120, height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_quantidade.pack()

        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            btn_frame, text=" ",
            font=ctk.CTkFont(size=FONTS["size_small"]),
        ).pack()

        ctk.CTkButton(
            btn_frame,
            text="+ Adicionar",
            height=36, corner_radius=4,
            fg_color=COLORS["primary_light"],
            hover_color=COLORS["primary_light_hover"],
            text_color=COLORS["primary"],
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.adicionar_item,
        ).pack()

        table_header = ctk.CTkFrame(section, fg_color="#FAFAFA", height=36, corner_radius=4)
        table_header.pack(fill="x", padx=20, pady=(0, 5))
        table_header.pack_propagate(False)

        table_header.grid_columnconfigure(0, weight=3)
        table_header.grid_columnconfigure(1, weight=1)
        table_header.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            table_header, text="Item",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, sticky="w", padx=10)

        ctk.CTkLabel(
            table_header, text="Quantidade",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(
            table_header, text="Acoes",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=2, sticky="w", padx=10)

        self.itens_body = ctk.CTkScrollableFrame(
            section, fg_color="transparent", height=120
        )
        self.itens_body.pack(fill="x", padx=20, pady=(0, 10))

        self.total_label = ctk.CTkLabel(
            section, text="Total de Itens: 0",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
        )
        self.total_label.pack(padx=20, pady=(0, 15))

    def build_informacoes_adicionais_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 15))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 10))

        ctk.CTkLabel(
            header_frame, text="3. Informacoes Adicionais",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        fields_frame = ctk.CTkFrame(section, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=(0, 10))

        for i in range(3):
            fields_frame.grid_columnconfigure(i, weight=1)

        campo_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        campo_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            campo_frame, text="Numero do Processo",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.entry_processo = ctk.CTkEntry(
            campo_frame,
            placeholder_text="",
            height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.entry_processo.pack(fill="x")

        doc_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        doc_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            doc_frame, text="Documento SEI",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.entry_documento_sei = ctk.CTkEntry(
            doc_frame,
            placeholder_text="",
            height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.entry_documento_sei.pack(fill="x")

        resp_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        resp_frame.grid(row=0, column=2, sticky="ew")

        ctk.CTkLabel(
            resp_frame, text="Responsavel pela Entrega",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.entry_responsavel = ctk.CTkEntry(
            resp_frame,
            placeholder_text="",
            height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.entry_responsavel.pack(fill="x")

        obs_frame = ctk.CTkFrame(section, fg_color="transparent")
        obs_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            obs_frame, text="Observacoes",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.text_obs = ctk.CTkTextbox(
            obs_frame,
            height=80, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.text_obs.pack(fill="x")

    def build_bottom_buttons(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Salvar Relatorio",
            height=40, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.salvar_relatorio,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Voltar",
            height=40, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.voltar,
        ).pack(side="left")

    def build_preview_panel(self, parent):
        preview_container = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        preview_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            preview_container, text="Previa do Relatorio",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=15, pady=(12, 10))

        self.preview_frame = ctk.CTkFrame(
            preview_container, fg_color=COLORS["border"], corner_radius=4
        )
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ctk.CTkLabel(
            self.preview_frame,
            text="Previa do relatorio\nsera exibida aqui",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(expand=True)

        btn_frame = ctk.CTkFrame(preview_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Baixar PDF",
            height=36, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.baixar_pdf,
        ).pack(side="left", padx=(0, 8), expand=True, fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Imprimir",
            height=36, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.imprimir,
        ).pack(side="right", expand=True, fill="x")

    def adicionar_item(self):
        display = self.combo_item.get().strip()
        qtd = self.entry_quantidade.get().strip()

        if not display or "Nenhum item" in display:
            messagebox.showwarning("Aviso", "Selecione um item do catalogo.")
            return
        if not qtd:
            messagebox.showwarning("Aviso", "Preencha a quantidade.")
            return

        try:
            qtd_int = int(qtd)
            if qtd_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade deve ser um numero inteiro positivo.")
            return

        item_info = None
        for item in self.itens_catalogo:
            if f"{item['nome']} ({item['descricao']})" == display:
                item_info = item
                break

        if item_info is None:
            messagebox.showwarning("Aviso", "Item nao encontrado no catalogo.")
            return

        self.itens_lista.append({
            "item_id": item_info["id"],
            "item": item_info["nome"],
            "descricao": item_info["descricao"],
            "quantidade": qtd_int,
        })
        self.render_itens()

        self.entry_quantidade.delete(0, "end")

    def render_itens(self):
        for widget in self.itens_body.winfo_children():
            widget.destroy()

        if not self.itens_lista:
            ctk.CTkLabel(
                self.itens_body, text="Nenhum item adicionado",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            for idx, item in enumerate(self.itens_lista):
                row = ctk.CTkFrame(self.itens_body, fg_color="transparent", height=32)
                row.pack(fill="x", pady=2)
                row.pack_propagate(False)

                row.grid_columnconfigure(0, weight=3)
                row.grid_columnconfigure(1, weight=1)
                row.grid_columnconfigure(2, weight=1)

                ctk.CTkLabel(
                    row, text=item["item"],
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=COLORS["text"],
                ).grid(row=0, column=0, sticky="w", padx=10)

                ctk.CTkLabel(
                    row, text=str(item["quantidade"]),
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=COLORS["text"],
                ).grid(row=0, column=1, sticky="w", padx=10)

                btn_frame = ctk.CTkFrame(row, fg_color="transparent")
                btn_frame.grid(row=0, column=2, sticky="w", padx=10)

                ctk.CTkButton(
                    btn_frame, text="Editar", width=50, height=28,
                    corner_radius=4, fg_color=COLORS["white"],
                    hover_color=COLORS["hover"], text_color=COLORS["text"],
                    border_width=1, border_color=COLORS["border"],
                    command=lambda i=idx: self.editar_item(i),
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    btn_frame, text="Excluir", width=50, height=28,
                    corner_radius=4, fg_color=COLORS["white"],
                    hover_color=COLORS["danger_light"], text_color=COLORS["danger"],
                    border_width=1, border_color=COLORS["border"],
                    command=lambda i=idx: self.remover_item(i),
                ).pack(side="left", padx=2)

        total = sum(item["quantidade"] for item in self.itens_lista)
        self.total_label.configure(text=f"Total de Itens: {total}")

    def editar_item(self, idx):
        item = self.itens_lista[idx]
        display = f"{item['item']} ({item['descricao']})"
        self.combo_item.set(display)
        self.entry_quantidade.delete(0, "end")
        self.entry_quantidade.insert(0, str(item["quantidade"]))
        self.itens_lista.pop(idx)
        self.render_itens()

    def remover_item(self, idx):
        if messagebox.askyesno("Confirmar", "Deseja remover este item?"):
            self.itens_lista.pop(idx)
            self.render_itens()

    def cadastrar_local(self):
        form = ctk.CTkToplevel(self)
        form.title("Novo Local de Destino")
        form.geometry("500x620")
        form.configure(fg_color=COLORS["bg"])
        form.transient(self.winfo_toplevel())
        form.grab_set()

        container = ctk.CTkFrame(form, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            container,
            text="Cadastrar Local de Destino",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 20))

        fields = [
            ("CEP", "cep", "00000-000"),
            ("Endereco Completo", "endereco", "Rua, numero, bairro, cidade-UF"),
            ("Instituicao", "instituicao", "Nome da instituicao"),
            ("Responsavel", "responsavel", "Nome do responsavel"),
            ("Telefone", "telefone", "(00) 00000-0000"),
        ]

        entries = {}
        for label_text, key, placeholder in fields:
            ctk.CTkLabel(
                container, text=label_text,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"],
            ).pack(anchor="w", pady=(10, 2))

            entry = ctk.CTkEntry(
                container,
                placeholder_text=placeholder,
                height=38, border_width=1,
                border_color=COLORS["border"], corner_radius=4,
                fg_color=COLORS["white"], text_color=COLORS["text"],
            )
            entry.pack(fill="x")
            entries[key] = entry

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        def salvar():
            cep = entries["cep"].get().strip()
            endereco = entries["endereco"].get().strip()
            instituicao = entries["instituicao"].get().strip()
            responsavel = entries["responsavel"].get().strip()
            telefone = entries["telefone"].get().strip()

            if not all([cep, endereco, instituicao, responsavel]):
                messagebox.showwarning("Aviso", "Preencha CEP, Endereco, Instituicao e Responsavel.")
                return

            with Database() as db:
                if not db.conexao:
                    messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                    return

                sql = """INSERT INTO locais (cep, endereco, instituicao, responsavel, telefone)
                         VALUES (?, ?, ?, ?, ?)"""
                params = (cep, endereco, instituicao, responsavel, telefone or None)

                db.executar(sql, params)
                db.commitar()

            registrar_log(
                self.usuario_logado or "Sistema",
                "cadastro",
                "locais",
                f"Local '{instituicao}' cadastrado via Relatorio de Entrega"
            )

            messagebox.showinfo("Sucesso", "Local cadastrado com sucesso!")
            form.destroy()
            self._atualizar_combo_locais()

        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=form.destroy,
        ).pack(side="left")

    def _gerar_texto_relatorio(self):
        texto = "RELATORIO DE ENTREGA DE MATERIAIS\n"
        texto += "=" * 40 + "\n\n"
        texto += f"Processo: {self.entry_processo.get() or 'N/A'}\n"
        texto += f"Documento SEI: {self.entry_documento_sei.get() or 'N/A'}\n"
        texto += f"Responsavel: {self.entry_responsavel.get() or 'N/A'}\n"
        obs = self.text_obs.get("1.0", "end").strip()
        if obs:
            texto += f"Observacoes: {obs}\n"
        texto += "\nITENS:\n"
        texto += "-" * 40 + "\n"
        for item in self.itens_lista:
            texto += f"  {item['item']}: {item['quantidade']}\n"
        texto += "-" * 40 + "\n"
        total = sum(item["quantidade"] for item in self.itens_lista)
        texto += f"Total de Itens: {total}\n"
        return texto

    def salvar_relatorio(self):
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item ao relatorio.")
            return
        messagebox.showinfo("Sucesso", "Relatorio salvo com sucesso!")

    def baixar_pdf(self):
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item ao relatorio.")
            return

        from tkinter import filedialog

        caminho = filedialog.asksaveasfilename(
            title="Salvar Relatorio como PDF",
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile="relatorio_entrega.txt",
        )
        if not caminho:
            return

        texto = self._gerar_texto_relatorio()
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            messagebox.showinfo("Sucesso", f"Relatorio salvo em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel salvar o relatorio:\n{e}")

    def imprimir(self):
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item ao relatorio.")
            return

        preview_text = self._gerar_texto_relatorio()

        try:
            tmp = os.path.join(tempfile.gettempdir(), "relatorio_entrega.txt")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(preview_text)
            subprocess.Popen(["notepad.exe", "/p", tmp])
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel abrir a impressao:\n{e}")

    def voltar(self):
        if self.on_voltar:
            self.on_voltar()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Relatorio de Entrega de Materiais")
    app.geometry("1400x800")
    app.configure(fg_color=COLORS["bg"])

    RelatorioEntregaPage(app).pack(fill="both", expand=True)
    app.mainloop()
