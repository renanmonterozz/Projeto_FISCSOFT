from tkinter import messagebox
import customtkinter as ctk
from config.styles import COLORS, FONTS
from config.layout_system import LayoutSystem
from services.notas_service import NotasFiscaisService



def _rebuild_sidebar_and_content(page):
    """Reconstrói a sidebar e o content_frame após alternar o tema."""
    root = page.winfo_toplevel()
    sidebar = getattr(root, "_sidebar", None)
    content_frame = getattr(root, "_content_frame", None)
    navegar = getattr(root, "_navegar", None)

    if sidebar:
        sidebar.rebuild()
    if content_frame:
        content_frame.configure(fg_color=COLORS["bg"])
    if navegar and content_frame:
        for w in content_frame.winfo_children():
            w.destroy()
        # Re-navega para a página atual (mantém na mesma tela)
        current_page = page.__class__.__name__
        page_map = {
            "MenuInicialPage": "Menu Principal",
            "ItensPage": "Itens",
            "UsuariosPage": "Agente",
            "InfratoresPage": "Usuario Externo",
            "LocaisPage": "Locais Cadastrados",
            "RelatoriosPage": "Relatorio",
            "RelatorioEntregaPage": "Destinacao",
            "HistoricoPage": "Historico",
        }
        page_name = page_map.get(current_page)
        if page_name:
            navegar(page_name)


