import _path  # noqa: F401

import customtkinter as ctk
from datetime import datetime

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone


class HistoricoPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.logs = []

        self.build_header("Historico de Atividades", "Registros de todas as alteracoes realizadas no sistema")
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(row, "Buscar por usuario, acao ou descricao...", 400)

        btn_frame = self.build_btn_frame(row)

        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))

        # Container interno com borda
        self.table_container = ctk.CTkFrame(
            self.table_frame, fg_color="transparent",
            border_width=1, border_color="#999999", corner_radius=4
        )
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- cabeçalho com PLACE ---
        header = ctk.CTkFrame(self.table_container, fg_color=COLORS["table_header"],
                              height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

        colunas = ["Data/Hora", "Usuario", "Acao", "Tabela", "Descricao"]
        col_cfg = [
            (0.0, 0.20, "w"),    # Data/Hora
            (0.20, 0.15, "w"),   # Usuario
            (0.35, 0.15, "w"),   # Acao
            (0.50, 0.15, "w"),   # Tabela
            (0.65, 0.35, "w"),   # Descricao
        ]

        for texto, (rx, rw, anchor) in zip(colunas, col_cfg):
            ctk.CTkLabel(
                cols, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        self.table_body = ctk.CTkScrollableFrame(
            self.table_container, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.logs = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        with Database() as db:
            if not db.conexao:
                return []
            sql = """SELECT id, usuario, acao, tabela, descricao, criado_em
                     FROM logs ORDER BY criado_em DESC"""
            resultados = db.executar(sql)
            logs = []
            if resultados:
                for row in resultados.fetchall():
                    criado_em = row[5]
                    if isinstance(criado_em, str):
                        try:
                            criado_em = datetime.strptime(criado_em, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            criado_em = None

                    logs.append({
                        "id": row[0],
                        "usuario": row[1],
                        "acao": row[2],
                        "tabela": row[3],
                        "descricao": row[4],
                        "data_hora": criado_em,
                    })
            return logs

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.logs:
            ctk.CTkLabel(
                self.table_body,
                text="Nenhum registro encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"],
            ).pack(pady=40)
            return

        for log in self.logs:
            self._add_row(log)

    def _add_row(self, log):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # pesos → relx / relwidth (idêntico ao cabeçalho)
        col_cfg = [
            (0.0,  0.20, "w"),      # Data/Hora
            (0.20, 0.15, "w"),      # Usuario
            (0.35, 0.15, "w"),      # Acao
            (0.50, 0.15, "w"),      # Tabela
            (0.65, 0.35, "w"),      # Descricao
        ]

        data_hora_str = log["data_hora"].strftime("%d/%m/%Y %H:%M") if log["data_hora"] else "--"

        acao_cor = COLORS.get("primary", "#1D4D21")
        if log["acao"] == "exclusao":
            acao_cor = COLORS.get("danger", "#D32F2F")
        elif log["acao"] == "edicao":
            acao_cor = COLORS.get("warning", "#F57C00")

        descricao = log["descricao"][:80] + ("..." if len(log["descricao"]) > 80 else "")

        dados = [
            (data_hora_str, COLORS["text"]),
            (log["usuario"], COLORS["text_muted"]),
            (log["acao"].capitalize(), acao_cor),
            (log["tabela"], COLORS["text_muted"]),
            (descricao, COLORS["text_muted"]),
        ]

        for (rx, rw, anchor), (texto, cor) in zip(col_cfg, dados):
            ctk.CTkLabel(
                data, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=cor, anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

    def pesquisar(self):
        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self.logs = self.carregar_do_banco()
        else:
            self.logs = [
                l for l in self.carregar_do_banco()
                if termo in l["usuario"].lower()
                or termo in l["acao"].lower()
                or termo in l["tabela"].lower()
                or termo in l["descricao"].lower()
            ]
        self.render_rows()

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.logs = self.carregar_do_banco()
        self.render_rows()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Historico")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    HistoricoPage(app).pack(fill="both", expand=True)
    app.mainloop()
