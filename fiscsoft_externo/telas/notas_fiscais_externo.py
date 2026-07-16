import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


class NotasFiscaisExterno(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator

        self.build_header("Notas Fiscais",
                          "Visualize suas notas fiscais enviadas ao sistema")
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_periodo = self.build_filter_entry(row, "Periodo (mm/aaaa)", 160)
        self.entry_status = self.build_filter_entry(row, "Status", 160)
        self.entry_nf = self.build_filter_entry(row, "Numero da NF", 200)

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(btn_frame, "  Filtrar", None, self.filtrar,
                              fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                              text_color="white", border=False, bold=True)
        self.build_action_btn(btn_frame, "  Limpar", None, self.limpar_filtros)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))

        columns = [
            "Numero da NF", "Chave de Acesso", "Data de Emissao",
            "Valor Total(R$)", "Status"
        ]
        weights = [2, 3, 2, 2, 1]

        header = ctk.CTkFrame(self.table_frame, fg_color=COLORS["table_header"],
                              height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(15, 0))

        for i, w in enumerate(weights):
            cols_frame.grid_columnconfigure(i, weight=w)

        for i, col in enumerate(columns):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=i, sticky="w", padx=5)

        self.table_body = ctk.CTkScrollableFrame(
            self.table_frame, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.notas = self._carregar_notas()
        self._render_rows()

    def _carregar_notas(self):
        if not self.id_infrator:
            return []

        with Database() as db:
            if not db.conexao:
                return []

            sql = """SELECT nf.nota_fiscal, nf.chave_de_acesso, nf.data,
                            nf.valor_total, nf.status_nota
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
                            "chave_de_acesso": row[1] or "--",
                            "data": row[2].strftime("%d/%m/%Y") if row[2] else "--",
                            "valor_total": float(row[3]) if row[3] else 0,
                            "status": row[4] or "Pendente",
                        })
                return notas
            except Exception:
                return []

    def _render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.notas:
            ctk.CTkLabel(
                self.table_body, text="Nenhuma nota fiscal encontrada",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        weights = [2, 3, 2, 2, 1]
        for nota in self.notas:
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)

            valor_formatado = f"R$ {nota['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            dados = [nota["nota_fiscal"], nota["chave_de_acesso"], nota["data"], valor_formatado]

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
                status_text = "\u2714 Aprovada"
            elif nota["status"] == "Rejeitada":
                status_color = COLORS["danger"]
                status_text = "\u2718 Rejeitada"
            else:
                status_color = COLORS["warning"]
                status_text = "\u26A0 Pendente"

            ctk.CTkLabel(
                status_frame, text=status_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=status_color
            ).pack(expand=True)

    def filtrar(self):
        periodo = self.entry_periodo.get().strip().lower()
        status = self.entry_status.get().strip().lower()
        nf = self.entry_nf.get().strip().lower()

        todos = self._carregar_notas()
        self.notas = [
            n for n in todos
            if (not nf or nf in n["nota_fiscal"].lower())
            and (not status or status in n["status"].lower())
            and (not periodo or periodo in n["data"])
        ]
        self._render_rows()

    def limpar_filtros(self):
        self.clear_entries(self.entry_periodo, self.entry_status, self.entry_nf)
        self.notas = self._carregar_notas()
        self._render_rows()
