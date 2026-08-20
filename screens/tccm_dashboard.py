import _path  # noqa: F401

import calendar
from datetime import datetime as _dt

import customtkinter as ctk

from config.styles import COLORS, FONTS
from config.permissoes import pode_acao
from screens.crud_base import CrudBase
from services.tccm_service import TccmService


def _calcular_data_validade(data_inicio, semestres):
    """Retorna a data final ao somar seis meses para cada semestre."""
    try:
        if isinstance(data_inicio, str):
            data_inicio = _dt.strptime(data_inicio, "%Y-%m-%d")

        total_meses = int(semestres) * 6
        mes_indice = data_inicio.month - 1 + total_meses
        ano = data_inicio.year + mes_indice // 12
        mes = mes_indice % 12 + 1
        dia = min(data_inicio.day, calendar.monthrange(ano, mes)[1])
        return data_inicio.replace(year=ano, month=mes, day=dia)
    except (TypeError, ValueError):
        return None


def _fmt_date(val):
    if not val:
        return "--"
    if hasattr(val, "strftime"):
        return val.strftime("%d/%m/%Y")
    try:
        return _dt.strptime(str(val), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(val)


def _fmt_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


COL_TCCM_CFG = [
    (0.0, 0.14, "w"),
    (0.14, 0.26, "w"),
    (0.40, 0.14, "center"),
    (0.54, 0.14, "center"),
    (0.68, 0.14, "center"),
    (0.82, 0.12, "center"),
]


class TccmDetalhesPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, processo, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.processo = processo
        self.is_post_login = True

        self.tccm_data = None
        self._carregar_dados()

        self.build_header_detalhes()
        self.build_info_section()
        self.build_pessoas_section()

    def build_header_detalhes(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        self.build_alerta_nota(right, processo_tccm=self.processo, pack_direction="right")

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(left, text=f"Detalhes TCCM - {self.processo}",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

    def build_info_section(self):
        if not self.tccm_data:
            return

        t = self.tccm_data
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Informacoes do TCCM",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        pct = (t["total_pago"] / t["total_devido"] * 100) if t["total_devido"] > 0 else 0
        progress_frame = ctk.CTkFrame(section, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 12))

        progress_bar_bg = ctk.CTkFrame(progress_frame, fg_color=COLORS["border"], height=8, corner_radius=4)
        progress_bar_bg.pack(fill="x")

        progress_bar_fg = ctk.CTkFrame(progress_bar_bg, fg_color=COLORS["primary"], height=8, corner_radius=4)
        progress_bar_fg.place(x=0, y=0, relwidth=pct / 100, relheight=1)

        ctk.CTkLabel(progress_frame, text=f"{pct:.1f}% pago",
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(anchor="e", pady=(4, 0))

        info_grid = ctk.CTkFrame(section, fg_color="transparent")
        info_grid.pack(fill="x", padx=15, pady=(0, 15))
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)
        info_grid.grid_columnconfigure(2, weight=1)
        info_grid.grid_columnconfigure(3, weight=1)

        campos = [
            ("Processo", t["processo"]),
            ("Status", t["status"].capitalize()),
            ("Documento SEI", t.get("documento_sei", "--")),
            ("Data Inicio", t.get("data_inicio", "--")),
            ("Semestres", f"{t.get('semestres', 0)}"),
            ("Data Validade", t["data_validade"]),
            ("Total Devido", _fmt_brl(t["total_devido"])),
            ("Total Pago", _fmt_brl(t["total_pago"])),
            ("Total Pendente", _fmt_brl(max(0, t["total_devido"] - t["total_pago"]))),
        ]

        for i, (label, valor) in enumerate(campos):
            row = i // 4
            col = i % 4
            frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            frame.grid(row=row, column=col, padx=5, pady=4, sticky="w")

            ctk.CTkLabel(frame, text=label,
                          font=ctk.CTkFont(size=14),
                          text_color=COLORS["text_muted"]).pack(anchor="w")
            ctk.CTkLabel(frame, text=valor,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w")

    def build_pessoas_section(self):
        if not self.tccm_data:
            return

        t = self.tccm_data
        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["warning"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Pessoas Envolvidas",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 15))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        inf_frame = ctk.CTkFrame(grid, fg_color=COLORS["bg"], corner_radius=6)
        inf_frame.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

        ctk.CTkLabel(inf_frame, text="Infrator",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", padx=12, pady=(10, 2))

        campos_inf = [
            ("Nome", t.get("infrator_nome", "--")),
            ("CPF", t.get("infrator_cpf", "--")),
            ("Email", t.get("infrator_email", "--")),
            ("Telefone", t.get("infrator_telefone", "--")),
        ]
        for label, valor in campos_inf:
            ctk.CTkLabel(inf_frame, text=f"{label}: {valor}",
                          font=ctk.CTkFont(size=13),
                          text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=1)
        ctk.CTkFrame(inf_frame, fg_color="transparent").pack(pady=(0, 8))

        age_frame = ctk.CTkFrame(grid, fg_color=COLORS["bg"], corner_radius=6)
        age_frame.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")

        ctk.CTkLabel(age_frame, text="Agente IBAMA",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["primary"]).pack(anchor="w", padx=12, pady=(10, 2))

        campos_age = [
            ("Nome", t.get("agente_nome", "--")),
            ("Matricula", str(t.get("agente_matricula", "--"))),
            ("CPF", t.get("agente_cpf", "--")),
            ("Email", t.get("agente_email", "--")),
        ]
        for label, valor in campos_age:
            ctk.CTkLabel(age_frame, text=f"{label}: {valor}",
                          font=ctk.CTkFont(size=13),
                          text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=1)
        ctk.CTkFrame(age_frame, fg_color="transparent").pack(pady=(0, 8))

    def _carregar_dados(self):
        dados = TccmService().buscar_detalhes(self.processo)
        if not dados:
            return
        dados["data_inicio"] = _fmt_date(dados["data_inicio"])
        dados["data_validade"] = _fmt_date(
            _calcular_data_validade(dados.get("data_inicio"), dados.get("semestres"))
            or dados.get("data_validade")
        )
        self.tccm_data = dados

class TccmDashboardPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, perfil="admin", **kwargs):
        self.on_selecionar = kwargs.pop("on_selecionar", None)
        self.on_sair = kwargs.pop("on_sair", None)
        self.on_cadastrar = kwargs.pop("on_cadastrar", None)
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.perfil = perfil
        self.is_post_login = True
        self.pode_criar_tccm = pode_acao(perfil, "criar_tccm")

        self.tccms_todos = []

        self._build_header_custom()
        self._build_status_cards()
        self._build_lista_tccms()

    def _build_header_custom(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(left, text="Painel Geral",
                      font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        ctk.CTkLabel(left, text="  Visão consolidada do controle de Termo de Cooperação e Controle de Multas",
                      font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                      text_color=COLORS["text_muted"]).pack(side="left", padx=(8, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self.build_alerta_nota(right, pack_direction="right")

        if self.pode_criar_tccm:
            ctk.CTkButton(
                right, text="+ Novo TCCM", height=36, corner_radius=6,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                command=self._navegar_cadastro,
            ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right, text="Sair", height=36, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._sair,
        ).pack(side="left")

    def _build_status_cards(self):
        self._cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._cards_frame.pack(fill="x", padx=30, pady=(0, 15))

        for i in range(2):
            self._cards_frame.grid_columnconfigure(i, weight=1)

        self._card_pendentes = self._criar_card_status(self._cards_frame, "Pendentes", "0", COLORS["warning"], 0)
        self._card_concluidos = self._criar_card_status(self._cards_frame, "Concluidos", "0", COLORS["success_dark"], 1)

    def _criar_card_status(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=4,
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=0, column=col, padx=5, sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 4))

        dot = ctk.CTkFrame(top, fg_color=cor, width=8, height=8, corner_radius=4)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(top, text=titulo,
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(side="left")

        lbl = ctk.CTkLabel(card, text=valor,
                           font=ctk.CTkFont(size=28, weight="bold"),
                           text_color=COLORS["text"])
        lbl.pack(anchor="w", padx=14, pady=(0, 12))

        return card, lbl

    def _build_lista_tccms(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header_row,
            text="Todos os TCCMs",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            header_row, text="",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["primary"],
        )
        self.lbl_count.pack(side="right", padx=(0, 12))

        filter_frame = ctk.CTkFrame(header_row, fg_color="transparent")
        filter_frame.pack(side="right", padx=(0, 24))

        ctk.CTkLabel(filter_frame, text="Filtrar:",
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 6))

        self.entry_filtro = ctk.CTkEntry(
            filter_frame, height=32, width=220, corner_radius=6,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="Processo, infrator ou status...",
        )
        self.entry_filtro.pack(side="left")
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tccms())

        col_header = ctk.CTkFrame(container, fg_color=COLORS["table_header"], height=36, corner_radius=4)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        cols = ctk.CTkFrame(col_header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

        colunas = ["Processo", "Infrator", "Total Devido", "Total Pago", "Validade", "Status"]

        for texto, (rx, rw, anchor) in zip(colunas, COL_TCCM_CFG):
            ctk.CTkLabel(
                cols, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        self.table_body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.table_body.pack(fill="both", expand=True)

        self._carregar_tccms()

    def _carregar_tccms(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        tccms = []
        qtd_pendentes = 0
        qtd_concluidos = 0

        try:
            tccms = TccmService().listar_dashboard()
            for tccm in tccms:
                if tccm["status"] == "concluido":
                    qtd_concluidos += 1
                else:
                    qtd_pendentes += 1
                tccm["data_validade"] = _fmt_date(tccm["data_validade"])
            tccms = tccms
        except Exception:
            tccms = []

        self.tccms_todos = tccms
        self.lbl_count.configure(text=f"{len(tccms)} TCCM(s)")

        self._card_pendentes[1].configure(text=str(qtd_pendentes))
        self._card_concluidos[1].configure(text=str(qtd_concluidos))

        self._filtrar_tccms()

    def _filtrar_tccms(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        termo = self.entry_filtro.get().strip().lower()
        filtrados = self.tccms_todos
        if termo:
            filtrados = [t for t in self.tccms_todos
                         if termo in t["processo"].lower()
                         or termo in t["infrator"].lower()
                         or termo in t["status"].lower()
                         or termo in t["cpf"].lower()]

        self.lbl_count.configure(text=f"{len(filtrados)} TCCM(s)")

        if not filtrados:
            ctk.CTkLabel(self.table_body, text="Nenhum TCCM encontrado",
                          font=ctk.CTkFont(size=FONTS["size_body"]),
                          text_color=COLORS["text_muted"]).pack(pady=40)
            return

        for idx, t in enumerate(filtrados):
            row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
            row = ctk.CTkFrame(self.table_body, fg_color=row_bg, height=40,
                                corner_radius=0, cursor="hand2")
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            row.bind("<Button-1>", lambda e, proc=t["processo"]: self._selecionar(proc))

            cols = ctk.CTkFrame(row, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

            if t["status"] == "concluido":
                st_text = "Concluido"
                st_cor = COLORS["success_dark"]
            elif t["status"] == "pago_parcial":
                st_text = "Parcial"
                st_cor = "#FF9800"
            else:
                st_text = "Pendente"
                st_cor = COLORS["warning"]

            dados = [
                t["processo"], t["infrator"],
                _fmt_brl(t["total_devido"]), _fmt_brl(t["total_pago"]),
                t["data_validade"], st_text,
            ]
            for i, valor in enumerate(dados):
                relx, relwidth, anchor = COL_TCCM_CFG[i]
                cor = COLORS["text"] if i == 0 else (st_cor if i == 5 else COLORS["text_muted"])
                weight = "bold" if i == 0 or i == 5 else "normal"
                ctk.CTkLabel(
                    cols, text=valor,
                    font=ctk.CTkFont(size=FONTS["size_small"], weight=weight),
                    text_color=cor, anchor=anchor,
                ).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

            ctk.CTkButton(
                row, text="\u25b6", width=32, height=28,
                corner_radius=4, fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"], text_color="white",
                font=ctk.CTkFont(size=12),
                command=lambda proc=t["processo"]: self._selecionar(proc),
            ).place(relx=1.0, rely=0.5, anchor="e", x=-15)

    def _selecionar(self, processo):
        if self.on_selecionar:
            self.on_selecionar(processo)

    def _navegar_cadastro(self):
        if self.on_cadastrar:
            self.on_cadastrar()

    def _recarregar(self):
        for w in self.table_body.winfo_children():
            w.destroy()
        self._carregar_tccms()

    def _sair(self):
        if self.on_sair:
            self.on_sair()
