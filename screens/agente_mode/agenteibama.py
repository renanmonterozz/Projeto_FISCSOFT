import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase


class AgenteIbamaPage(CrudBase, ctk.CTkFrame):
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

        self.build_action_btn(btn_frame, "\U0001f50d  Pesquisar", None, self.pesquisar)
        self.build_action_btn(btn_frame, "\u2715  Limpar", None, self.limpar_filtros)
        self.build_action_btn(btn_frame, "+  Novo Infrator", None,
                              self.novo_agente, fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"], text_color="white",
                              border=False, bold=True)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))
        self.build_table_header(self.table_frame, ["Nome", "CPF", "Email", "Telefone"],
                                [3, 2, 2, 2], has_checkbox=True)

        self.agentes = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        db = Database()
        if db.conectar():
            resultados = db.executar(
                "SELECT id_infrator, nome_infrator, cpf, email, telefone_infrator FROM infrator"
            )
            agentes = []
            if resultados:
                for row in resultados.fetchall():
                    agentes.append({
                        "id": row[0],
                        "nome": row[1],
                        "cpf": row[2],
                        "email": row[3],
                        "telefone": row[4] or "-",
                    })
            db.desconectar()
            return agentes
        return []

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for agente in self.agentes:
            self.adicionar_linha(agente)

    def adicionar_linha(self, agente):
        linha, data, _ = self.add_data_row()
        self.configure_data_columns(data, [3, 2, 2, 2])

        ctk.CTkLabel(data, text=agente["nome"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w"
                      ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(data, text=agente["cpf"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text_muted"], anchor="w"
                      ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(data, text=agente["email"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text_muted"], anchor="w"
                      ).grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(data, text=agente["telefone"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w"
                      ).grid(row=0, column=3, sticky="w")

        self.add_action_buttons(linha, [
            ("\U0001f441", lambda u=agente: self.visualizar(u)),
            ("\u270f", lambda u=agente: self.editar(u)),
            ("\U0001f5d1", lambda u=agente: self.excluir(u)),
        ])

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        filtro_email = self.entry_filtro1.get().strip().lower()
        filtro_tel = self.entry_filtro2.get().strip().lower()

        todos = self.carregar_do_banco()
        self.agentes = [
            a for a in todos
            if (not busca or busca in a["nome"].lower()
                or busca in a["cpf"] or busca in a["email"].lower())
            and (not filtro_email or filtro_email in a["email"].lower())
            and (not filtro_tel or filtro_tel in a["telefone"])
        ]
        self.render_rows()

    def limpar_filtros(self):
        self.clear_entries(self.entry_busca, self.entry_filtro1, self.entry_filtro2)
        self.agentes = self.carregar_do_banco()
        self.render_rows()

    def novo_agente(self):
        from screens.agente_mode.cadastrar_agenteibama import CadastrarAgenteIbamaWindow
        janela = CadastrarAgenteIbamaWindow(self)
        self.wait_window(janela)
        self.agentes = self.carregar_do_banco()
        self.render_rows()

    def visualizar(self, agente):
        from screens.visualizar_agenteibama import VisualizarAgenteIbamaWindow
        janela = VisualizarAgenteIbamaWindow(self, agente)
        self.wait_window(janela)

    def editar(self, agente):
        from screens.agente_mode.cadastrar_agenteibama import CadastrarAgenteIbamaWindow
        janela = CadastrarAgenteIbamaWindow(self, agente=agente)
        self.wait_window(janela)
        self.agentes = self.carregar_do_banco()
        self.render_rows()

    def excluir(self, agente):
        if messagebox.askyesno("Excluir", f"Deseja excluir {agente['nome']}?"):
            db = Database()
            if db.conectar():
                db.executar(
                    "DELETE FROM infrator WHERE id_infrator = %s",
                    (agente["id"],)
                )
                db.commitar()
                db.desconectar()
            self.agentes = self.carregar_do_banco()
            self.render_rows()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Agentes IBAMA")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    AgenteIbamaPage(app).pack(fill="both", expand=True)
    app.mainloop()
