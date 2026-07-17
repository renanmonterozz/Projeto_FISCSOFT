import _path  # noqa: F401

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


class MenuInicialPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, perfil="admin", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.perfil = perfil

        titulo = "Menu do Administrador" if perfil == "admin" else "Menu do Agente"
        subtitulo = "Gerencie usuarios, relatorios e informacoes do sistema"
        self.build_header(titulo, subtitulo)
        self.build_stats_cards()
        self.build_notas_table()

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        card_data = [
            ("Notas Fiscais", "Total de notas", "0"),
            ("Itens Recebidos", "Total de itens", "0"),
            ("Valor Total(R$)", "Valor acumulado", "R$ 0,00"),
            ("Tccms Ativos", "Tccms cadastrados", "0"),
        ]

        self.stat_labels = {}
        icons = ["\U0001f4cb", "\U0001f4e6", "\U0001f4b0", "\U0001f464"]

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

        self.atualizar_cards()

    def build_notas_table(self):
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
            header_frame, text="Notas Fiscais Recebidas",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        columns = [
            "Numero da NF", "Chave de acesso", "Data de Emissao",
            "Itens", "Valor Total(R$)", "Usuario", "Status"
        ]
        weights = [2, 3, 2, 1, 2, 2, 1]

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
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 5))

        footer = ctk.CTkFrame(section, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        self.lbl_total_registros = ctk.CTkLabel(
            footer, text="Total de Registros: 0",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_total_registros.pack(side="left")

        self.lbl_valor_total = ctk.CTkLabel(
            footer, text="Valor Total: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_valor_total.pack(side="right")

        self.notas = self._carregar_notas()
        self._render_rows()

    def _carregar_notas(self):
        with Database() as db:
            if not db.conexao:
                return []

            sql = """SELECT nf.nota_fiscal, nf.chave_de_acesso, nf.data,
                            nf.valor_total, nf.status_nota,
                            a.nome_agente,
                            COUNT(p.lote) as qtd_itens
                     FROM "nota fiscal" nf
                     LEFT JOIN "agente ibama" a ON a.matricula = nf."agente ibama_matricula"
                     LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                        AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                     GROUP BY nf.nota_fiscal, nf.chave_de_acesso, nf.data,
                            nf.valor_total, nf.status_nota, a.nome_agente
                     ORDER BY nf.data DESC"""
            try:
                resultados = db.executar(sql)
                notas = []
                if resultados:
                    for row in resultados.fetchall():
                        notas.append({
                            "nota_fiscal": row[0] or "--",
                            "chave_de_acesso": row[1] or "--",
                            "data": _fmt_date(row[2]),
                            "valor_total": float(row[3]) if row[3] else 0,
                            "status": row[4] or "Pendente",
                            "usuario": row[5] or "--",
                            "qtd_itens": row[6] if row[6] else 0,
                        })
                return notas
            except Exception:
                return []

    def _render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.notas:
            ctk.CTkLabel(
                self.table_body, text="Nenhuma nota fiscal cadastrada",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        weights = [2, 3, 2, 1, 2, 2, 1]
        for idx, nota in enumerate(self.notas):
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=44)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            dados = [
                nota["nota_fiscal"], nota["chave_de_acesso"], nota["data"],
                str(nota["qtd_itens"]), f"R$ {nota['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                nota["usuario"]
            ]

            for i, valor in enumerate(dados):
                cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
                ctk.CTkLabel(
                    cols, text=valor,
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=cor, anchor="w"
                ).grid(row=0, column=i, sticky="w", padx=5)

            status_frame = ctk.CTkFrame(linha, fg_color="transparent", width=80)
            status_frame.pack(side="right", padx=(0, 10))
            status_frame.pack_propagate(False)

            if nota["status"] == "Aprovada":
                status_color = COLORS["success_dark"]
                status_text = "\u2714"
            elif nota["status"] == "Rejeitada":
                status_color = COLORS["danger"]
                status_text = "\u2718"
            else:
                status_color = COLORS["warning"]
                status_text = "\u26A0"

            status_icon = ctk.CTkLabel(
                status_frame, text=status_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=status_color
            )
            status_icon.pack(expand=True)

        self.lbl_total_registros.configure(text=f"Total de Registros: {len(self.notas)}")
        valor_total = sum(n["valor_total"] for n in self.notas)
        self.lbl_valor_total.configure(
            text=f"Valor Total: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def atualizar_cards(self):
        with Database() as db:
            if not db.conexao:
                return

            try:
                r = db.executar('SELECT COUNT(DISTINCT nota_fiscal) FROM "nota fiscal"').fetchone()
                total_nf = r[0] if r else 0
            except Exception:
                total_nf = 0

            try:
                r = db.executar('SELECT COUNT(DISTINCT id) FROM itens').fetchone()
                total_itens = r[0] if r else 0
            except Exception:
                total_itens = 0

            try:
                r = db.executar('SELECT COALESCE(SUM(valor_total), 0) FROM "nota fiscal"').fetchone()
                valor_total = float(r[0]) if r else 0
            except Exception:
                valor_total = 0

            try:
                r = db.executar("SELECT COUNT(DISTINCT processo) FROM tccm").fetchone()
                total_tccm = r[0] if r else 0
            except Exception:
                total_tccm = 0

        self.stat_labels["Notas Fiscais"].configure(text=str(total_nf))
        self.stat_labels["Itens Recebidos"].configure(text=str(total_itens))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)
        self.stat_labels["Tccms Ativos"].configure(text=str(total_tccm))
