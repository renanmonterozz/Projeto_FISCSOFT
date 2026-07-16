import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


class DashboardExterno(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator

        self.build_header("Meu Painel", f"Bem-vindo, {usuario_logado or 'Usuario'}")
        self.build_stats_cards()
        self.build_tccm_info()
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
        icons = ["\U0001f4cb", "\U0001f4c4", "\U0001f4b0", "\u23F3"]

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

    def build_tccm_info(self):
        section = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="x", padx=30, pady=(0, 20))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        dot = ctk.CTkFrame(
            header_frame, fg_color=COLORS["primary"],
            width=12, height=12, corner_radius=6
        )
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="Informacoes do TCCM",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        info_frame = ctk.CTkFrame(section, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.tccm_labels = {}
        campos = [
            ("Processo:", "processo"),
            ("Total Devido:", "total_devido"),
            ("Total Pago:", "total_pago"),
            ("Status:", "status"),
        ]

        for i, (campo_texto, key) in enumerate(campos):
            row = i // 2
            col = i % 2

            campo_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            campo_frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            info_frame.columnconfigure(col, weight=1)

            ctk.CTkLabel(
                campo_frame, text=campo_texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(side="left")

            lbl = ctk.CTkLabel(
                campo_frame, text="--",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text"]
            )
            lbl.pack(side="left", padx=(5, 0))
            self.tccm_labels[key] = lbl

        self._carregar_tccm()

    def build_notas_resumo(self):
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
        weights = [3, 2, 2, 1]

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

        self._carregar_notas()

    def _carregar_tccm(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            sql = """SELECT processo, total_devido, total_pago, status
                     FROM tccm
                     WHERE "infrator_id_infrator" = ?
                     LIMIT 1"""
            try:
                resultado = db.executar(sql, (self.id_infrator,))
                row = resultado.fetchone() if resultado else None
                if row:
                    self.tccm_labels["processo"].configure(text=row[0] or "--")
                    valor_devido = float(row[1]) if row[1] else 0
                    self.tccm_labels["total_devido"].configure(
                        text=f"R$ {valor_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    valor_pago = float(row[2]) if row[2] else 0
                    self.tccm_labels["total_pago"].configure(
                        text=f"R$ {valor_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                    self.tccm_labels["status"].configure(text=row[3] or "--")
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
                     FROM "nota fiscal" nf
                     JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                     WHERE t."infrator_id_infrator" = ?
                     ORDER BY nf.data DESC"""
            try:
                resultado = db.executar(sql, (self.id_infrator,))
                notas = []
                if resultado:
                    for row in resultado.fetchall():
                        notas.append({
                            "nota_fiscal": row[0] or "--",
                            "data": row[1].strftime("%d/%m/%Y") if row[1] else "--",
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
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

        weights = [3, 2, 2, 1]
        for nota in notas:
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=44)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            valor_formatado = f"R$ {nota['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            dados = [nota["nota_fiscal"], nota["data"], valor_formatado]

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

            ctk.CTkLabel(
                status_frame, text=status_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=status_color
            ).pack(expand=True)

    def _atualizar_cards(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            try:
                r = db.executar(
                    'SELECT COUNT(*) FROM tccm WHERE "infrator_id_infrator" = ?',
                    (self.id_infrator,)
                ).fetchone()
                total_tccm = r[0] if r else 0
            except Exception:
                total_tccm = 0

            try:
                r = db.executar(
                    '''SELECT COUNT(*) FROM "nota fiscal" nf
                       JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                       WHERE t."infrator_id_infrator" = ?''',
                    (self.id_infrator,)
                ).fetchone()
                total_nf = r[0] if r else 0
            except Exception:
                total_nf = 0

            try:
                r = db.executar(
                    '''SELECT COALESCE(SUM(nf.valor_total), 0) FROM "nota fiscal" nf
                       JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                       WHERE t."infrator_id_infrator" = ?''',
                    (self.id_infrator,)
                ).fetchone()
                valor_total = float(r[0]) if r else 0
            except Exception:
                valor_total = 0

            try:
                r = db.executar(
                    '''SELECT COUNT(*) FROM "nota fiscal" nf
                       JOIN tccm t ON t."agente ibama_matricula" = nf."agente ibama_matricula"
                       WHERE t."infrator_id_infrator" = ? AND nf.status_nota = 'Pendente' ''',
                    (self.id_infrator,)
                ).fetchone()
                total_pendentes = r[0] if r else 0
            except Exception:
                total_pendentes = 0

        self.stat_labels["Meus TCCMs"].configure(text=str(total_tccm))
        self.stat_labels["Notas Fiscais"].configure(text=str(total_nf))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)
        self.stat_labels["Pendentes"].configure(text=str(total_pendentes))