class CrudBase:
    CARD_BORDER_RADIUS = 4

    def _servico_notas_alerta(self):
        service = getattr(self, "_alerta_notas_service", None)
        if service is None:
            service = NotasFiscaisService()
            self._alerta_notas_service = service
        return service

    def build_alerta_nota(self, header, processo_tccm=None, pack_direction="right"):
        """Exibe um sino que so aparece quando existe nota fiscal pendente de conferencia."""
        # only show alerta on the post-login main screen
        if not getattr(self, "is_post_login", False):
            return None

        pendentes = self._notas_pendentes(processo_tccm)
        if not pendentes:
            return None

        texto = self._texto_alerta_notas(pendentes)

        btn = ctk.CTkButton(
            header, text="\U0001f514  Nova nota fiscal",
            height=38, corner_radius=19,
            fg_color=COLORS["white"], hover_color=COLORS["primary_light"],
            text_color=COLORS["warning"], border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: messagebox.showinfo("Notificacao", texto, parent=self),
        )
        if pack_direction == "right":
            btn.pack(side="right", padx=(10, 0))
        else:
            btn.pack(side="left", padx=(0, 10))
        # keep a reference to the alerta button so it can be removed later
        try:
            self._alerta_btn = btn
        except Exception:
            self._alerta_btn = None

        # initialize exigencias tracking
        try:
            self._exigencias_set = set(
                self._servico_notas_alerta().listar_processos_com_correcao(processo_tccm)
            )
        except Exception:
            self._exigencias_set = set()

        return btn

    def _notas_pendentes(self, processo_tccm=None):
        """Retorna lista de (processo, quantidade) de notas fiscais pendentes de conferencia."""
        try:
            return self._servico_notas_alerta().listar_pendencias_alerta(processo_tccm)
        except Exception:
            return []

    def _texto_alerta_notas(self, pendentes):
        """Monta texto do alerta informando quantas notas foram anexadas e em qual processo."""
        if len(pendentes) == 1:
            processo, qtd = pendentes[0]
            palavra = "nota fiscal" if qtd == 1 else "notas fiscais"
            anexada = "anexada" if qtd == 1 else "anexadas"
            return f"Voce tem {qtd} {palavra} {anexada} no processo {processo}"
        total = sum(q for _, q in pendentes)
        partes = "; ".join(f"{q} no processo {p}" for p, q in pendentes)
        return f"Voce tem {total} notas fiscais anexadas: {partes}"

    def build_card(self, parent, **kwargs):
        return ctk.CTkFrame(
            parent,
            fg_color=COLORS["white"],
            corner_radius=self.CARD_BORDER_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

    def build_header(self, title, subtitle, alerta_nota=False, processo_tccm=None):
        colors = COLORS
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_frame, text=title,
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=colors["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame, text=subtitle,
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=colors["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        if alerta_nota:
                self.build_alerta_nota(
                header,
                processo_tccm=processo_tccm,
                pack_direction="right"
        )

    def build_filter_container(self):
        container = LayoutSystem.panel(
            self,
            fill="x",
            padding=(30, (0, 20)),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)
        return inner

    def build_search_entry(self, parent, placeholder, width=340):
        colors = COLORS
        frame = ctk.CTkFrame(
            parent, fg_color=colors["white"], border_width=1,
            border_color=colors["border"], corner_radius=4
        )
        frame.pack(side="left", padx=(0, 10))

        entry = ctk.CTkEntry(
            frame, placeholder_text=placeholder,
            width=width, height=38, border_width=0,
            fg_color=colors["white"], text_color=colors["text"],
            placeholder_text_color=colors["text_muted"],
        )
        entry.pack(side="left", padx=(12, 4), pady=2)
        ctk.CTkLabel(
            frame, text="\U0001f50d",
            font=ctk.CTkFont(size=14), text_color="#999999"
        ).pack(side="right", padx=(0, 10))
        return entry

    def build_filter_entry(self, parent, placeholder, width=200):
        colors = COLORS
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            width=width, height=38, border_width=1,
            border_color=colors["border"], corner_radius=4,
            fg_color=colors["white"], text_color=colors["text"],
            placeholder_text_color=colors["text_muted"],
        )
        entry.pack(side="left", padx=(0, 10))
        return entry

    def build_btn_frame(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(side="left", padx=(5, 0))
        return btn_frame

    def build_action_btn(self, parent, text, icon, command,
                         fg_color=None, hover_color=None,
                         text_color=None, border=True, bold=False):
        colors = COLORS
        if fg_color is None:
            fg_color = colors["white"]
        if hover_color is None:
            hover_color = colors["row_hover"]
        if text_color is None:
            text_color = colors["text"]
        btn = ctk.CTkButton(
            parent,
            image=icon,
            text=text,
            height=38, corner_radius=4,
            fg_color=fg_color, hover_color=hover_color,
            text_color=text_color,
            border_width=1 if border else 0,
            border_color=colors["border"],
            font=ctk.CTkFont(
                size=FONTS["size_body"],
                weight="bold" if bold else "normal"
            ),
            compound="left",
            command=command,
        )
        btn.pack(side="left", padx=(0, 8))
        return btn

    def build_table(self, pad_y=(0, 30), height=None):
        colors = COLORS
        self.table_frame = ctk.CTkFrame(
            self, fg_color=colors["white"], corner_radius=4,
            border_width=1, border_color=colors["border"]
        )
        if height:
            self.table_frame.configure(height=height)
            self.table_frame.pack(fill="x", padx=30, pady=pad_y)
            self.table_frame.pack_propagate(False)
        else:
            self.table_frame.pack(fill="both", expand=True, padx=30, pady=pad_y)
        return self.table_frame

    def build_table_header(self, parent, columns, weights, has_checkbox=True, alignments=None):
        colors = COLORS
        header = ctk.CTkFrame(parent, fg_color=colors["table_header"], height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        if has_checkbox:
            ctk.CTkLabel(header, text="", width=20).pack(side="left", padx=(17, 0))

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

        for i, w in enumerate(weights):
            cols.grid_columnconfigure(i, weight=w)

        if alignments is None:
            alignments = ["w"] * len(columns)

        for i, col_text in enumerate(columns):
            padx = (10, 5) if i == 0 else (5, 5) if i < len(columns) - 1 else (5, 10)
            ctk.CTkLabel(
                cols, text=col_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=colors["text_muted"],
                anchor=alignments[i]
            ).grid(row=0, column=i, sticky="ew", padx=padx)

        ctk.CTkLabel(
            header, text="Açoes",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=colors["text_muted"],
            width=120
        ).pack(side="right", padx=(0, 15))

        self.table_body = ctk.CTkScrollableFrame(
            parent, fg_color=colors["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)
        return self.table_body

    def add_data_row(self, has_checkbox=True):
        colors = COLORS
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(self.table_body, fg_color=colors["border"], height=1).pack(fill="x")

        cb = None
        if has_checkbox:
            cb = ctk.CTkCheckBox(linha, text="", width=20, height=20,
                                  border_width=2, corner_radius=4)
            cb.pack(side="left", padx=(17, 0))

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(10, 0))

        return linha, data, cb

    def add_action_buttons(self, parent, actions, width=120):
        colors = COLORS
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=width)
        frame.pack(side="right", padx=(0, 15))
        frame.pack_propagate(False)

        for icon, cmd in actions:
            ctk.CTkButton(
                frame,
                text=icon, width=32, height=32,
                corner_radius=4, fg_color=colors["white"],
                hover_color=colors["row_hover"], text_color=colors["text"],
                border_width=1, border_color=colors["border"],
                font=ctk.CTkFont(size=14),
                command=cmd,
            ).pack(side="left", padx=2)

    def clear_entries(self, *entries):
        for entry in entries:
            entry.delete(0, "end")

    def refresh_from_db(self, carregar_fn):
        self.data = carregar_fn()
        self.render_rows()

    def configure_data_columns(self, data_frame, weights):
        for i, w in enumerate(weights):
            data_frame.grid_columnconfigure(i, weight=w)

    def _check_exigencias_and_refresh(self, processo_tccm=None):
        """Check for exigencias (correcao solicitada) that were attended and refresh alerta button."""
        try:
            current = set(
                self._servico_notas_alerta().listar_processos_com_correcao(processo_tccm)
            )
        except Exception:
            current = set()

        prev = getattr(self, '_exigencias_set', set())
        removed = prev - current
        for proc in removed:
            try:
                messagebox.showinfo("Exigência atendida", f"Exigência atendida para processo {proc}", parent=self)
            except Exception:
                pass

        # store new set
        self._exigencias_set = current

        # refresh alerta visibility
        try:
            pendentes = self._notas_pendentes(processo_tccm)
        except Exception:
            pendentes = []

        if not pendentes:
            if hasattr(self, '_alerta_btn') and self._alerta_btn:
                try:
                    self._alerta_btn.destroy()
                except Exception:
                    pass
                self._alerta_btn = None
        else:
            texto = self._texto_alerta_notas(pendentes)
            if hasattr(self, '_alerta_btn') and self._alerta_btn:
                try:
                    self._alerta_btn.configure(command=lambda: messagebox.showinfo("Notificacao", texto, parent=self))
                except Exception:
                    pass
