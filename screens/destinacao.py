import _path  # noqa: F401

import subprocess
import os
import tempfile
from tkinter import messagebox

import customtkinter as ctk

from config.styles import COLORS, FONTS
from config.permissoes import pode_acao
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from services.destinacao_service import (
    DestinacaoService,
    RegraDestinacaoError,
    gerar_texto_relatorio,
    item_display,
    preparar_item,
    quantidade_disponivel,
    validar_local,
)
from screens.widgets import ComboBoxComSeta


class RelatorioEntregaPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, usuario_logado=None, processo_tccm=None, perfil="admin", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.processo_tccm = processo_tccm
        self.perfil = perfil
        self.pode_cadastrar_local = pode_acao(perfil, "gerenciar_locais")
        self.itens_lista = []
        self.local_selecionado = None
        self.locais_catalogo = []
        self.itens_catalogo = []
        self.service = DestinacaoService()

        self._carregar_locais()
        self._carregar_itens_catalogo()
        self.build_ui()

    def build_ui(self):
        self.build_bottom_buttons(self)

        self.build_header(
            "Relatorio de Entrega de Materiais",
            "Selecione um local de destino ou cadastre um novo local"
        )

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 0))

        self.build_local_destino_section(main_container)
        self.build_adicionar_itens_section(main_container)
        self.build_informacoes_adicionais_section(main_container)

    def _carregar_locais(self):
        try:
            self.locais_catalogo = self.service.listar_locais()
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
        section.pack(fill="x", pady=(0, 12))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(8, 6))

        ctk.CTkLabel(
            header_frame, text="1. Local de Destino",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        if self.pode_cadastrar_local:
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
        self.combo_local = ComboBoxComSeta(
            combo_frame, values=nomes_locais,
            height=34, border_width=1, border_color=COLORS["primary"],
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
        info_frame.pack(fill="x", padx=20, pady=(0, 10))

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
            self.itens_catalogo = self.service.listar_itens(self.processo_tccm)
        except Exception:
            self.itens_catalogo = []

    def _item_display(self, item):
        return item_display(item)

    def _on_item_select(self, selection):
        if not hasattr(self, "entry_quantidade"):
            return
        for item in self.itens_catalogo:
            if self._item_display(item) == selection:
                self.entry_quantidade.delete(0, "end")
                disponivel = self._quantidade_disponivel(item["id"])
                if disponivel:
                    self.entry_quantidade.insert(0, str(disponivel))
                    self.entry_quantidade.configure(placeholder_text=f"max: {disponivel}")
                elif disponivel == 0:
                    self.entry_quantidade.configure(placeholder_text="max: 0")
                else:
                    self.entry_quantidade.configure(placeholder_text="0")
                return

    def build_adicionar_itens_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 10))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(6, 4))

        ctk.CTkLabel(
            header_frame, text="2. Adicionar Itens",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        input_frame = ctk.CTkFrame(section, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 4))

        item_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        item_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            item_frame, text="Item",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        nomes_itens = [self._item_display(i) for i in self.itens_catalogo] if self.itens_catalogo else (["Nenhum item registrado no TCCM"] if self.processo_tccm else ["Nenhum item ativo"])
        self.combo_item = ComboBoxComSeta(
            item_frame, values=nomes_itens,
            height=30, border_width=1, border_color=COLORS["primary"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            command=self._on_item_select,
        )
        self.combo_item.pack(fill="x")
        if nomes_itens:
            self.combo_item.set(nomes_itens[0])
            self._on_item_select(nomes_itens[0])

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
            width=120, height=30, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_quantidade.pack()

        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="+ Adicionar",
            height=30, corner_radius=4,
            fg_color=COLORS["primary_light"],
            hover_color=COLORS["primary_light_hover"],
            text_color=COLORS["primary"],
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.adicionar_item,
        ).pack()

        table_header = ctk.CTkFrame(section, fg_color="#FAFAFA", height=26, corner_radius=4)
        table_header.pack(fill="x", padx=20, pady=(0, 4))
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
            section, fg_color="transparent", height=45
        )
        self.itens_body.pack(fill="x", padx=20, pady=(0, 4))

        self.total_label = ctk.CTkLabel(
            section, text="Total de Itens: 0",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
        )
        self.total_label.pack(padx=20, pady=(0, 6))

    def build_informacoes_adicionais_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 10))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(8, 6))

        ctk.CTkLabel(
            header_frame, text="3. Informacoes Adicionais",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        fields_frame = ctk.CTkFrame(section, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=(0, 6))

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
            height=32, border_width=1,
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
            height=32, border_width=1,
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
            height=32, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.entry_responsavel.pack(fill="x")

        obs_frame = ctk.CTkFrame(section, fg_color="transparent")
        obs_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            obs_frame, text="Observacoes",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.text_obs = ctk.CTkTextbox(
            obs_frame,
            height=60, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
        )
        self.text_obs.pack(fill="x")

    def build_bottom_buttons(self, parent):
        footer = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=0,
                              border_width=1, border_color=COLORS["border"])
        footer.pack(side="bottom", fill="x", pady=(10, 0))

        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(anchor="center", pady=12)

        ctk.CTkButton(
            inner,
            text="Baixar PDF",
            height=40, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.baixar_pdf,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            inner,
            text="Imprimir",
            height=40, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.imprimir,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            inner,
            text="Salvar Relatorio",
            height=40, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.salvar_relatorio,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            inner,
            text="Voltar",
            height=40, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.voltar,
        ).pack(side="left", padx=6)

    def _quantidade_disponivel(self, item_id):
        return quantidade_disponivel(self.itens_catalogo, self.itens_lista, item_id)

    def adicionar_item(self):
        display = self.combo_item.get().strip()
        qtd = self.entry_quantidade.get().strip()

        try:
            item = preparar_item(display, qtd, self.itens_catalogo, self.itens_lista)
        except RegraDestinacaoError as exc:
            messagebox.showwarning("Aviso", str(exc))
            return

        self.itens_lista.append(item)
        self.render_itens()

        self.entry_quantidade.delete(0, "end")
        self.entry_quantidade.configure(placeholder_text="0")

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
        display = self._item_display(item)
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

            try:
                mensagem = self.service.salvar_local(
                    cep,
                    endereco,
                    instituicao,
                    responsavel,
                    telefone,
                    self.usuario_logado,
                )
            except RegraDestinacaoError as exc:
                messagebox.showwarning("Aviso", str(exc))
                return
            except Exception as exc:
                messagebox.showerror("Erro", f"Nao foi possivel salvar o local:\n{exc}")
                return

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

    def salvar_relatorio(self):
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item ao relatorio.")
            return
        messagebox.showinfo("Sucesso", "Relatorio salvo com sucesso!")

    def _gerar_texto_relatorio(self):
        obs = self.text_obs.get("1.0", "end").strip()
        return gerar_texto_relatorio(
            self.entry_processo.get(),
            self.entry_documento_sei.get(),
            self.entry_responsavel.get(),
            obs,
            self.itens_lista,
        )

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
    app.configure(fg_color=COLORS["bg"])
    app.after(0, app.state, "zoomed")

    RelatorioEntregaPage(app).pack(fill="both", expand=True)
    app.mainloop()
