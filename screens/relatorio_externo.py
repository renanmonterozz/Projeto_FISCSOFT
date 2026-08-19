import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.service.dashboard_service import formatar_data, formatar_moeda_brl, status_nota
from screens.widgets import CalendarioPopup, ComboBoxComSeta





class RelatorioExterno(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator

        self.build_header("Relatório Geral","Visualize o resumo das suas notas fiscais e processos TCCM.", alerta_nota=False)
        self.build_filter_bar()
        self.build_stats_cards()
        self.build_relatorio_content()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.data_inicio = None
        self.data_fim = None
        # Processo (TCCM) combobox (left of the period selector)
        col_processo = ctk.CTkFrame(row, fg_color="transparent")
        col_processo.pack(side="left", padx=(0, 10))


        # use the same style as in Cadastrar Notas
        self.combo_processo = ComboBoxComSeta(
            col_processo, values=["Todos"], height=38, width=300,
            border_width=1, border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            command=self._on_processo_changed,
        )
        self.combo_processo.pack(fill="x")
        self.combo_processo.set("Todos")

        ctk.CTkButton(
            row, text="Selecionar Periodo", height=38, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self._abrir_calendario
        ).pack(side="left", padx=(0, 10))

        # periodo label (shows selected period)
        self.lbl_periodo = ctk.CTkLabel(
            row, text="Periodo: -", font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_periodo.pack(side="left", padx=(10, 0))


        try:
            self._carregar_processos()
        except Exception:
            pass

        btn_frame = self.build_btn_frame(row)
        # create gerar relatorio button but keep it disabled until periodo is selected
        self.btn_gerar = self.build_action_btn(btn_frame, "  Gerar Relatorio", None, self.gerar_relatorio,
                              fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                              text_color="white", border=False, bold=True)
        try:
            self.btn_gerar.configure(state="disabled")
        except Exception:
            pass
        self.build_action_btn(btn_frame, "  Limpar", None, self.limpar_filtros)

    def _abrir_calendario(self):
        CalendarioPopup(self, title="Selecionar Periodo", on_confirm=self._periodo_selecionado)

    def _carregar_processos(self):
        try:
            with Database() as db:
                if not db.conexao:
                    return
                sql = """SELECT t.processo, i.nome_infrator
                         FROM tccm t
                         JOIN infrator i ON t."infrator_id_infrator" = i.id_infrator
                         WHERE t."infrator_id_infrator" = ?
                         ORDER BY t.processo"""
                resultado = db.executar(sql, (self.id_infrator,))
                if resultado:
                    rows = resultado.fetchall()
                    if rows:
                        self._processo_map = {}
                        opcoes = []
                        for row in rows:
                            processo = row[0]
                            nome_infrator = row[1]
                            display = f"{processo} - {nome_infrator}"
                            self._processo_map[display] = processo
                            opcoes.append(display)
                        valores = ["Todos"] + opcoes
                        self.combo_processo.configure(values=valores)
                        self.combo_processo.set("Todos")
                    else:
                        self.combo_processo.configure(values=["Todos", "Nenhum TCCM encontrado"])
                        self.combo_processo.set("Todos")
        except Exception:
            pass

    def _get_processo_real(self):
        display = self.combo_processo.get().strip()
        if not display or display == "Todos" or "Nenhum TCCM" in display:
            return ""
        if hasattr(self, '_processo_map') and display in self._processo_map:
            return self._processo_map[display]
        if " - " in display:
            return display.split(" - ")[0].strip()
        return display

    def _on_processo_changed(self, event=None):
        # reload data when processo changes
        self._carregar_dados()
        self._atualizar_cards()

    def _periodo_selecionado(self, inicio, fim):
        self.data_inicio = inicio
        self.data_fim = fim
        texto = f"Periodo: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
        self.lbl_periodo.configure(text=texto, text_color=COLORS["text"])
        self._carregar_dados()
        self._atualizar_cards()
        # enable gerar relatorio button when a period is selected
        if hasattr(self, 'btn_gerar'):
            try:
                self.btn_gerar.configure(state="normal")
            except Exception:
                pass

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        card_data = [
            ("Total Notas", "Notas enviadas", "0"),
            ("Aprovadas", "Notas aprovadas", "0"),
            ("Pendentes", "Aguardando analise", "0"),
            ("Valor Total(R$)", "Valor acumulado", "R$ 0,00"),
        ]

        self.stat_labels = {}
        icons = ["\U0001f4cb", "\u2705", "\u23F3", "\U0001f4b0"]

        for i, (titulo, subtitulo, valor) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards_frame, fg_color=COLORS["white"], corner_radius=4,
                border_width=1, border_color=COLORS["border"]
            )
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=15)

            icon_circle = ctk.CTkFrame(
                inner, fg_color=COLORS["primary_light"],
                width=48, height=48, corner_radius=24
            )
            icon_circle.pack(side="left", padx=(0, 12))
            icon_circle.pack_propagate(False)

            ctk.CTkLabel(
                icon_circle, text=icons[i],
                font=ctk.CTkFont(size=18),
                text_color=COLORS["primary"]
            ).pack(expand=True)

            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                text_frame, text=titulo,
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                text_color=COLORS["text"], anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame, text=subtitulo,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            lbl_valor = ctk.CTkLabel(
                card, text=valor,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=COLORS["text"]
            )
            lbl_valor.pack(pady=(0, 15))
            self.stat_labels[titulo] = lbl_valor

        self._atualizar_cards()

    def build_relatorio_content(self):
        section = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        section.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        dot = ctk.CTkFrame(
            header_frame, fg_color=COLORS["primary"],
            width=12, height=12, corner_radius=6
        )
        dot.pack(side="left", padx=(0, 8))
        dot.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="Detalhamento por Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        columns = [
            "Numero NF", "Data Emissao", "Valor(R$)",
            "Quantidade Itens", "Status"
        ]

        col_cfg = [
            (0.0,  0.22, "w"),    # Numero NF
            (0.22, 0.18, "center"),  # Data Emissao
            (0.40, 0.18, "center"),  # Valor
            (0.58, 0.16, "center"),  # Qtd Itens
            (0.74, 0.14, "center"),  # Status
            (0.88, 0.12, "center"),  # Detalhes
        ]

        header = ctk.CTkFrame(section, fg_color=COLORS["table_header"], height=40, corner_radius=0)
        header.pack(fill="x", padx=15, pady=(5, 0))
        header.pack_propagate(False)

        for texto, (rx, rw, anchor) in zip(columns, col_cfg):
            ctk.CTkLabel(
                header, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
        ).place(relx=0.88, relwidth=0.12, rely=0, relheight=1)

        self.table_body = ctk.CTkScrollableFrame(
            section, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        footer = ctk.CTkFrame(section, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        self.lbl_total = ctk.CTkLabel(
            footer, text="Total de Registros: 0",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_total.pack(side="left")

        self.lbl_valor_total = ctk.CTkLabel(
            footer, text="Valor Total: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"]
        )
        self.lbl_valor_total.pack(side="right")

        self._carregar_dados()

    def _carregar_dados(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if not self.id_infrator:
            ctk.CTkLabel(
                self.table_body, text="Nenhum dado encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            self._processo_map = {}
            return


        with Database() as db:
            if not db.conexao:
                return

            sql = """SELECT nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota,
                            COUNT(p.lote) as qtd_itens
                     FROM "nota fiscal" nf
                     JOIN tccm t ON nf.processo = t.processo
                     LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                        AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                     WHERE t."infrator_id_infrator" = ?"""
            params = [self.id_infrator]
            # filter by selected processo if any
            try:
                proc = self._get_processo_real()
            except Exception:
                proc = ""
            if proc:
                sql += " AND nf.processo = ?"
                params.append(proc)

            if self.data_inicio and self.data_fim:
                sql += " AND nf.data >= ? AND nf.data <= ?"
                params.append(self.data_inicio.strftime("%Y-%m-%d"))
                params.append(self.data_fim.strftime("%Y-%m-%d"))

            sql += " GROUP BY nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota ORDER BY nf.data DESC"
            try:
                resultado = db.executar(sql, params)
                dados = []
                if resultado:
                    for row in resultado.fetchall():
                        raw_data = row[1]
                        if hasattr(raw_data, "strftime"):
                            data_fmt = raw_data.strftime("%d/%m/%Y")
                        elif raw_data:
                            from datetime import datetime as _dt
                            try:
                                data_fmt = _dt.strptime(str(raw_data), "%Y-%m-%d").strftime("%d/%m/%Y")
                            except Exception:
                                data_fmt = str(raw_data)
                        else:
                            data_fmt = "--"
                        dados.append({
                            "nota_fiscal": row[0] or "--",
                            "data": data_fmt,
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
                            "qtd_itens": row[4] if row[4] else 0,
                        })
            except Exception:
                dados = []

        if not dados:
            ctk.CTkLabel(
                self.table_body, text="Nenhum dado encontrado",
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text_muted"]
            ).pack(pady=30)
            return

        col_cfg = [
            (0.0,  0.22, "w"),    # Numero NF
            (0.22, 0.18, "center"),  # Data Emissao
            (0.40, 0.18, "center"),  # Valor
            (0.58, 0.16, "center"),  # Qtd Itens
            (0.74, 0.14, "center"),  # Status
            (0.88, 0.12, "center"),  # Detalhes
        ]

        for item in dados:
            linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=48)
            linha.pack(fill="x")
            linha.pack_propagate(False)

            ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

            valor_formatado = f"R$ {item['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            if item["status"] == "Aprovada":
                status_color = COLORS["success_dark"]
                status_text = "\u2714 Aprovada"
            elif item["status"] == "Rejeitada":
                status_color = COLORS["danger"]
                status_text = "\u2718 Rejeitada"
            elif item["status"] == "Correcao Solicitada":
                status_color = "#D97706"
                status_text = "\u270F Correcao"
            else:
                status_color = COLORS["warning"]
                status_text = "\u26A0 Pendente"

            valores = [
                item["nota_fiscal"], item["data"], valor_formatado,
                str(item["qtd_itens"]), status_text
            ]

            for texto, (rx, rw, anchor) in zip(valores, col_cfg[:5]):
                cor = COLORS["text"] if anchor == "w" else status_color if texto == status_text else COLORS["text_muted"]
                ctk.CTkLabel(
                    linha, text=texto,
                    font=ctk.CTkFont(size=FONTS["size_small"], weight="bold" if anchor == "w" else "normal"),
                    text_color=cor, anchor=anchor,
                ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

            btn_detalhes = ctk.CTkButton(
                linha, text="Detalhes", height=28, width=80, corner_radius=4,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                text_color="white", border_width=0,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                command=lambda nf=item["nota_fiscal"]: self._ver_detalhes(nf),
            )
            btn_detalhes.place(relx=0.89, rely=0.15, relwidth=0.10, relheight=0.7)

        self.lbl_total.configure(text=f"Total de Registros: {len(dados)}")
        valor_total = sum(d["valor_total"] for d in dados if d.get("status") == "Aprovada")
        self.lbl_valor_total.configure(
            text=f"Valor Total: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _atualizar_cards(self):
        if not self.id_infrator:
            return

        with Database() as db:
            if not db.conexao:
                return

            base = '''FROM "nota fiscal" nf
                      JOIN tccm t ON nf.processo = t.processo
                      WHERE t."infrator_id_infrator" = ?'''

            try:
                r = db.executar(
                    f'SELECT COUNT(DISTINCT nf.nota_fiscal) {base}',
                    (self.id_infrator,)
                ).fetchone()
                total = r[0] if r else 0
            except Exception:
                total = 0

            try:
                r = db.executar(
                    f"SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Aprovada'",
                    (self.id_infrator,)
                ).fetchone()
                aprovadas = r[0] if r else 0
            except Exception:
                aprovadas = 0

            try:
                r = db.executar(
                    f"SELECT COUNT(DISTINCT nf.nota_fiscal) {base} AND nf.status_nota = 'Pendente'",
                    (self.id_infrator,)
                ).fetchone()
                pendentes = r[0] if r else 0
            except Exception:
                pendentes = 0

            try:
                r = db.executar(
                    f"""SELECT COALESCE(SUM(nf.valor_total), 0) {base}
                        AND nf.status_nota = 'Aprovada'""",
                    (self.id_infrator,)
                ).fetchone()
                valor_total = float(r[0]) if r else 0
            except Exception:
                valor_total = 0

        self.stat_labels["Total Notas"].configure(text=str(total))
        self.stat_labels["Aprovadas"].configure(text=str(aprovadas))
        self.stat_labels["Pendentes"].configure(text=str(pendentes))
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total(R$)"].configure(text=valor_formatado)

    def gerar_relatorio(self):
        if not self.data_inicio or not self.data_fim:
            messagebox.showwarning("Aviso", "Selecione um periodo (data de inicio e fim) para gerar o relatorio.")
            return

        if not self.id_infrator:
            messagebox.showwarning("Aviso", "Nenhum infrator logado.")
            return

        periodo_label = f"{self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}"
        dados_nf = []
        itens_por_nf = {}

        with Database() as db:
            if not db.conexao:
                return

            sql_nf = """SELECT nf.nota_fiscal, nf.data, nf.valor_total, nf.status_nota, nf.processo
                        FROM "nota fiscal" nf
                        JOIN tccm t ON nf.processo = t.processo
                        WHERE t."infrator_id_infrator" = ?
                          AND nf.data >= ? AND nf.data <= ?
                        ORDER BY nf.data DESC"""
            try:
                # allow optional processo filter
                proc = self._get_processo_real() if hasattr(self, '_get_processo_real') else ""
                params = [self.id_infrator, self.data_inicio.strftime("%Y-%m-%d"), self.data_fim.strftime("%Y-%m-%d")]
                if proc:
                    sql_nf = sql_nf.replace("ORDER BY nf.data DESC", "AND nf.processo = ?\n                        ORDER BY nf.data DESC")
                    params.append(proc)
                resultado = db.executar(sql_nf, tuple(params))
                if resultado:
                    for row in resultado.fetchall():
                        raw_data = row[1]
                        if hasattr(raw_data, "strftime"):
                            data_fmt = raw_data.strftime("%d/%m/%Y")
                        elif raw_data:
                            from datetime import datetime as _dt
                            try:
                                data_fmt = _dt.strptime(str(raw_data), "%Y-%m-%d").strftime("%d/%m/%Y")
                            except Exception:
                                data_fmt = str(raw_data)
                        else:
                            data_fmt = "--"
                        nf_info = {
                            "nota_fiscal": row[0] or "--",
                            "data": data_fmt,
                            "valor_total": float(row[2]) if row[2] else 0,
                            "status": row[3] or "Pendente",
                            "processo": row[4] or "--",
                        }
                        dados_nf.append(nf_info)

                        sql_itens = """SELECT p.nome_item, p.quantidade, p.preco_unitario
                                       FROM produtos p
                                       WHERE p."nota fiscal_nota_fiscal" = ?
                                       ORDER BY p.lote"""
                        res_itens = db.executar(sql_itens, (row[0],))
                        itens = []
                        if res_itens:
                            for ir in res_itens.fetchall():
                                qtd = int(ir[1]) if ir[1] else 0
                                preco = float(ir[2]) if ir[2] else 0
                                itens.append({
                                    "nome": ir[0] or "--",
                                    "quantidade": qtd,
                                    "preco_unitario": preco,
                                    "subtotal": qtd * preco,
                                })
                        itens_por_nf[row[0]] = itens
            except Exception:
                pass

        if not dados_nf:
            messagebox.showinfo("Relatorio", f"Nenhuma nota fiscal encontrada para o periodo {periodo_label}.")
            return

        texto = "RELATORIO DE NOTAS FISCAIS - PERIODO\n"
        texto += "=" * 50 + "\n\n"
        texto += f"Periodo: {periodo_label}\n"
        texto += f"Total de Notas Fiscais: {len(dados_nf)}\n"

        valor_total_geral = sum(nf["valor_total"] for nf in dados_nf if nf.get("status") == "Aprovada")
        texto += f"Valor Total: R$ {valor_total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"
        texto += "\n"

        for nf in dados_nf:
            texto += f"NOTA FISCAL: {nf['nota_fiscal']}\n"
            texto += f"  Data: {nf['data']}\n"
            texto += f"  Processo: {nf['processo']}\n"
            texto += f"  Status: {nf['status']}\n"
            texto += f"  Valor: R$ {nf['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"

            itens = itens_por_nf.get(nf["nota_fiscal"], [])
            if itens:
                texto += "  Itens:\n"
                texto += "  " + "-" * 46 + "\n"
                for item in itens:
                    preco_fmt = f"R$ {item['preco_unitario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    subtot_fmt = f"R$ {item['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    texto += f"    {item['nome']}\n"
                    texto += f"      Qtd: {item['quantidade']}  |  Unit: {preco_fmt}  |  Subtotal: {subtot_fmt}\n"
                texto += "  " + "-" * 46 + "\n"
            else:
                texto += "  Nenhum item registrado.\n"
            texto += "\n"

        texto += "=" * 50 + "\n"
        texto += f"Total de Itens: {sum(len(itens) for itens in itens_por_nf.values())}\n"
        valor_total_itens = sum(
            item["subtotal"]
            for nf in dados_nf
            if nf.get("status") == "Aprovada"
            for item in itens_por_nf.get(nf["nota_fiscal"], [])
        )
        texto += f"Valor Total Itens: R$ {valor_total_itens:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "\n"

        from tkinter import filedialog
        caminho = filedialog.asksaveasfilename(
            title="Salvar Relatorio",
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile=f"relatorio_{self.data_inicio.strftime('%d-%m-%Y')}_a_{self.data_fim.strftime('%d-%m-%Y')}.txt",
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            messagebox.showinfo("Sucesso", f"Relatorio salvo em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel salvar o relatorio:\n{e}")

    def limpar_filtros(self):
        self.data_inicio = None
        self.data_fim = None
        self._carregar_dados()
        self._atualizar_cards()
        # disable gerar relatorio when filters cleared
        if hasattr(self, 'btn_gerar'):
            try:
                self.btn_gerar.configure(state="disabled")
            except Exception:
                pass

    def _ver_detalhes(self, nota_fiscal):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Detalhes da NF {nota_fiscal}")
        popup.geometry("900x680+{}+{}".format(
            (popup.winfo_screenwidth() - 900) // 2,
            (popup.winfo_screenheight() - 680) // 2
        ))
        popup.minsize(750, 550)
        popup.resizable(True, True)
        popup.configure(fg_color=COLORS["white"])
        popup.transient(self)
        popup.grab_set()

        container = ctk.CTkFrame(
            popup, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        container.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        top_bar = ctk.CTkFrame(container, fg_color="transparent")
        top_bar.place(relx=0.04, rely=0.02, relwidth=0.92, relheight=0.08)

        ctk.CTkLabel(
            top_bar, text=f"Nota Fiscal #{nota_fiscal}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["primary"]
        ).place(relx=0, rely=0)

        ctk.CTkLabel(
            top_bar, text="Detalhes completos da nota fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        ).place(relx=0, rely=0.55)

        dados_nf = self._buscar_dados_nf(nota_fiscal)

        info_card = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        info_card.place(relx=0.04, rely=0.12, relwidth=0.92, relheight=0.30)

        ctk.CTkLabel(
            info_card, text="Dados da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).place(relx=0.04, rely=0.04)

        campos = [
            ("Numero NF:", dados_nf.get("nota_fiscal", "--")),
            ("Data Emissao:", dados_nf.get("data", "--")),
            ("Chave de Acesso:", dados_nf.get("chave", "--")),
            ("Valor Total:", dados_nf.get("valor_total_fmt", "R$ 0,00")),
            ("Status:", dados_nf.get("status", "--")),
            ("Processo:", dados_nf.get("processo", "--")),
        ]

        y_start = 0.18
        y_step = 0.13
        for i, (label_text, valor) in enumerate(campos):
            y = y_start + i * y_step
            ctk.CTkLabel(
                info_card, text=label_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor="w", width=140
            ).place(relx=0.04, rely=y)

            ctk.CTkLabel(
                info_card, text=valor,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text"], anchor="w"
            ).place(relx=0.22, rely=y)

        itens_card = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        itens_card.place(relx=0.04, rely=0.45, relwidth=0.92, relheight=0.45)

        ctk.CTkLabel(
            itens_card, text="Itens da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"]
        ).place(relx=0.04, rely=0.03)

        itens = dados_nf.get("itens", [])

        if not itens:
            ctk.CTkLabel(
                itens_card, text="Nenhum item encontrado",
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"]
            ).place(relx=0.35, rely=0.25)
        else:
            header = ctk.CTkFrame(itens_card, fg_color=COLORS["table_header"], height=36, corner_radius=0)
            header.place(relx=0.03, rely=0.10, relwidth=0.94)
            header.pack_propagate(False)

            col_cfg = [
                (0.0,  0.40, "w"),    # Item
                (0.40, 0.15, "center"),  # Qtd.
                (0.55, 0.22, "center"),  # Preco Unit.
                (0.77, 0.23, "center"),  # Subtotal
            ]

            titulos = ["Item", "Qtd.", "Preco Unit. (R$)", "Subtotal (R$)"]
            for texto, (rx, rw, anchor) in zip(titulos, col_cfg):
                ctk.CTkLabel(
                    header, text=texto,
                    font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                    text_color=COLORS["text_muted"],
                    anchor=anchor,
                ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

            scroll = ctk.CTkScrollableFrame(
                itens_card, fg_color=COLORS["white"], corner_radius=0
            )
            scroll.place(relx=0.03, rely=0.22, relwidth=0.94, relheight=0.73)

            for idx, item in enumerate(itens):
                linha = ctk.CTkFrame(scroll, fg_color="transparent", height=32)
                linha.pack(fill="x")
                linha.pack_propagate(False)

                if idx < len(itens) - 1:
                    ctk.CTkFrame(scroll, fg_color="#E0E0E0", height=1).pack(fill="x")

                preco_fmt = f"R$ {item['preco_unitario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                subtot_fmt = f"R$ {item['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                valores = [item["nome"], str(item["quantidade"]), preco_fmt, subtot_fmt]
                for texto, (rx, rw, anchor) in zip(valores, col_cfg):
                    ctk.CTkLabel(
                        linha, text=texto,
                        font=ctk.CTkFont(size=FONTS["size_small"]),
                        text_color=COLORS["text"] if anchor == "w" else COLORS["text_muted"],
                        anchor=anchor,
                    ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        ctk.CTkButton(
            container, text="Fechar", height=36, corner_radius=4,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=popup.destroy
        ).place(relx=0.38, rely=0.92, relwidth=0.24)

    def _buscar_dados_nf(self, nota_fiscal):
        dados = {}
        with Database() as db:
            if not db.conexao:
                return dados

            try:
                sql = """SELECT nf.nota_fiscal, nf.data, nf.chave_de_acesso,
                                nf.valor_total, nf.status_nota, nf.processo
                         FROM "nota fiscal" nf
                         JOIN tccm t ON nf.processo = t.processo
                         WHERE nf.nota_fiscal = ?
                           AND t."infrator_id_infrator" = ?
                         LIMIT 1"""
                resultado = db.executar(sql, (nota_fiscal, self.id_infrator,))
                row = resultado.fetchone() if resultado else None
                if row:
                    raw_data = row[1]
                    if hasattr(raw_data, "strftime"):
                        data_fmt = raw_data.strftime("%d/%m/%Y")
                    elif raw_data:
                        from datetime import datetime as _dt
                        try:
                            data_fmt = _dt.strptime(str(raw_data), "%Y-%m-%d").strftime("%d/%m/%Y")
                        except Exception:
                            data_fmt = str(raw_data)
                    else:
                        data_fmt = "--"

                    valor = float(row[3]) if row[3] else 0
                    valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    dados = {
                        "nota_fiscal": row[0] or "--",
                        "data": data_fmt,
                        "chave": row[2] or "--",
                        "valor_total": valor,
                        "valor_total_fmt": valor_fmt,
                        "status": row[4] or "Pendente",
                        "processo": row[5] or "--",
                    }
            except Exception:
                pass

            try:
                sql_itens = """SELECT p.nome_item, p.quantidade, p.preco_unitario
                               FROM produtos p
                               WHERE p."nota fiscal_nota_fiscal" = ?
                               ORDER BY p.lote"""
                resultado_itens = db.executar(sql_itens, (nota_fiscal,))
                itens = []
                if resultado_itens:
                    for item_row in resultado_itens.fetchall():
                        qtd = int(item_row[1]) if item_row[1] else 0
                        preco = float(item_row[2]) if item_row[2] else 0
                        itens.append({
                            "nome": item_row[0] or "--",
                            "quantidade": qtd,
                            "preco_unitario": preco,
                            "subtotal": qtd * preco,
                        })
                dados["itens"] = itens
            except Exception:
                dados["itens"] = []

        return dados
