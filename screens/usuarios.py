import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from utils import registrar_log


class UsuariosPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado

        self.build_header("Agentes IBAMA", "Gerencie os agentes cadastrados no sistema")
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(row, "Buscar por nome, usuario ou matricula...", 340)
        self.entry_filtro1 = self.build_filter_entry(row, "Email")
        self.entry_filtro2 = self.build_filter_entry(row, "Perfil / Status")

        btn_frame = self.build_btn_frame(row)

        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        self.build_action_btn(btn_frame, "  Novo Usuario", carregar_icone("mais.png"),
                              self.novo_usuario, fg_color=COLORS["primary"],
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

        colunas = ["Usuario", "Email", "Perfil", "Status"]
        col_cfg = [
            (0.0, 0.40, "w"),    # Usuario
            (0.40, 0.30, "w"),   # Email
            (0.70, 0.15, "center"),  # Perfil
            (0.85, 0.15, "center"),  # Status
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

        self.usuarios = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        with Database() as db:
            if not db.conexao:
                return []
            sql = """SELECT matricula, nome_agente, cpf, email, telefone, login, perfil, status
                     FROM "agente ibama" """
            resultados = db.executar(sql)
            usuarios = []
            if resultados:
                for row in resultados.fetchall():
                    usuarios.append({
                        "matricula": row[0],
                        "nome": row[1],
                        "cpf": row[2],
                        "email": row[3],
                        "telefone": row[4],
                        "login": row[5],
                        "perfil": row[6].capitalize() if row[6] else "Agente",
                        "status": "Ativo" if row[7] == "ativo" else "Inativo",
                    })
            return usuarios

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for usuario in self.usuarios:
            self.adicionar_linha(usuario)

    def adicionar_linha(self, usuario):
        linha, data, _ = self.add_data_row(has_checkbox=False)

        # pesos → relx / relwidth (idêntico ao cabeçalho)
        col_cfg = [
            (0.0,  0.40, "w"),      # Usuario
            (0.40, 0.30, "w"),      # Email
            (0.70, 0.15, "center"), # Perfil
            (0.85, 0.15, "center"), # Status
        ]

        valores = [
            usuario["nome"],
            usuario["email"],
            usuario["perfil"],
            usuario["status"],
        ]

        for (rx, rw, anchor), texto in zip(col_cfg, valores):
            ctk.CTkLabel(
                data, text=texto,
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text"] if anchor == "w" else COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        self.add_action_buttons(linha, [
            ("\U0001f441", lambda u=usuario: self.visualizar(u)),
            ("\u270f", lambda u=usuario: self.editar(u)),
            ("\U0001f5d1", lambda u=usuario: self.excluir(u)),
        ])

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        filtro_email = self.entry_filtro1.get().strip().lower()
        filtro_perfil = self.entry_filtro2.get().strip().lower()

        todos = self.carregar_do_banco()
        self.usuarios = [
            u for u in todos
            if (not busca or busca in u["nome"].lower()
                or busca in u["login"].lower()
                or busca in str(u["matricula"]))
            and (not filtro_email or filtro_email in u["email"].lower())
            and (not filtro_perfil or filtro_perfil in u["perfil"].lower()
                 or filtro_perfil in u["status"].lower())
        ]
        self.render_rows()

    def limpar_filtros(self):
        self.clear_entries(self.entry_busca, self.entry_filtro1, self.entry_filtro2)
        self.usuarios = self.carregar_do_banco()
        self.render_rows()

    def novo_usuario(self):
        from screens.cadastrar_usuario import CadastrarUsuarioWindow
        janela = CadastrarUsuarioWindow(self, usuario_logado=self.usuario_logado)
        self.wait_window(janela)
        self.usuarios = self.carregar_do_banco()
        self.render_rows()

    def visualizar(self, usuario):
        from screens.visualizar_usuario import VisualizarUsuarioWindow
        janela = VisualizarUsuarioWindow(self, usuario)
        self.wait_window(janela)

    def editar(self, usuario):
        from screens.cadastrar_usuario import CadastrarUsuarioWindow
        janela = CadastrarUsuarioWindow(self, usuario=usuario, usuario_logado=self.usuario_logado)
        self.wait_window(janela)
        self.usuarios = self.carregar_do_banco()
        self.render_rows()

    def excluir(self, usuario):
        if messagebox.askyesno("Excluir", f"Deseja excluir {usuario['nome']}?"):
            with Database() as db:
                if db.conexao:
                    db.executar(
                        "DELETE FROM \"agente ibama\" WHERE matricula = ?",
                        (usuario["matricula"],)
                    )
                    db.commitar()
            registrar_log(
                self.usuario_logado or "Sistema",
                "exclusao",
                "agente ibama",
                f"Usuario '{usuario['nome']}' (matricula: {usuario['matricula']}) excluido"
            )
            self.usuarios = self.carregar_do_banco()
            self.render_rows()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Usuarios")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    UsuariosPage(app).pack(fill="both", expand=True)
    app.mainloop()
