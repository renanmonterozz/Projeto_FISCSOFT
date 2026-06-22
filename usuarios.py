import customtkinter as ctk
from tkinter import messagebox


class UsuariosPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#F5F5F5")

        self.build_header()
        self.build_filter_bar()
        self.build_table()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header,
            text="Usuários",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#111111",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Gerencie os usuários cadastrados no sistema",
            font=ctk.CTkFont(size=13),
            text_color="#666666",
        ).pack(anchor="w", pady=(4, 0))

    def build_filter_bar(self):
        container = ctk.CTkFrame(
            self, fg_color="white", corner_radius=8,
            border_width=1, border_color="#D9D9D9"
        )
        container.pack(fill="x", padx=30, pady=(0, 20))

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        # --- Busca geral com lupa ---
        busca_container = ctk.CTkFrame(
            row, fg_color="white", border_width=1,
            border_color="#D9D9D9", corner_radius=6
        )
        busca_container.pack(side="left", padx=(0, 10))

        self.entry_busca = ctk.CTkEntry(
            busca_container,
            placeholder_text="Buscar por nome, usuário ou matrícula...",
            width=340, height=38,
            border_width=0, fg_color="white",
            text_color="#111111", placeholder_text_color="#999999",
        )
        self.entry_busca.pack(side="left", padx=(12, 4), pady=2)
        ctk.CTkLabel(
            busca_container, text="🔍",
            font=ctk.CTkFont(size=14), text_color="#999999"
        ).pack(side="right", padx=(0, 10))

        # --- Filtro 1 ---
        self.entry_filtro1 = ctk.CTkEntry(
            row,
            placeholder_text="Email",
            width=200, height=38,
            border_width=1, border_color="#D9D9D9",
            corner_radius=6, fg_color="white",
            text_color="#111111", placeholder_text_color="#999999",
        )
        self.entry_filtro1.pack(side="left", padx=(0, 10))

        # --- Filtro 2 ---
        self.entry_filtro2 = ctk.CTkEntry(
            row,
            placeholder_text="Perfil / Status",
            width=200, height=38,
            border_width=1, border_color="#D9D9D9",
            corner_radius=6, fg_color="white",
            text_color="#111111", placeholder_text_color="#999999",
        )
        self.entry_filtro2.pack(side="left", padx=(0, 10))

        # --- Botões ---
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            btn_frame,
            text="🔍  Pesquisar",
            height=38, corner_radius=6,
            fg_color="white", hover_color="#F0F0F0",
            text_color="#111111",
            border_width=1, border_color="#D9D9D9",
            font=ctk.CTkFont(size=13),
            command=self.pesquisar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="✕  Limpar",
            height=38, corner_radius=6,
            fg_color="white", hover_color="#F0F0F0",
            text_color="#111111",
            border_width=1, border_color="#D9D9D9",
            font=ctk.CTkFont(size=13),
            command=self.limpar_filtros,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="+  Novo Usuário",
            height=38, corner_radius=6,
            fg_color="#16A34A", hover_color="#15803D",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.novo_usuario,
        ).pack(side="left")

    def build_table(self):
        self.table_frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=15,
            border_width=1, border_color="#D9D9D9"
        )
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # --- Header da tabela ---
        header = ctk.CTkFrame(
            self.table_frame, fg_color="#FAFAFA",
            height=44, corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="", width=40).pack(side="left", padx=(15, 0))

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(5, 20))
        cols.grid_columnconfigure(0, weight=3)
        cols.grid_columnconfigure(1, weight=2)
        cols.grid_columnconfigure(2, weight=1)
        cols.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            cols, text="Usuário",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666"
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            cols, text="Email",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666"
        ).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(
            cols, text="Perfil",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666"
        ).grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(
            cols, text="Status",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666"
        ).grid(row=0, column=3, sticky="w")

        ctk.CTkLabel(
            header, text="Ações",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666",
            width=120
        ).pack(side="right", padx=(0, 15))

        # --- Corpo da tabela (scrollável) ---
        self.table_body = ctk.CTkScrollableFrame(
            self.table_frame, fg_color="white", corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.usuarios = [
            {"nome": "João Silva", "email": "joao.silva@empresa.com",
             "perfil": "Administrador", "status": "Ativo"},
            {"nome": "Maria Souza", "email": "maria.souza@empresa.com",
             "perfil": "Usuário", "status": "Ativo"},
            {"nome": "Carlos Pereira", "email": "carlos.pereira@empresa.com",
             "perfil": "Usuário", "status": "Inativo"},
            {"nome": "Ana Oliveira", "email": "ana.oliveira@empresa.com",
             "perfil": "Supervisor", "status": "Ativo"},
            {"nome": "Pedro Santos", "email": "pedro.santos@empresa.com",
             "perfil": "Usuário", "status": "Ativo"},
            {"nome": "Luciana Costa", "email": "luciana.costa@empresa.com",
             "perfil": "Administrador", "status": "Inativo"},
        ]
        self.carregar_usuarios()

    def carregar_usuarios(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for usuario in self.usuarios:
            self.adicionar_linha(usuario)

    def adicionar_linha(self, usuario):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(
            self.table_body, fg_color="#F0F0F0", height=1
        ).pack(fill="x")

        cb = ctk.CTkCheckBox(
            linha, text="", width=20, height=20,
            border_width=2, corner_radius=4
        )
        cb.pack(side="left", padx=(17, 0))

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(10, 0))
        data.grid_columnconfigure(0, weight=3)
        data.grid_columnconfigure(1, weight=2)
        data.grid_columnconfigure(2, weight=1)
        data.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            data, text=usuario["nome"],
            font=ctk.CTkFont(size=13), text_color="#111111", anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            data, text=usuario["email"],
            font=ctk.CTkFont(size=13), text_color="#666666", anchor="w"
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            data, text=usuario["perfil"],
            font=ctk.CTkFont(size=13), text_color="#111111", anchor="w"
        ).grid(row=0, column=2, sticky="w")

        status_container = ctk.CTkFrame(data, fg_color="transparent")
        status_container.grid(row=0, column=3, sticky="w")

        cor = "#16A34A" if usuario["status"] == "Ativo" else "#DC2626"
        bolinha = ctk.CTkFrame(
            status_container, fg_color=cor,
            width=8, height=8, corner_radius=4
        )
        bolinha.pack(side="left", padx=(0, 6))
        bolinha.pack_propagate(False)
        ctk.CTkLabel(
            status_container, text=usuario["status"],
            font=ctk.CTkFont(size=13), text_color="#111111"
        ).pack(side="left")

        actions = ctk.CTkFrame(linha, fg_color="transparent")
        actions.pack(side="right", padx=(0, 10))

        botoes_acoes = [
            ("👁", lambda u=usuario: self.visualizar(u)),
            ("✏", lambda u=usuario: self.editar(u)),
            ("🗑", lambda u=usuario: self.excluir(u)),
        ]
        for icon, cmd in botoes_acoes:
            ctk.CTkButton(
                actions,
                text=icon, width=32, height=32,
                corner_radius=6, fg_color="white",
                hover_color="#F0F0F0", text_color="#111111",
                border_width=1, border_color="#D9D9D9",
                font=ctk.CTkFont(size=14),
                command=cmd,
            ).pack(side="left", padx=2)

    # ── Ações ──────────────────────────────────────────

    def pesquisar(self):
        messagebox.showinfo(
            "Pesquisar",
            "Funcionalidade de pesquisa será implementada."
        )

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.entry_filtro1.delete(0, "end")
        self.entry_filtro2.delete(0, "end")

    def novo_usuario(self):
        messagebox.showinfo(
            "Novo Usuário",
            "Funcionalidade de cadastro será implementada."
        )

    def visualizar(self, usuario):
        messagebox.showinfo(
            "Visualizar", f"Visualizando: {usuario['nome']}"
        )

    def editar(self, usuario):
        messagebox.showinfo(
            "Editar", f"Editando: {usuario['nome']}"
        )

    def excluir(self, usuario):
        if messagebox.askyesno(
            "Excluir", f"Deseja excluir {usuario['nome']}?"
        ):
            self.usuarios.remove(usuario)
            self.carregar_usuarios()


if __name__ == "__main__":
    from tela_lateral import Sidebar

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Usuários")
    app.geometry("1200x700")
    app.configure(fg_color="#F5F5F5")

    sidebar = Sidebar(app, width=210)
    sidebar.pack(side="left", fill="y")

    UsuariosPage(app).pack(side="right", fill="both", expand=True)
    app.mainloop()
