import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone


class RelatorioEntregaPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.itens_lista = []
        self.local_selecionado = None

        self.build_ui()

    def build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        left_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.build_header(
            "Relatório de Entrega de Materiais",
            "Selecione um local de destino ou cadastre um novo local"
        )
        self.build_gerar_btn(left_panel)
        self.build_local_destino_section(left_panel)
        self.build_adicionar_itens_section(left_panel)
        self.build_informacoes_adicionais_section(left_panel)
        self.build_bottom_buttons(left_panel)

        right_panel = ctk.CTkFrame(main_container, fg_color="transparent", width=320)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        self.build_preview_panel(right_panel)

    def build_gerar_btn(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))

        self.build_action_btn(
            btn_frame, "  Gerar Relatório", carregar_icone("relatorios.png"),
            self.gerar_relatorio, fg_color=COLORS["white"],
            hover_color=COLORS["hover"], text_color=COLORS["text"],
            border=True, bold=True,
        )

    def build_local_destino_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 15))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 10))

        ctk.CTkLabel(
            header_frame, text="① Local de Destino",
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

        search_frame = ctk.CTkFrame(section, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_busca_local = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar local...",
            height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_busca_local.pack(side="left", fill="x", expand=True)

        table_frame = ctk.CTkFrame(section, fg_color="transparent")
        table_frame.pack(fill="x", padx=20, pady=(0, 15))

        columns = ["CEP", "Endereço", "Instituição", "Responsável"]
        header = ctk.CTkFrame(table_frame, fg_color="#FAFAFA", height=36, corner_radius=4)
        header.pack(fill="x")
        header.pack_propagate(False)

        for i, col in enumerate(columns):
            header.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                header, text=col,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
            ).grid(row=0, column=i, sticky="w", padx=10)

        self.locais_body = ctk.CTkFrame(table_frame, fg_color="transparent", height=80)
        self.locais_body.pack(fill="x")
        self.locais_body.pack_propagate(False)

        ctk.CTkLabel(
            self.locais_body, text="Nenhum local selecionado",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(expand=True)

    def build_adicionar_itens_section(self, parent):
        section = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", pady=(0, 15))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 10))

        ctk.CTkLabel(
            header_frame, text="② Adicionar Itens",
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

        self.entry_item = ctk.CTkEntry(
            item_frame,
            placeholder_text="Nome do item",
            height=36, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_item.pack(fill="x")

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
            text="⊕ Adicionar",
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
            table_header, text="Ações",
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
            header_frame, text="③ Informações Adicionais",
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
            campo_frame, text="Número do Processo",
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
            resp_frame, text="Responsável pela Entrega",
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
            obs_frame, text="Observações",
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
            text="💾 Salvar Relatório",
            height=40, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.salvar_relatorio,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="← Voltar",
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
            preview_container, text="Prévia do Relatório",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=15, pady=(12, 10))

        self.preview_frame = ctk.CTkFrame(
            preview_container, fg_color=COLORS["border"], corner_radius=4
        )
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ctk.CTkLabel(
            self.preview_frame,
            text="Prévia do relatório\nserá exibida aqui",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(expand=True)

        btn_frame = ctk.CTkFrame(preview_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="↓ Baixar PDF",
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
            text="🖨 Imprimir",
            height=36, corner_radius=4,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self.imprimir,
        ).pack(side="right", expand=True, fill="x")

    def adicionar_item(self):
        item = self.entry_item.get().strip()
        qtd = self.entry_quantidade.get().strip()

        if not item or not qtd:
            messagebox.showwarning("Aviso", "Preencha o nome do item e a quantidade.")
            return

        try:
            qtd_int = int(qtd)
            if qtd_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade deve ser um número inteiro positivo.")
            return

        self.itens_lista.append({"item": item, "quantidade": qtd_int})
        self.render_itens()

        self.entry_item.delete(0, "end")
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
                    btn_frame, text="✏️", width=28, height=28,
                    corner_radius=4, fg_color=COLORS["white"],
                    hover_color=COLORS["hover"], text_color=COLORS["text"],
                    border_width=1, border_color=COLORS["border"],
                    command=lambda i=idx: self.editar_item(i),
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    btn_frame, text="🗑️", width=28, height=28,
                    corner_radius=4, fg_color=COLORS["white"],
                    hover_color=COLORS["danger_light"], text_color=COLORS["danger"],
                    border_width=1, border_color=COLORS["border"],
                    command=lambda i=idx: self.remover_item(i),
                ).pack(side="left", padx=2)

        total = sum(item["quantidade"] for item in self.itens_lista)
        self.total_label.configure(text=f"Total de Itens: {total}")

    def editar_item(self, idx):
        item = self.itens_lista[idx]
        self.entry_item.delete(0, "end")
        self.entry_item.insert(0, item["item"])
        self.entry_quantidade.delete(0, "end")
        self.entry_quantidade.insert(0, str(item["quantidade"]))
        self.itens_lista.pop(idx)
        self.render_itens()

    def remover_item(self, idx):
        if messagebox.askyesno("Confirmar", "Deseja remover este item?"):
            self.itens_lista.pop(idx)
            self.render_itens()

    def cadastrar_local(self):
        messagebox.showinfo("Info", "Funcionalidade de cadastro de local em desenvolvimento.")

    def gerar_relatorio(self):
        messagebox.showinfo("Info", "Gerando relatório...")

    def salvar_relatorio(self):
        messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")

    def baixar_pdf(self):
        messagebox.showinfo("Info", "Funcionalidade de download em desenvolvimento.")

    def imprimir(self):
        messagebox.showinfo("Info", "Funcionalidade de impressão em desenvolvimento.")

    def voltar(self):
        if self.on_voltar:
            self.on_voltar()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Relatório de Entrega de Materiais")
    app.geometry("1400x800")
    app.configure(fg_color=COLORS["bg"])

    RelatorioEntregaPage(app).pack(fill="both", expand=True)
    app.mainloop()
