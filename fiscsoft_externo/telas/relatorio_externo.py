import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk
from tkinter import messagebox

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
                     JOIN tccm t ON nf.processo = t.processo
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
            status_frame.pack(side="right", padx=(0, 5))
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

            btn_detalhes = ctk.CTkButton(
                linha, text="Detalhes", height=28, width=80, corner_radius=4,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                text_color="white", border_width=0,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                command=lambda nf=item["nota_fiscal"]: self._ver_detalhes(nf),
            )
            btn_detalhes.pack(side="right", padx=(0, 10))

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
                      JOIN tccm t ON nf.processo = t.processo
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
                    f"SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Aprovada'",
                    (self.id_infrator,)
                ).fetchone()
                aprovadas = r[0] if r else 0
            except Exception:
                aprovadas = 0

            try:
                r = db.executar(
                    f"SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Pendente'",
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

    def _ver_detalhes(self, nota_fiscal):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Detalhes da NF {nota_fiscal}")
        popup.geometry("650x550+{}+{}".format(
            (popup.winfo_screenwidth() - 650) // 2,
            (popup.winfo_screenheight() - 550) // 2
        ))
        popup.resizable(False, False)
        popup.configure(fg_color=COLORS["white"])
        popup.transient(self)
        popup.grab_set()

        container = ctk.CTkFrame(
            popup, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        top_bar = ctk.CTkFrame(container, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 0))

        ctk.CTkLabel(
            top_bar, text=f"Nota Fiscal #{nota_fiscal}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            top_bar, text="Detalhes completos da nota fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        dados_nf = self._buscar_dados_nf(nota_fiscal)

        info_card = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        info_card.pack(fill="x", padx=25, pady=(15, 0))

        ctk.CTkLabel(
            info_card, text="Dados da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        campos = [
            ("Numero NF:", dados_nf.get("nota_fiscal", "--")),
            ("Data Emissao:", dados_nf.get("data", "--")),
            ("Chave de Acesso:", dados_nf.get("chave", "--")),
            ("Valor Total:", dados_nf.get("valor_total_fmt", "R$ 0,00")),
            ("Status:", dados_nf.get("status", "--")),
            ("Processo:", dados_nf.get("processo", "--")),
        ]

        for label_text, valor in campos:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=(0, 5))

            ctk.CTkLabel(
                row, text=label_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor="w", width=140
            ).pack(side="left")

            ctk.CTkLabel(
                row, text=valor,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text"], anchor="w"
            ).pack(side="left")

        itens_card = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        itens_card.pack(fill="both", expand=True, padx=25, pady=(15, 0))

        ctk.CTkLabel(
            itens_card, text="Itens da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        itens = dados_nf.get("itens", [])

        if not itens:
            ctk.CTkLabel(
                itens_card, text="Nenhum item encontrado",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=15)
        else:
            header = ctk.CTkFrame(itens_card, fg_color=COLORS["table_header"], height=36, corner_radius=0)
            header.pack(fill="x", padx=15, pady=(5, 0))
            header.pack_propagate(False)

            hdr_cols = ctk.CTkFrame(header, fg_color="transparent")
            hdr_cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            pesos = [3, 1, 2, 2]
            for i in range(4):
                hdr_cols.grid_columnconfigure(i, weight=pesos[i])

            titulos = ["Item", "Qtd.", "Preco Unit. (R$)", "Subtotal (R$)"]
            for i, titulo in enumerate(titulos):
                ctk.CTkLabel(
                    hdr_cols, text=titulo,
                    font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                    text_color=COLORS["text_muted"]
                ).grid(row=0, column=i, sticky="w", padx=5)

            scroll = ctk.CTkScrollableFrame(
                itens_card, fg_color=COLORS["white"], corner_radius=0, height=120
            )
            scroll.pack(fill="both", expand=True, padx=15, pady=(5, 10))

            for idx, item in enumerate(itens):
                linha = ctk.CTkFrame(scroll, fg_color="transparent", height=32)
                linha.pack(fill="x")
                linha.pack_propagate(False)

                if idx < len(itens) - 1:
                    ctk.CTkFrame(scroll, fg_color="#E0E0E0", height=1).pack(fill="x")

                l_cols = ctk.CTkFrame(linha, fg_color="transparent")
                l_cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

                for i in range(4):
                    l_cols.grid_columnconfigure(i, weight=pesos[i])

                preco_fmt = f"R$ {item['preco_unitario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                subtot_fmt = f"R$ {item['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                valores = [item["nome"], str(item["quantidade"]), preco_fmt, subtot_fmt]
                for i, val in enumerate(valores):
                    cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                    ctk.CTkLabel(
                        l_cols, text=val,
                        font=ctk.CTkFont(size=FONTS["size_small"]),
                        text_color=cor, anchor="w"
                    ).grid(row=0, column=i, sticky="w", padx=5)

        ctk.CTkButton(
            container, text="Fechar", height=36, corner_radius=4,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=popup.destroy
        ).pack(pady=(15, 15))

    def _buscar_dados_nf(self, nota_fiscal):
        dados = {}
        with Database() as db:
            if not db.conexao:
                return dados

            try:
                sql = """SELECT nf.nota_fiscal, nf.data, nf.chave_de_acesso,
                                nf.valor_total, nf.status_nota, nf.processo
                         FROM "nota fiscal" nf
                         JOIN tccm t ON nf.processo = t.processo
                         WHERE nf.nota_fiscal = ?
                           AND t."infrator_id_infrator" = ?
                         LIMIT 1"""
                resultado = db.executar(sql, (nota_fiscal, self.id_infrator,))
                row = resultado.fetchone() if resultado else None
                if row:
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

                    valor = float(row[3]) if row[3] else 0
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    dados = {
                        "nota_fiscal": row[0] or "--",
                        "data": data_fmt,
                        "chave": row[2] or "--",
                        "valor_total": valor,
                        "valor_total_fmt": valor_fmt,
                        "status": row[4] or "Pendente",
                        "processo": row[5] or "--",
                    }
            except Exception:
                pass

            try:
                sql_itens = """SELECT p.nome_item, p.quantidade, p.preco_unitario
                               FROM produtos p
                               WHERE p."nota fiscal_nota_fiscal" = ?
                               ORDER BY p.lote"""
                resultado_itens = db.executar(sql_itens, (nota_fiscal,))
                itens = []
                if resultado_itens:
                    for item_row in resultado_itens.fetchall():
                        qtd = int(item_row[1]) if item_row[1] else 0
                        preco = float(item_row[2]) if item_row[2] else 0
                        itens.append({
                            "nome": item_row[0] or "--",
                            "quantidade": qtd,
                            "preco_unitario": preco,
                            "subtotal": qtd * preco,
                        })
                dados["itens"] = itens
            except Exception:
                dados["itens"] = []

        return dados
