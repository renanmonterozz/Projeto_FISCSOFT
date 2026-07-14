import customtkinter as ctk
from config.styles import COLORS, FONTS


class VisualizarUsuarioWindow(ctk.CTkToplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario

        self.title("Visualizacao de Agente IBAMA")
        self.geometry("700+{}+{}".format(
            (self.winfo_screenwidth() - 700) // 2,
            (self.winfo_screenheight() - 620) // 2
        ))
        self.resizable(False, False)
        self.configure(fg_color=COLORS["white"])
        self.transient(master)
        self.grab_set()

        main_container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        top_bar = ctk.CTkFrame(main_container, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 0))

        ctk.CTkLabel(
            top_bar, text="Visualizacao de Agente IBAMA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            top_bar, text="Consulte os dados do agente",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        content = ctk.CTkFrame(
            main_container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        content.pack(fill="both", expand=True, padx=25, pady=(15, 20))

        self._build_dados_pessoais(content)
        self._build_dados_acesso(content)
        extras = [
            (self.usuario.get("data_cadastro"), "Data de cadastro"),
            (self.usuario.get("ultimo_acesso"), "Ultimo Acesso"),
            (self.usuario.get("cadastrado_por"), "Cadastrado por"),
            (self.usuario.get("atualizado_por"), "Atualizado por"),
        ]
        if any(v for v, _ in extras):
            self._build_informacoes_adicionais(content, extras)
        self._build_botao_editar(content)

    def _build_section_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

    def _build_field_row(self, parent, fields, pad_top=0):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(pad_top, 0))

        col_count = len(fields)
        for i, (label, value) in enumerate(fields):
            field_frame = ctk.CTkFrame(row, fg_color="transparent")
            field_frame.pack(side="left", fill="x", expand=True,
                             padx=(0, 15) if i < col_count - 1 else (0, 0))

            ctk.CTkLabel(
                field_frame, text=label,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            entry = ctk.CTkEntry(
                field_frame, height=34, corner_radius=4,
                border_width=1, border_color=COLORS["border"],
                fg_color="#F5F5F5", text_color=COLORS["text"],
                font=ctk.CTkFont(size=FONTS["size_body"]),
                state="normal"
            )
            entry.pack(fill="x", pady=(2, 0))
            entry.insert(0, value)
            entry.configure(state="disabled")

    def _build_dados_pessoais(self, parent):
        self._build_section_label(parent, "Dados Pessoais")
        self._build_field_row(parent, [
            ("Nome Completo", self.usuario.get("nome", "")),
            ("CPF", self.usuario.get("cpf", "")),
        ])
        self._build_field_row(parent, [
            ("E-mail", self.usuario.get("email", "")),
            ("Telefone", self.usuario.get("telefone", "")),
        ], pad_top=10)

    def _build_dados_acesso(self, parent):
        self._build_section_label(parent, "Dados de Acesso")
        self._build_field_row(parent, [
            ("Login", self.usuario.get("login", "")),
            ("Perfil", self.usuario.get("perfil", "")),
        ])

    def _build_informacoes_adicionais(self, parent, extras):
        self._build_section_label(parent, "Informacoes Adicionais")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(5, 0))

        for i, (valor, label) in enumerate(extras):
            if not valor:
                continue
            field_frame = ctk.CTkFrame(row, fg_color="transparent")
            field_frame.pack(side="left", fill="x", expand=True,
                             padx=(0, 10) if i < 3 else (0, 0))

            ctk.CTkLabel(
                field_frame, text=label,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            entry = ctk.CTkEntry(
                field_frame, height=34, corner_radius=4,
                border_width=1, border_color=COLORS["border"],
                fg_color="#F5F5F5", text_color=COLORS["text"],
                font=ctk.CTkFont(size=FONTS["size_body"]),
            )
            entry.pack(fill="x", pady=(2, 0))
            entry.insert(0, valor)
            entry.configure(state="disabled")

    def _build_botao_editar(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20))

        ctk.CTkButton(
            btn_frame,
            text="Editar Usuario",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self._on_editar
        ).pack(anchor="center")

    def _on_editar(self):
        self.destroy()
        if hasattr(self.master, "editar"):
            self.master.editar(self.usuario)
