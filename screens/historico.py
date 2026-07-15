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
        self.build_table_header(
            self.table_frame,
            ["Data/Hora", "Usuario", "Acao", "Tabela", "Descricao"],
            [1, 1, 1, 1, 3],
            has_checkbox=False
        )

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

        data.grid_columnconfigure(0, weight=1)
        data.grid_columnconfigure(1, weight=1)
        data.grid_columnconfigure(2, weight=1)
        data.grid_columnconfigure(3, weight=1)
        data.grid_columnconfigure(4, weight=3)

        data_hora_str = log["data_hora"].strftime("%d/%m/%Y %H:%M") if log["data_hora"] else "--"

        ctk.CTkLabel(
            data, text=data_hora_str,
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text"], anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(10, 5))

        ctk.CTkLabel(
            data, text=log["usuario"],
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"], anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=5)

        acao_cor = COLORS.get("primary", "#1D4D21")
        if log["acao"] == "exclusao":
            acao_cor = COLORS.get("danger", "#D32F2F")
        elif log["acao"] == "edicao":
            acao_cor = COLORS.get("warning", "#F57C00")

        ctk.CTkLabel(
            data, text=log["acao"].capitalize(),
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=acao_cor, anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=log["tabela"],
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"], anchor="w",
        ).grid(row=0, column=3, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=log["descricao"][:80] + ("..." if len(log["descricao"]) > 80 else ""),
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"], anchor="w",
        ).grid(row=0, column=4, sticky="w", padx=(5, 10))

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
