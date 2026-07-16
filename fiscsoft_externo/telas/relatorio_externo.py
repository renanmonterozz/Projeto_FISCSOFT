import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


class RelatorioExterno(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator

        self.build_header("Relatorio",
                          "Visualize o resumo das suas notas fiscais e processos")
        self.build_filter_bar()
        self.build_stats_cards()
        self.build_relatorio_content()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_periodo = self.build_filter_entry(row, "Periodo (mm/aaaa)", 160)

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(btn_frame, "  Gerar Relatorio", None, self.gerar_relatorio,
                              fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                              text_color="white", border=False, bold=True)
        self.build_action_btn(btn_frame, "  Limpar", None, self.limpar_filtros)

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        card_data = [
            ("Total Notas", "Notas enviadas", "0"),
            ("Aprovadas", "Notas aprovadas", "0"),
            ("Pendentes", "Aguardando analise", "0"),
            ("Valor Total(R$)", "Valor acumulado", "R$ 0,00"),
        ]

        self.stat_labels = {}
        icons = ["\U0001f4cb", "\u2705", "\u23F3", "\U0001f4b0"]

        for i, (titulo, subtitulo, valor) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards_frame, fg_color=COLORS["white"], corner_radius=4,
                border_width=1, border_color=COLORS["border"]
            )
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=15)

            icon_circle = ctk.CTkFrame(
                inner, fg_color=COLORS["primary_light"],
                width=48, height=48, corner_radius=24
            )
            icon_circle.pack(side="left", padx=(0, 12))
            icon_circle.pack_propagate(False)

            ctk.CTkLabel(
                icon_circle, text=icons[i],
                font=ctk.CTkFont(size=18),
                text_color=COLORS["primary"]
            ).pack(expand=True)

            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                text_frame, text=titulo,
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                text_color=COLORS["text"], anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame, text=subtitulo,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            lbl_valor = ctk.CTkLabel(
                card, text=valor,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=COLORS["text"]
            )
            lbl_valor.pack(pady=(0, 15))
            self.stat_labels[titulo] = lbl_valor

        self._atualizar_cards()

    def build_relatorio_content(self):
        section = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        dot = ctk.CTkFrame(
            header_frame, fg_color=COLORS["primary"],
            width=12, height=12, corner_radius=6
        )
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="Detalhamento por Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        columns = [
            "Numero NF", "Data Emissao", "Valor(R$)",
            "Quantidade Itens", "Status"
        ]
        weights = [2, 2, 2, 2, 1]

        header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=40, corner_radius=0)
        header.pack(fill="x", padx=15, pady=(5, 0))
        header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=i, sticky="w", padx=5)

        self.table_body = ctk.CTkScrollableFrame(
            section, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        footer = ctk.CTkFrame(section, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        self.lbl_total = ctk.CTkLabel(
            footer, text="Total de Registros: 0",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_total.pack(side="left")

        self.lbl_valor_total = ctk.CTkLabel(
            footer, text="Valor Total: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_valor_total.pack(side="right")

        self._carregar_dados()

    def _carregar_dados(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.id_infrator:
            ctk.CTkLabel(
                self.table_body, text="Nenhum dado encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        with Database() as db:
            if not db.conexao:
                return

            sql = """SELECT nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota,
                            COUNT(p.lote) as qtd_itens
                     FROM "nota fiscal" nf
                     JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                     LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                        AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                     WHERE t."infrator_id_infrator" = ?
                     GROUP BY nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota
                     ORDER BY nf.data DESC"""
            try:
                resultado = db.executar(sql, (self.id_infrator,))
                dados = []
                if resultado:
                    for row in resultado.fetchall():
                        raw_data = row[1]
                        if hasattr(raw_data, "strftime"):
                            data_fmt = raw_data.strftime("%d/%m/%Y")
                        elif raw_data:
                            from datetime import datetime as _dt
                            try:
                                data_fmt = _dt.strptime(str(raw_data), "%Y-%m-%d").strftime("%d/%m/%Y")
                            except Exception:
                                data_fmt = str(raw_data)
                        else:
                            data_fmt = "--"
                        dados.append({
                            "nota_fiscal": row[0] or "--",
                            "data": data_fmt,
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
                            "qtd_itens": row[4] if row[4] else 0,
                        })
            except Exception:
                dados = []

        if not dados:
            ctk.CTkLabel(
                self.table_body, text="Nenhum dado encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        weights = [2, 2, 2, 2, 1]
        for item in dados:
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=48)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            valor_formatado = f"R$ {item['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            dados_row = [
                item["nota_fiscal"], item["data"], valor_formatado,
                str(item["qtd_itens"])
            ]

            for i, valor in enumerate(dados_row):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(
                    cols, text=valor,
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=cor, anchor="w"
                ).grid(row=0, column=i, sticky="w", padx=5)

            status_frame = ctk.CTkFrame(linha, fg_color="transparent", width=100)
            status_frame.pack(side="right", padx=(0, 10))
            status_frame.pack_propagate(False)

            if item["status"] == "Aprovada":
                status_color = COLORS["success_dark"]
                status_text = "\u2714 Aprovada"
            elif item["status"] == "Rejeitada":
                status_color = COLORS["danger"]
                status_text = "\u2718 Rejeitada"
            elif item["status"] == "Correcao Solicitada":
                status_color = "#D97706"
                status_text = "\u270F Correcao"
            else:
                status_color = COLORS["warning"]
                status_text = "\u26A0 Pendente"

            ctk.CTkLabel(
                status_frame, text=status_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=status_color
            ).pack(expand=True)

        self.lbl_total.configure(text=f"Total de Registros: {len(dados)}")
        valor_total = sum(d["valor_total"] for d in dados)
        self.lbl_valor_total.configure(
            text=f"Valor Total: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _atualizar_cards(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            base = '''FROM "nota fiscal" nf
                      JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                      WHERE t."infrator_id_infrator" = ?'''

            try:
                r = db.executar(
                    f'SELECT COUNT(DISTINCT nf.nota_fiscal) {base}',
                    (self.id_infrator,)
                ).fetchone()
                total = r[0] if r else 0
            except Exception:
                total = 0

            try:
                r = db.executar(
                    f'SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Aprovada'',
                    (self.id_infrator,)
                ).fetchone()
                aprovadas = r[0] if r else 0
            except Exception:
                aprovadas = 0

            try:
                r = db.executar(
                    f'SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Pendente'',
                    (self.id_infrator,)
                ).fetchone()
                pendentes = r[0] if r else 0
            except Exception:
                pendentes = 0

            try:
                r = db.executar(
                    f'''SELECT COALESCE(SUM(nf.valor_total), 0) {base}''',
                    (self.id_infrator,)
                ).fetchone()
                valor_total = float(r[0]) if r else 0
            except Exception:
                valor_total = 0

        self.stat_labels["Total Notas"].configure(text=str(total))
        self.stat_labels["Aprovadas"].configure(text=str(aprovadas))
        self.stat_labels["Pendentes"].configure(text=str(pendentes))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)

    def gerar_relatorio(self):
        self._carregar_dados()
        self._atualizar_cards()

    def limpar_filtros(self):
        self.clear_entries(self.entry_periodo)
        self._carregar_dados()
        self._atualizar_cards()
