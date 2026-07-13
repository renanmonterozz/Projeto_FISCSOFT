import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from config.styles import COLORS, FONTS, ASSETS_DIR
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone


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

        self.entry_busca = ctk.CTkEntry(
            busca_container,
            placeholder_text="Buscar por nome, usuario ou matricula...",
            width=340, height=38,
            border_width=0, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_busca.pack(side="left", padx=(12, 4), pady=2)

        try:
            lupa_busca_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                size=(18, 18),
            )
        except Exception:
            lupa_busca_icon = None

        ctk.CTkLabel(
            busca_container, image=lupa_busca_icon, text="",
        ).pack(side="right", padx=(0, 10))

        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        self.build_action_btn(btn_frame, "  Novo Usuario", carregar_icone("mais.png"),
                              self.novo_usuario, fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"], text_color="white",
                              border=False, bold=True)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))
        self.build_table_header(self.table_frame, ["Usuario", "Email", "Perfil", "Status"],
                                [3, 2, 1, 1], has_checkbox=True)

        self.usuarios = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        db = Database()
        if db.conectar():
            sql = """SELECT matricula, nome_agente, cpf, email, telefone, login, senha, perfil, status
                     FROM `agente ibama`"""
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
                        "senha": row[6],
                        "perfil": row[7].capitalize(),
                        "status": "Ativo" if row[8] == "ativo" else "Inativo",
                    })
            db.desconectar()
            return usuarios
        return []

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for usuario in self.usuarios:
            self.adicionar_linha(usuario)

    def adicionar_linha(self, usuario):
        linha, data, _ = self.add_data_row()
        self.configure_data_columns(data, [3, 2, 1, 1])

        ctk.CTkLabel(data, text=usuario["nome"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w"
                      ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(data, text=usuario["email"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text_muted"], anchor="w"
                      ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(data, text=usuario["perfil"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w"
                      ).grid(row=0, column=2, sticky="w")

        status_container = ctk.CTkFrame(data, fg_color="transparent")
        status_container.grid(row=0, column=3, sticky="w")

        cor = COLORS["primary"] if usuario["status"] == "Ativo" else COLORS["danger"]
        bolinha = ctk.CTkFrame(status_container, fg_color=cor,
                                width=8, height=8, corner_radius=4)
        bolinha.pack(side="left", padx=(0, 6))
        bolinha.pack_propagate(False)
        ctk.CTkLabel(status_container, text=usuario["status"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"]
                      ).pack(side="left")

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
            db = Database()
            if db.conectar():
                db.executar(
                    "DELETE FROM `agente ibama` WHERE nome_agente = %s",
                    (usuario["nome"],)
                )
                db.commitar()
                db.desconectar()
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
