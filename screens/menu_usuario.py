import customtkinter as ctk
from config.styles import COLORS, FONTS
from conexaodb import Database


class MenuUsuarioPage(ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado

        self.build_header()
        self.build_summary_cards()
        self.build_table()
        self.carregar_dados()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            header,
            text="Menu do Usuario",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Visualize suas informacoes e acesse os modulos do sistema",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def build_summary_cards(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=(10, 20))

        ctk.CTkLabel(
            container,
            text="Resumo periodo",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 10))

        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Card 1: Notas Fiscais
        card1 = ctk.CTkFrame(cards_frame, fg_color=COLORS["white"], corner_radius=8,
                             border_width=1, border_color=COLORS["border"])
        card1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        icon_frame1 = ctk.CTkFrame(card1, fg_color="#E8F5E9", corner_radius=20, width=50, height=50)
        icon_frame1.pack(pady=(15, 8))
        icon_frame1.pack_propagate(False)
        ctk.CTkLabel(icon_frame1, text="NF", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["primary"]).pack(expand=True)

        self.notas_fiscais_label = ctk.CTkLabel(
            card1, text="0",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"]
        )
        self.notas_fiscais_label.pack()

        ctk.CTkLabel(
            card1, text="Total de notas",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 15))

        # Card 2: Itens Recebidos
        card2 = ctk.CTkFrame(cards_frame, fg_color=COLORS["white"], corner_radius=8,
                             border_width=1, border_color=COLORS["border"])
        card2.grid(row=0, column=1, padx=5, sticky="nsew")

        icon_frame2 = ctk.CTkFrame(card2, fg_color="#E8F5E9", corner_radius=20, width=50, height=50)
        icon_frame2.pack(pady=(15, 8))
        icon_frame2.pack_propagate(False)
        ctk.CTkLabel(icon_frame2, text="IT", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["primary"]).pack(expand=True)

        self.itens_recebidos_label = ctk.CTkLabel(
            card2, text="0",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"]
        )
        self.itens_recebidos_label.pack()

        ctk.CTkLabel(
            card2, text="Total de itens",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 15))

        # Card 3: Valor Total
        card3 = ctk.CTkFrame(cards_frame, fg_color=COLORS["white"], corner_radius=8,
                             border_width=1, border_color=COLORS["border"])
        card3.grid(row=0, column=2, padx=5, sticky="nsew")

        icon_frame3 = ctk.CTkFrame(card3, fg_color="#E8F5E9", corner_radius=20, width=50, height=50)
        icon_frame3.pack(pady=(15, 8))
        icon_frame3.pack_propagate(False)
        ctk.CTkLabel(icon_frame3, text="R$", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["primary"]).pack(expand=True)

        self.valor_total_label = ctk.CTkLabel(
            card3, text="R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"]
        )
        self.valor_total_label.pack()

        ctk.CTkLabel(
            card3, text="Valor acumulado",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 15))

        # Card 4: TCCMs Ativos
        card4 = ctk.CTkFrame(cards_frame, fg_color=COLORS["white"], corner_radius=8,
                             border_width=1, border_color=COLORS["border"])
        card4.grid(row=0, column=3, padx=(10, 0), sticky="nsew")

        icon_frame4 = ctk.CTkFrame(card4, fg_color="#E8F5E9", corner_radius=20, width=50, height=50)
        icon_frame4.pack(pady=(15, 8))
        icon_frame4.pack_propagate(False)
        ctk.CTkLabel(icon_frame4, text="TC", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["primary"]).pack(expand=True)

        self.tccms_ativos_label = ctk.CTkLabel(
            card4, text="0",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"]
        )
        self.tccms_ativos_label.pack()

        ctk.CTkLabel(
            card4, text="Tccms cadastrados",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 15))

    def build_table(self):
        container = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=8,
                                 border_width=1, border_color=COLORS["border"])
        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        ctk.CTkLabel(
            container,
            text="Notas Fiscais Recebidas",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Table header
        header = ctk.CTkFrame(container, fg_color="#FAFAFA", height=40)
        header.pack(fill="x", padx=15)
        header.pack_propagate(False)

        cols = ["Numero da NF", "Chave de acesso", "Data de Emissao", "Itens", "Valor Total(R$)", "Usuario", "Status"]
        widths = [100, 180, 100, 60, 100, 100, 80]

        for col, width in zip(cols, widths):
            ctk.CTkLabel(
                header, text=col, width=width,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(side="left", padx=5)

        # Table body
        self.table_body = ctk.CTkScrollableFrame(container, fg_color=COLORS["white"])
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Footer
        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(0, 15))

        self.total_registros_label = ctk.CTkLabel(
            footer, text="Total de Registros: 0",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        )
        self.total_registros_label.pack(side="left")

        self.valor_total_geral_label = ctk.CTkLabel(
            footer, text="Valor Total: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        )
        self.valor_total_geral_label.pack(side="right")

    def carregar_dados(self):
        db = Database()
        if db.conectar():
            # Notas Fiscais count
            result = db.executar("SELECT COUNT(*) FROM `nota fiscal`")
            if result:
                count_nf = result.fetchone()[0]
                self.notas_fiscais_label.configure(text=str(count_nf))

            # Itens count
            result = db.executar("SELECT COUNT(*) FROM `itens`")
            if result:
                count_itens = result.fetchone()[0]
                self.itens_recebidos_label.configure(text=str(count_itens))

            # Valor Total
            result = db.executar("SELECT SUM(valor_total) FROM `nota fiscal`")
            if result:
                valor = result.fetchone()[0] or 0
                valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.valor_total_label.configure(text=valor_fmt)

            # TCCMs Ativos
            result = db.executar("SELECT COUNT(*) FROM `tccm`")
            if result:
                count_tccm = result.fetchone()[0]
                self.tccms_ativos_label.configure(text=str(count_tccm))

            # Load notas fiscais for table
            result = db.executar("""
                SELECT nf.nota_fiscal, nf.chave_de_acesso, nf.data,
                       (SELECT COUNT(*) FROM produtos p WHERE p.`nota fiscal_nota_fiscal` = nf.nota_fiscal) as qtd_itens,
                       nf.valor_total, ag.nome_agente
                FROM `nota fiscal` nf
                JOIN `agente ibama` ag ON nf.`agente ibama_matricula` = ag.matricula
                ORDER BY nf.data DESC
            """)
            if result:
                rows = result.fetchall()
                for row in rows:
                    self._adicionar_linha_nota(row)
                self.total_registros_label.configure(text=f"Total de Registros: {len(rows)}")

            # Total valor
            result = db.executar("SELECT SUM(valor_total) FROM `nota fiscal`")
            if result:
                valor = result.fetchone()[0] or 0
                valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.valor_total_geral_label.configure(text=f"Valor Total: {valor_fmt}")

            db.desconectar()

    def _adicionar_linha_nota(self, row):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=40)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        nf, chave, data, qtd_itens, valor, usuario = row

        chave_str = str(chave)
        if len(chave_str) > 20:
            chave_str = chave_str[:20] + "..."

        valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        dados = [str(nf), chave_str, str(data), str(qtd_itens), valor_fmt, str(usuario), "OK"]
        widths = [100, 180, 100, 60, 100, 100, 80]

        for texto, width in zip(dados, widths):
            ctk.CTkLabel(
                linha, text=texto, width=width,
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text"]
            ).pack(side="left", padx=5)
