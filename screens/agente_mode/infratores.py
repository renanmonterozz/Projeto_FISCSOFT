import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from utils import registrar_log


class InfratoresPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])

        self.build_header("Infratores", "Gerencie os infratores cadastrados no sistema")
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(row, "Buscar por nome, CPF ou email...", 340)
        self.entry_filtro1 = self.build_filter_entry(row, "Email")
        self.entry_filtro2 = self.build_filter_entry(row, "Telefone")

        btn_frame = self.build_btn_frame(row)

        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        self.build_action_btn(btn_frame, "  Novo Infrator", carregar_icone("mais.png"),
                              self.novo_infrator, fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"], text_color="white",
                              border=False, bold=True)

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

        colunas = ["Nome", "CPF", "Email", "Telefone"]
        col_cfg = [
            (0.0, 0.35, "w"),    # Nome
            (0.35, 0.20, "w"),   # CPF
            (0.55, 0.25, "w"),   # Email
            (0.80, 0.20, "w"),   # Telefone
        ]

        for texto, (rx, rw, anchor) in zip(colunas, col_cfg):
            ctk.CTkLabel(
                cols, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        ctk.CTkLabel(
            header, text="Ações",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"], width=120,
        ).pack(side="right", padx=(0, 15))

        self.table_body = ctk.CTkScrollableFrame(
            self.table_container, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.infratores = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        with Database() as db:
            if not db.conexao:
                return []
            resultados = db.executar(
                "SELECT id_infrator, nome_infrator, cpf, email, telefone_infrator FROM infrator"
            )
            infratores = []
            if resultados:
                for row in resultados.fetchall():
                    infratores.append({
                        "id": row[0],
                        "nome": row[1],
                        "cpf": row[2],
                        "email": row[3],
                        "telefone": row[4] or "-",
                    })
            return infratores

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for infrator in self.infratores:
            self.adicionar_linha(infrator)

    def adicionar_linha(self, infrator):
        linha, data, _ = self.add_data_row(has_checkbox=False)

        # pesos → relx / relwidth (idêntico ao cabeçalho)
        col_cfg = [
            (0.0,  0.35, "w"),      # Nome
            (0.35, 0.20, "w"),      # CPF
            (0.55, 0.25, "w"),      # Email
            (0.80, 0.20, "w"),      # Telefone
        ]

        valores = [
            infrator["nome"],
            infrator["cpf"],
            infrator["email"],
            infrator["telefone"],
        ]

        for (rx, rw, anchor), texto in zip(col_cfg, valores):
            ctk.CTkLabel(
                data, text=texto,
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text"] if anchor == "w" else COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        self.add_action_buttons(linha, [
            ("\U0001f441", lambda i=infrator: self.visualizar(i)),
            ("\u270f", lambda i=infrator: self.editar(i)),
            ("\U0001f5d1", lambda i=infrator: self.excluir(i)),
        ])

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        filtro_email = self.entry_filtro1.get().strip().lower()
        filtro_tel = self.entry_filtro2.get().strip().lower()

        todos = self.carregar_do_banco()
        self.infratores = [
            i for i in todos
            if (not busca or busca in i["nome"].lower()
                or busca in i["cpf"] or busca in i["email"].lower())
            and (not filtro_email or filtro_email in i["email"].lower())
            and (not filtro_tel or filtro_tel in i["telefone"])
        ]
        self.render_rows()

    def limpar_filtros(self):
        self.clear_entries(self.entry_busca, self.entry_filtro1, self.entry_filtro2)
        self.infratores = self.carregar_do_banco()
        self.render_rows()

    def novo_infrator(self):
        from screens.agente_mode.cadastrar_infrator import CadastrarInfratorWindow
        janela = CadastrarInfratorWindow(self)
        self.wait_window(janela)
        self.infratores = self.carregar_do_banco()
        self.render_rows()

    def visualizar(self, infrator):
        from screens.visualizar_infrator import VisualizarInfratorWindow
        janela = VisualizarInfratorWindow(self, infrator)
        self.wait_window(janela)

    def editar(self, infrator):
        from screens.agente_mode.cadastrar_infrator import CadastrarInfratorWindow
        janela = CadastrarInfratorWindow(self, infrator=infrator)
        self.wait_window(janela)
        self.infratores = self.carregar_do_banco()
        self.render_rows()

    def excluir(self, infrator):
        if messagebox.askyesno("Excluir", f"Deseja excluir {infrator['nome']}?"):
            with Database() as db:
                if db.conexao:
                    db.executar(
                        "DELETE FROM infrator WHERE id_infrator = ?",
                        (infrator["id"],)
                    )
                    db.commitar()
            registrar_log(
                "Sistema",
                "exclusao",
                "infrator",
                f"Infrator '{infrator['nome']}' (ID: {infrator['id']}) excluido"
            )
            self.infratores = self.carregar_do_banco()
            self.render_rows()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Infratores")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    InfratoresPage(app).pack(fill="both", expand=True)
    app.mainloop()
