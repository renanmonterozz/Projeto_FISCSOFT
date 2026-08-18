import _path  # noqa: F401

import os
import calendar
from datetime import datetime as _dt

import customtkinter as ctk
from PIL import Image

<<<<<<< HEAD
from config.layout_system import LayoutSystem
from config.styles import ASSETS_DIR, COLORS, FONTS
=======
from config.styles import COLORS, FONTS
>>>>>>> main
from database.conexaodb import Database
from screens.crud_base import CrudBase


def _fmt_date(val):
    if not val:
        return "--"
    if hasattr(val, "strftime"):
        return val.strftime("%d/%m/%Y")
    try:
        return _dt.strptime(str(val), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(val)


class ToolTip:
    def __init__(self, widget, itens, master=None):
        self.widget = widget
        self.itens = itens
        self.tooltip_window = None
        self.master = master
        self.widget.bind("<Enter>", self.mostrar)
        self.widget.bind("<Leave>", self.esconder)

    def mostrar(self, event=None):
        if not self.itens:
            return
        self.esconder()
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        import tkinter as tk
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg=COLORS["white"])

        frame = ctk.CTkFrame(tw, fg_color=COLORS["white"], corner_radius=4,
                             border_width=1, border_color=COLORS["border"])
        frame.pack()

        ctk.CTkLabel(
            frame, text="Itens da NF",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=6, pady=(4, 2))

        for item in self.itens:
            ctk.CTkLabel(
                frame, text=f"\u2022 {item['nome']} | {item['unidade']} | {item['quantidade']}",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text"]
            ).pack(anchor="w", padx=6, pady=1)

        ctk.CTkLabel(frame, text="", height=4).pack()

    def esconder(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class MenuInicialPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, perfil="admin", processo_tccm=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"]) 
        self.usuario_logado = usuario_logado
        self.perfil = perfil
        self.processo_tccm = processo_tccm

        if processo_tccm:
            titulo = f"TCCM - {processo_tccm}"
            subtitulo = "Notas fiscais e itens deste processo"
        else:
            if perfil == "admin":
                titulo = "Menu do Administrador"
            elif perfil == "operador":
                titulo = "Menu do Operador"
            else:
                titulo = "Menu do Agente"
            subtitulo = "Gerencie usuarios, relatorios e informacoes do sistema"
        self.build_header(titulo, subtitulo)
        self.build_stats_cards()
        if processo_tccm:
            self.build_info_tccm()
        self.build_notas_table()

    def build_stats_cards(self):
        colors = COLORS
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        card_data = [
            ("Notas Fiscais", "Total de notas", "0"),
            ("Itens Recebidos", "Itens de notas aprovadas", "0"),
            ("Valor Total(R$)", "Valor acumulado", "R$ 0,00"),
        ]

        self.stat_labels = {}
        icons = ["nota.png", "caixa2.png", "cifrao.png"]

        for i, (titulo, subtitulo, valor) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards_frame, fg_color=colors["white"], corner_radius=4,
                border_width=1, border_color=colors["border"]
            )
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=15)

            icon_circle = ctk.CTkFrame(
                inner, fg_color=colors["primary_light"],
                width=48, height=48, corner_radius=24
            )
            icon_circle.pack(side="left", padx=(0, 12))
            icon_circle.pack_propagate(False)

            icon_img = None
            try:
                icon_img = ctk.CTkImage(
                    light_image=Image.open(os.path.join(ASSETS_DIR, icons[i])),
                    dark_image=Image.open(os.path.join(ASSETS_DIR, icons[i])),
                    size=(32, 32),
                )
            except Exception:
                pass

            if icon_img:
                ctk.CTkLabel(
                    icon_circle, text="",
                    image=icon_img
                ).pack(expand=True)
            else:
                ctk.CTkLabel(
                    icon_circle, text=["\U0001f4cb", "\U0001f4e6", "\U0001f4b0"][i],
                    font=ctk.CTkFont(size=18),
                    text_color=COLORS["primary"]
                ).pack(expand=True)

            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                text_frame, text=titulo,
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                text_color=colors["text"], anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame, text=subtitulo,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=colors["text_muted"], anchor="w"
            ).pack(anchor="w")

            lbl_valor = ctk.CTkLabel(
                card, text=valor,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=colors["text"]
            )
            lbl_valor.pack(pady=(0, 15))
            self.stat_labels[titulo] = lbl_valor

        self.atualizar_cards()

    def build_notas_table(self):
        colors = COLORS
        self.colunas_place = [
            (0.00, 0.14, "w"),      # Numero da NF
            (0.18, 0.14, "center"), # Data de Emissao
            (0.34, 0.10, "center"), # Itens
            (0.47, 0.14, "center"), # Valor Total
            (0.64, 0.20, "w"),      # Infrator
            (0.87, 0.11, "center"), # Status
        ]

        section = LayoutSystem.panel(
            self,
            height=340 if self.processo_tccm else None,
            fill="x" if self.processo_tccm else "both",
            expand=not self.processo_tccm,
            padding=(30, (0, 30)),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )
        if self.processo_tccm:
            section.pack_propagate(False)

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        dot = ctk.CTkFrame(
            header_frame, fg_color=colors["primary"],
            width=12, height=12, corner_radius=6
        )
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="Notas Fiscais Recebidas",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=colors["text"]
        ).pack(side="left")

        columns = [
            "Numero da NF", "Data de Emissao",
            "Itens", "Valor Total(R$)", "Infrator", "Status"
        ]
        header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=40, corner_radius=0)
        header.pack(fill="x", padx=15, pady=(5, 0))
        header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(10, 16))

        for col, (relx, relwidth, anchor) in zip(columns, self.colunas_place):
            ctk.CTkLabel(
                cols_frame, text=col,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor=anchor,
            ).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

        self.table_body = ctk.CTkScrollableFrame(
            section, fg_color=colors["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 5))

        footer = ctk.CTkFrame(section, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        self.lbl_total_registros = ctk.CTkLabel(
            footer, text="Total de Registros: 0",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=colors["text_muted"]
        )
        self.lbl_total_registros.pack(side="left")

        self.lbl_valor_total = ctk.CTkLabel(
            footer, text="Valor Total: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=colors["text_muted"]
        )
        self.lbl_valor_total.pack(side="right")

        self.notas = self._carregar_notas()
        self._render_rows()

    def _carregar_notas(self):
        with Database() as db:
            if not db.conexao:
                return []

            if self.processo_tccm:
                sql = """SELECT nf.nota_fiscal, nf.data,
                                nf.valor_total, nf.status_nota,
                                i.nome_infrator,
                                COUNT(DISTINCT p.lote) as qtd_itens,
                                GROUP_CONCAT(
                                    p.nome_item || '|' || COALESCE(p.quantidade, 0) || '|' || COALESCE(it.unidade_medida, 'un'),
                                    ';; '
                                ) as itens_detalhes
                         FROM "nota fiscal" nf
                         LEFT JOIN tccm t ON t.processo = nf.processo
                         LEFT JOIN infrator i ON i.id_infrator = t."infrator_id_infrator"
                         LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                            AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                         LEFT JOIN itens it ON it.id = p.itens_id
                         WHERE nf.processo = ?
                         GROUP BY nf.nota_fiscal, nf.data,
                                nf.valor_total, nf.status_nota, i.nome_infrator
                         ORDER BY nf.data DESC"""
                params = (self.processo_tccm,)
            else:
                sql = """SELECT nf.nota_fiscal, nf.data,
                                nf.valor_total, nf.status_nota,
                                i.nome_infrator,
                                COUNT(DISTINCT p.lote) as qtd_itens,
                                GROUP_CONCAT(
                                    p.nome_item || '|' || COALESCE(p.quantidade, 0) || '|' || COALESCE(it.unidade_medida, 'un'),
                                    ';; '
                                ) as itens_detalhes
                         FROM "nota fiscal" nf
                         LEFT JOIN tccm t ON t.processo = nf.processo
                         LEFT JOIN infrator i ON i.id_infrator = t."infrator_id_infrator"
                         LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                            AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                         LEFT JOIN itens it ON it.id = p.itens_id
                         GROUP BY nf.nota_fiscal, nf.data,
                                nf.valor_total, nf.status_nota, i.nome_infrator
                         ORDER BY nf.data DESC"""
                params = ()

            try:
                resultados = db.executar(sql, params)
                notas = []
                if resultados:
                    for row in resultados.fetchall():
                        itens_lista = []
                        if row[6]:
                            for item_str in row[6].split(";; "):
                                partes = item_str.split("|")
                                if len(partes) == 3:
                                    itens_lista.append({
                                        "nome": partes[0],
                                        "quantidade": int(partes[1]) if partes[1] else 0,
                                        "unidade": partes[2] or "un"
                                    })
                        notas.append({
                            "nota_fiscal": row[0] or "--",
                            "data": _fmt_date(row[1]),
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
                            "infrator": row[4] or "--",
                            "qtd_itens": row[5] if row[5] else 0,
                            "itens_detalhes": itens_lista,
                        })
                return notas
            except Exception:
                return []

    def _render_rows(self):
        colors = COLORS
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.notas:
            ctk.CTkLabel(
                self.table_body, text="Nenhuma nota fiscal cadastrada",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=colors["text_muted"]
            ).pack(pady=30)
            return

        for idx, nota in enumerate(self.notas):
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=44)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            cols = ctk.CTkFrame(linha, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

            if nota["status"] == "Aprovada":
                status_color = colors["success_dark"]
                status_text = "\u2714"
            elif nota["status"] == "Rejeitada":
                status_color = colors["danger"]
                status_text = "\u2718"
            else:
                status_color = colors["warning"]
                status_text = "\u26A0"

            dados = [
                (nota["nota_fiscal"], COLORS["text"]),
                (nota["data"], COLORS["text_muted"]),
                (str(nota["qtd_itens"]), COLORS["text_muted"], nota["itens_detalhes"]),
                (f"R$ {nota['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), COLORS["text_muted"]),
                (nota["infrator"], COLORS["text_muted"]),
                (status_text, status_color),
            ]

            for (relx, relwidth, anchor), item_dado in zip(self.colunas_place, dados):
                if len(item_dado) == 3:
                    valor, cor, itens_detalhes = item_dado
                    lbl = ctk.CTkLabel(
                        cols, text=valor,
                        font=ctk.CTkFont(size=FONTS["size_small"]),
                        text_color=cor, anchor=anchor, cursor="hand2"
                    )
                    lbl.place(relx=relx, relwidth=relwidth, rely=0, relheight=1)
                    ToolTip(lbl, itens_detalhes)
                else:
                    valor, cor = item_dado
                    ctk.CTkLabel(
                        cols, text=valor,
                        font=ctk.CTkFont(size=FONTS["size_small"]),
                        text_color=cor, anchor=anchor,
                    ).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

        self.lbl_total_registros.configure(text=f"Total de Registros: {len(self.notas)}")
        valor_total = sum(n["valor_total"] for n in self.notas)
        self.lbl_valor_total.configure(
            text=f"Valor Total: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def build_info_tccm(self):
        with Database() as db:
            if not db.conexao:
                return
            try:
                r = db.executar(
                    """SELECT processo, status, documento_sei, data_inicio, semestres,
                              data_validade, total_devido, total_pago
                       FROM tccm WHERE processo = ?""",
                    (self.processo_tccm,),
                )
                row = r.fetchone() if r else None
            except Exception:
                row = None

        if not row:
            return

        status = row[1] or "pendente"
        semestres = row[4] or 0

        # try to parse data_inicio from DB; prefer a datetime object when possible
        data_inicio_obj = None
        try:
            if hasattr(row[3], "year"):
                data_inicio_obj = row[3]
            else:
                data_inicio_obj = _dt.strptime(str(row[3]), "%Y-%m-%d")
        except Exception:
            data_inicio_obj = None

        # calculate data_validade = data_inicio + semestres * 6 months
        def _add_months(dt_obj, months):
            if not dt_obj:
                return None
            total = dt_obj.month - 1 + months
            y = dt_obj.year + total // 12
            m = total % 12 + 1
            day = min(dt_obj.day, calendar.monthrange(y, m)[1])
            return _dt(y, m, day)

        months_to_add = int(semestres) * 6 if semestres else 0
        data_validade_obj = _add_months(data_inicio_obj, months_to_add) if months_to_add and data_inicio_obj else (row[5] if row[5] else None)

        data_inicio = _fmt_date(data_inicio_obj)
        data_validade = _fmt_date(data_validade_obj)
        total_devido = float(row[6]) if row[6] else 0
        total_pago = float(row[7]) if row[7] else 0
        pendente = max(0, total_devido - total_pago)
        pct = (total_pago / total_devido * 100) if total_devido > 0 else 0

        def _fmt_brl(valor):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
        section.pack(fill="x", padx=30, pady=(0, 20))

        hdr = ctk.CTkFrame(section, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 8))

        dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Informações do TCCM",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["text"]).pack(side="left")

        progress_frame = ctk.CTkFrame(section, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 8))

        progress_bar_bg = ctk.CTkFrame(progress_frame, fg_color=COLORS["border"], height=8, corner_radius=4)
        progress_bar_bg.pack(fill="x")
        progress_bar_fg = ctk.CTkFrame(progress_bar_bg, fg_color=COLORS["primary"], height=8, corner_radius=4)
        progress_bar_fg.place(x=0, y=0, relwidth=pct / 100, relheight=1)

        ctk.CTkLabel(progress_frame, text=f"{pct:.1f}% pago",
                      font=ctk.CTkFont(size=FONTS["size_small"]),
                      text_color=COLORS["text_muted"]).pack(anchor="e", pady=(4, 0))

        info_grid = ctk.CTkFrame(section, fg_color="transparent")
        info_grid.pack(fill="x", padx=15, pady=(0, 15))
        for i in range(4):
            info_grid.grid_columnconfigure(i, weight=1)

        campos = [
            ("Processo", row[0] or "--"),
            ("Status", status.capitalize()),
            ("Documento SEI", row[2] or "--"),
            ("Data Inicio", data_inicio),
            ("Semestres", f"{semestres}"),
            ("Data Validade", data_validade),
            ("Total Devido", _fmt_brl(total_devido)),
            ("Total Pago", _fmt_brl(total_pago)),
            ("Total Pendente", _fmt_brl(pendente)),
        ]

        for i, (label, valor) in enumerate(campos):
            row_idx = i // 4
            col = i % 4
            frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            frame.grid(row=row_idx, column=col, padx=5, pady=4, sticky="w")
            ctk.CTkLabel(frame, text=label,
                          font=ctk.CTkFont(size=14),
                          text_color=COLORS["text_muted"]).pack(anchor="w")
            ctk.CTkLabel(frame, text=valor,
                          font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                          text_color=COLORS["text"]).pack(anchor="w")

    def atualizar_cards(self):
        with Database() as db:
            if not db.conexao:
                return

            if self.processo_tccm:
                try:
                    r = db.executar('SELECT COUNT(DISTINCT nota_fiscal) FROM "nota fiscal" WHERE processo = ?',
                                    (self.processo_tccm,)).fetchone()
                    total_nf = r[0] if r else 0
                except Exception:
                    total_nf = 0

                try:
                    r = db.executar(
                        'SELECT COUNT(p.lote) FROM produtos p '
                        'JOIN "nota fiscal" nf ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal '
                        'AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula" '
                        'WHERE nf.processo = ? AND nf.status_nota = \'Aprovada\'',
                        (self.processo_tccm,)
                    ).fetchone()
                    total_itens = r[0] if r else 0
                except Exception:
                    total_itens = 0

                try:
                    r = db.executar(
                        'SELECT COALESCE(SUM(valor_total), 0) FROM "nota fiscal" WHERE processo = ? AND status_nota = \'Aprovada\'',
                        (self.processo_tccm,)
                    ).fetchone()
                    valor_total = float(r[0]) if r else 0
                except Exception:
                    valor_total = 0

            else:
                try:
                    r = db.executar('SELECT COUNT(DISTINCT nota_fiscal) FROM "nota fiscal"').fetchone()
                    total_nf = r[0] if r else 0
                except Exception:
                    total_nf = 0

                try:
                    r = db.executar('SELECT COUNT(lote) FROM produtos p '
                                    'JOIN "nota fiscal" nf ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal '
                                    'AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula" '
                                    'WHERE nf.status_nota = \'Aprovada\'').fetchone()
                    total_itens = r[0] if r else 0
                except Exception:
                    total_itens = 0

                try:
                    r = db.executar(
                        'SELECT COALESCE(SUM(valor_total), 0) FROM "nota fiscal" WHERE status_nota = \'Aprovada\''
                    ).fetchone()
                    valor_total = float(r[0]) if r else 0
                except Exception:
                    valor_total = 0

        self.stat_labels["Notas Fiscais"].configure(text=str(total_nf))
        self.stat_labels["Itens Recebidos"].configure(text=str(total_itens))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)
