import _path  # noqa: F401

import os

import customtkinter as ctk
from PIL import Image

from config.styles import ASSETS_DIR, COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


class DashboardExterno(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator

        self.build_header("Meu Painel", f"Bem-vindo, {usuario_logado or 'Usuario'}",
                          alerta_nota=False)
        self.build_stats_cards()
        # build_tccm_info removed
        self.build_notas_resumo()

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        card_data = [
            ("Meus TCCMs", "Processos ativos", "0"),
            ("Notas Fiscais", "Total enviadas", "0"),
            ("Valor Total(R$)", "Valor acumulado", "R$ 0,00"),
            ("Pendentes", "Aguardando analise", "0"),
        ]

        self.stat_labels = {}
        icons = ["nota.png", "caixa2.png", "cifrao.png", "icone_usuario.png"]

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

            icon_img = None
            try:
                icon_img = ctk.CTkImage(
                    light_image=Image.open(os.path.join(ASSETS_DIR, icons[i])),
                    dark_image=Image.open(os.path.join(ASSETS_DIR, icons[i])),
                    size=(32, 32),
                )
            except Exception:
                pass

            if icon_img:
                ctk.CTkLabel(
                    icon_circle, text="",
                    image=icon_img
                ).pack(expand=True)
            else:
                ctk.CTkLabel(
                    icon_circle, text=["\U0001f4cb", "\U0001f4e6", "\U0001f4b0", "\U0001f464"][i],
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

    # build_tccm_info removed — TCCM info panel not shown in external dashboard

    def build_notas_resumo(self):
        self.colunas_place = [
            (0.00, 0.25, "w"),      # Numero da NF
            (0.27, 0.15, "center"), # Data
            (0.44, 0.12, "center"), # Valor(R$)
            (0.58, 0.06, "center"), # Status
        ]

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
            header_frame, text="Ultimas Notas Fiscais",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        columns = ["Numero da NF", "Data", "Valor(R$)", "Status"]
        header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=40, corner_radius=0)
        header.pack(fill="x", padx=15, pady=(5, 0))
        header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(10, 17))

        for col, (relx, relwidth, anchor) in zip(columns, self.colunas_place):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor=anchor,
            ).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

        self.table_body = ctk.CTkScrollableFrame(
            section, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self._carregar_notas()

    def _carregar_tccm(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            sql = """SELECT processo, total_devido, total_pago, status
                     FROM tccm
                     WHERE `infrator_id_infrator` = %s
                     LIMIT 1"""
            try:
                resultado = db.executar(sql, (self.id_infrator,))
                row = resultado.fetchone() if resultado else None
                if row:
                    self.tccm_labels["processo"].configure(text=row['processo'] or "--")
                    valor_devido = float(row['total_devido']) if row['total_devido'] else 0
                    self.tccm_labels["total_devido"].configure(
                        text=f"R$ {valor_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    valor_pago = float(row['total_pago']) if row['total_pago'] else 0
                    self.tccm_labels["total_pago"].configure(
                        text=f"R$ {valor_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    self.tccm_labels["status"].configure(text=row['status'] or "--")
            except Exception:
                pass

    def _carregar_notas(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.id_infrator:
            ctk.CTkLabel(
                self.table_body, text="Nenhuma nota fiscal encontrada",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        with Database() as db:
            if not db.conexao:
                return

            sql = """SELECT nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota
                     FROM `nota fiscal` nf
                     JOIN tccm t ON nf.processo = t.processo
                     WHERE t.`infrator_id_infrator` = %s
                     GROUP BY nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota
                     ORDER BY nf.data DESC"""
            try:
                resultado = db.executar(sql, (self.id_infrator,))
                notas = []
                if resultado:
                    for row in resultado.fetchall():
                        raw_data = row['data']
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
                        notas.append({
                            "nota_fiscal": row['nota_fiscal'] or "--",
                            "data": data_fmt,
                            "valor_total": float(row['valor_total']) if row['valor_total'] else 0,
                            "status": row['status_nota'] or "Pendente",
                        })
            except Exception:
                notas = []

        if not notas:
            ctk.CTkLabel(
                self.table_body, text="Nenhuma nota fiscal encontrada",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        for nota in notas:
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=44)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            valor_formatado = f"R$ {nota['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            dados = [
                (nota["nota_fiscal"], COLORS["text"]),
                (nota["data"], COLORS["text_muted"]),
                (valor_formatado, COLORS["text_muted"]),
            ]

            for (relx, relwidth, anchor), (valor, cor) in zip(self.colunas_place[:3], dados):
                ctk.CTkLabel(
                    cols, text=valor,
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=cor, anchor=anchor,
                ).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

            if nota["status"] == "Aprovada":
                status_color = COLORS["success_dark"]
                status_text = "\u2714"
            elif nota["status"] == "Rejeitada":
                status_color = COLORS["danger"]
                status_text = "\u2718"
            elif nota["status"] == "Correcao Solicitada":
                status_color = "#D97706"
                status_text = "\u270F"
            else:
                status_color = COLORS["warning"]
                status_text = "\u26A0"

            ctk.CTkLabel(
                cols, text=status_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=status_color, anchor="center",
            ).place(relx=0.58, relwidth=0.06, rely=0, relheight=1)

    def _atualizar_cards(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            base = '''FROM `nota fiscal` nf
                      JOIN tccm t ON nf.processo = t.processo
                      WHERE t.`infrator_id_infrator` = %s'''

            try:
                r = db.executar(
                    'SELECT COUNT(*) FROM tccm WHERE `infrator_id_infrator` = %s',
                    (self.id_infrator,)
                ).fetchone()
                total_tccm = r['COUNT(*)'] if r else 0
            except Exception:
                total_tccm = 0

            try:
                r = db.executar(
                    f'SELECT COUNT(DISTINCT nf.nota_fiscal) {base}',
                    (self.id_infrator,)
                ).fetchone()
                total_nf = r['COUNT(DISTINCT nf.nota_fiscal)'] if r else 0
            except Exception:
                total_nf = 0

            try:
                r = db.executar(
                    f"""SELECT COALESCE(SUM(nf.valor_total), 0) {base}
                        AND nf.status_nota = 'Aprovada'""",
                    (self.id_infrator,)
                ).fetchone()
                valor_total = float(r['COALESCE(SUM(nf.valor_total), 0)']) if r else 0
            except Exception:
                valor_total = 0

            try:
                r = db.executar(
                    f"""SELECT COUNT(DISTINCT nf.nota_fiscal) {base}
                        AND nf.status_nota = 'Pendente'""",
                    (self.id_infrator,)
                ).fetchone()
                total_pendentes = r['COUNT(DISTINCT nf.nota_fiscal)'] if r else 0
            except Exception:
                total_pendentes = 0

        self.stat_labels["Meus TCCMs"].configure(text=str(total_tccm))
        self.stat_labels["Notas Fiscais"].configure(text=str(total_nf))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)
        self.stat_labels["Pendentes"].configure(text=str(total_pendentes))
