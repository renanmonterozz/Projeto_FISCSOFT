import _path  # noqa: F401

from datetime import datetime

import customtkinter as ctk

from config.styles import COLORS, FONTS
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from services.nota_fiscal_historico_service import NotaFiscalHistoricoService


class AuditoriaPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.service = NotaFiscalHistoricoService()
        self.registros = []

        self.build_header(
            "Auditoria de Notas Fiscais",
            "Consulte os eventos e motivos registrados no ciclo de cada nota fiscal.",
        )
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(
            row, "Buscar por NF, TCCM, usuario ou motivo...", 300
        )
        self.entry_processo = ctk.CTkEntry(
            row, width=150, height=36, placeholder_text="Processo/TCCM",
            border_width=1, border_color=COLORS["border"], corner_radius=4,
        )
        self.entry_processo.pack(side="left", padx=(8, 0))
        self.entry_nf = ctk.CTkEntry(
            row, width=130, height=36, placeholder_text="Numero NF",
            border_width=1, border_color=COLORS["border"], corner_radius=4,
        )
        self.entry_nf.pack(side="left", padx=(8, 0))
        self.combo_acao = ctk.CTkComboBox(
            row, width=190, height=36,
            values=["Todos", *self.service.ACOES],
            border_width=1, border_color=COLORS["border"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
        )
        self.combo_acao.pack(side="left", padx=(8, 0))
        self.combo_acao.set("Todos")

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(
            btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border=False, bold=True,
        )
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))
        self.colunas_place = [
            (0.00, 0.12, "w"),
            (0.12, 0.12, "w"),
            (0.24, 0.14, "w"),
            (0.38, 0.16, "w"),
            (0.54, 0.13, "w"),
            (0.67, 0.33, "w"),
        ]
        container = ctk.CTkFrame(
            self.table_frame, fg_color="transparent",
            border_width=1, border_color=COLORS["border"], corner_radius=4,
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)
        header = ctk.CTkFrame(container, fg_color=COLORS["table_header"], height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(fill="x", expand=True, padx=(10, 16))
        for texto, (rx, rw, anchor) in zip(
            ["Data/Hora", "NF", "Processo", "Acao", "Usuario", "Motivo"],
            self.colunas_place,
        ):
            ctk.CTkLabel(
                cols, text=texto, anchor=anchor,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)
        self.table_body = ctk.CTkScrollableFrame(container, fg_color=COLORS["white"], corner_radius=0)
        self.table_body.pack(fill="both", expand=True)
        self.registros = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        return self.service.listar()

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()
        if not self.registros:
            ctk.CTkLabel(
                self.table_body, text="Nenhum evento encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text_muted"],
            ).pack(pady=40)
            return
        for registro in self.registros:
            self._add_row(registro)

    def _add_row(self, registro):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=48)
        linha.pack(fill="x")
        linha.pack_propagate(False)
        ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")
        data_hora = registro.get("criado_em")
        if hasattr(data_hora, "strftime"):
            data_hora = data_hora.strftime("%d/%m/%Y %H:%M")
        else:
            data_hora = str(data_hora or "--")
        usuario = registro.get("usuario") or (
            f"Mat. {registro['agente_matricula']}" if registro.get("agente_matricula") else "--"
        )
        motivo = registro.get("motivo") or "--"
        valores = [
            data_hora, registro.get("nota_fiscal") or "--", registro.get("processo") or "--",
            self.service.rotulo_acao(registro.get("acao")), usuario, motivo,
        ]
        cols = ctk.CTkFrame(linha, fg_color="transparent")
        cols.pack(fill="x", expand=True, padx=(10, 0))
        for (rx, rw, anchor), texto in zip(self.colunas_place, valores):
            ctk.CTkLabel(
                cols, text=texto, anchor=anchor,
                font=ctk.CTkFont(size=FONTS["size_small"]), text_color=COLORS["text_muted"],
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

    def pesquisar(self):
        self.registros = self.service.listar(
            termo=self.entry_busca.get(),
            acao=self.combo_acao.get(),
            processo=self.entry_processo.get(),
            nota_fiscal=self.entry_nf.get(),
        )
        self.render_rows()

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.entry_processo.delete(0, "end")
        self.entry_nf.delete(0, "end")
        self.combo_acao.set("Todos")
        self.registros = self.carregar_do_banco()
        self.render_rows()
