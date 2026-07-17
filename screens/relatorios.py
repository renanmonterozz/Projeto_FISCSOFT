import _path  # noqa: F401

from datetime import datetime as _dt
from tkinter import messagebox

import customtkinter as ctk

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone


def _fmt_date(val):
    if not val:
        return "--"
    if hasattr(val, "strftime"):
        return val.strftime("%d/%m/%Y")
    try:
        return _dt.strptime(str(val), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(val)


class RelatoriosPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.nf_selecionada = None

        self.build_header("Monitoramento de Notas Fiscais",
                          "Acompanhe todas as notas fiscais enviadas neste TCCM.")
        self.build_filter_bar()
        self.build_stats_cards()
        self.build_main_content()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_periodo = self.build_filter_entry(row, "Periodo (mm/aaaa)", 160)
        self.entry_status = self.build_filter_entry(row, "Status", 160)
        self.entry_cpf = self.build_filter_entry(row, "CPF/CNPJ do interessado", 200)
        self.entry_processo = self.build_filter_entry(row, "No. do processo (TCCM)", 200)

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(btn_frame, "  Filtrar", carregar_icone("lupa.png"), self.filtrar,
                              fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                              text_color="white", border=False, bold=True)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)

    def build_stats_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=(0, 15))

        card_data = [
            ("Notas Fiscais Geral", "0"),
            ("Pendentes", "0"),
            ("Aprovadas", "0"),
            ("Rejeitadas", "0"),
            ("Valor Total (Periodo)", "R$ 0,00"),
        ]

        self.stat_labels = {}
        for i, (titulo, valor) in enumerate(card_data):
            card = ctk.CTkFrame(cards_frame, fg_color=COLORS["white"], corner_radius=4,
                                border_width=1, border_color=COLORS["border"])
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)

            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=FONTS["size_small"]),
                         text_color=COLORS["text_muted"], wraplength=120).pack(pady=(15, 5))
            lbl = ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=COLORS["text"])
            lbl.pack(pady=(0, 15))
            self.stat_labels[titulo] = lbl

    def build_main_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1)

        self.build_table_panel(content)
        self.build_detail_panel(content)

    def build_table_panel(self, parent):
        table_container = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=4,
                                       border_width=1, border_color=COLORS["border"])
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        parent.rowconfigure(0, weight=1)

        ctk.CTkLabel(table_container, text="Lista de Notas Fiscais",
                     font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(12, 5))

        columns = ("ID", "No. Processo (TCCM)", "Interessado", "CPF/CNPJ",
                   "No. Nota Fiscal", "Data Envio", "Valor Total (R$)",
                   "Itens Declarados", "Status", "Acoes")

        header = ctk.CTkFrame(table_container, fg_color=COLORS["table_header"], height=40, corner_radius=0)
        header.pack(fill="x", padx=3, pady=(1, 0))
        header.pack_propagate(False)

        cols_frame = ctk.CTkFrame(header, fg_color="transparent")
        cols_frame.pack(side="left", fill="x", expand=True, padx=(15, 0))

        weights = [1, 2, 2, 2, 2, 1, 2, 1, 1, 1]
        for i in range(len(columns) - 1):
            cols_frame.grid_columnconfigure(i, weight=weights[i])

        for i, col in enumerate(columns[:-1]):
            ctk.CTkLabel(cols_frame, text=col,
                         font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                         text_color=COLORS["text_muted"]).grid(row=0, column=i, sticky="w", padx=5)

        ctk.CTkLabel(header, text="Acoes",
                     font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                     text_color=COLORS["text_muted"], width=100).pack(side="right", padx=(0, 15))

        self.table_body = ctk.CTkScrollableFrame(table_container, fg_color=COLORS["white"],
                                                 corner_radius=0)
        self.table_body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.notas = self.carregar_do_banco()
        self.render_rows()

    def build_detail_panel(self, parent):
        detail_container = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=4,
                                        border_width=1, border_color=COLORS["border"])
        detail_container.grid(row=0, column=1, sticky="nsew")
        parent.rowconfigure(0, weight=1)

        ctk.CTkLabel(detail_container, text="Detalhes da Nota Fiscal",
                     font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=15, pady=(12, 10))

        self.info_frame = ctk.CTkFrame(detail_container, fg_color=COLORS["white"],
                                       corner_radius=4, border_width=1, border_color=COLORS["border"])
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))

        info_inner = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        info_inner.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(info_inner, text="Informacoes Gerais",
                     font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 5))

        self.info_labels = {}
        campos = ["No. Processo:", "No. Nota Fiscal:", "Interessado:", "CPF/CNPJ:",
                  "Data Envio:", "Valor Total:", "Total Devido:", "Total Pago:", "Status:"]
        for campo in campos:
            linha = ctk.CTkFrame(info_inner, fg_color="transparent")
            linha.pack(fill="x", pady=2)
            ctk.CTkLabel(linha, text=campo, font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                         text_color=COLORS["text_muted"], width=100, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(linha, text="--", font=ctk.CTkFont(size=FONTS["size_small"]),
                               text_color=COLORS["text"], anchor="w")
            lbl.pack(side="left")
            self.info_labels[campo] = lbl

        itens_frame = ctk.CTkFrame(detail_container, fg_color=COLORS["white"],
                                   corner_radius=4, border_width=1, border_color=COLORS["border"])
        itens_frame.pack(fill="x", padx=10, pady=(0, 10))

        itens_inner = ctk.CTkFrame(itens_frame, fg_color="transparent")
        itens_inner.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(itens_inner, text="Itens Declarados na Nota",
                     font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 5))

        self.itens_label = ctk.CTkLabel(itens_inner, text="Nenhum item selecionado",
                                        font=ctk.CTkFont(size=FONTS["size_small"]),
                                        text_color=COLORS["text_muted"])
        self.itens_label.pack(anchor="w")

        arquivos_frame = ctk.CTkFrame(detail_container, fg_color=COLORS["white"],
                                      corner_radius=4, border_width=1, border_color=COLORS["border"])
        arquivos_frame.pack(fill="x", padx=10, pady=(0, 10))

        arquivos_inner = ctk.CTkFrame(arquivos_frame, fg_color="transparent")
        arquivos_inner.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(arquivos_inner, text="Arquivos Anexados",
                     font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(arquivos_inner, text="Nenhum arquivo anexado",
                     font=ctk.CTkFont(size=FONTS["size_small"]),
                     text_color=COLORS["text_muted"]).pack(anchor="w")

        btn_frame = ctk.CTkFrame(detail_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkButton(btn_frame, text="Aprovar", height=36, corner_radius=4,
                      fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"], text_color="white",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      command=self.aprovar).pack(side="left", padx=(0, 5))

        ctk.CTkButton(btn_frame, text="Solicitar Correcao", height=36, corner_radius=4,
                      fg_color=COLORS["warning"], hover_color=COLORS["warning_hover"], text_color=COLORS["text"],
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      command=self.solicitar_correcao).pack(side="left", padx=(0, 5))

        ctk.CTkButton(btn_frame, text="Rejeitar", height=36, corner_radius=4,
                      fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                      text_color="white",
                      font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                      command=self.rejeitar).pack(side="left")

    def carregar_do_banco(self):
        try:
            with Database() as db:
                if not db.conexao:
                    return []
                sql = """SELECT nf.nota_fiscal, nf.data, nf.valor_total,
                                i.nome_infrator, i.cpf,
                                nf.processo, nf."agente ibama_matricula", nf.status_nota,
                                t.total_devido, t.total_pago,
                                COUNT(p.lote) as qtd_itens
                         FROM "nota fiscal" nf
                         JOIN tccm t ON nf.processo = t.processo
                         JOIN infrator i ON i.id_infrator = t."infrator_id_infrator"
                         LEFT JOIN produtos p ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                            AND p."nota fiscal_agente ibama_matricula" = nf."agente ibama_matricula"
                         GROUP BY nf.nota_fiscal, nf.data, nf.valor_total,
                                i.nome_infrator, i.cpf, nf.processo,
                                nf."agente ibama_matricula", nf.status_nota,
                                t.total_devido, t.total_pago"""
                try:
                    resultados = db.executar(sql)
                except Exception:
                    sql = """SELECT nf.nota_fiscal, nf.data, nf.valor_total,
                                    i.nome_infrator, i.cpf,
                                    nf.processo, nf."agente ibama_matricula", nf.status_nota
                             FROM "nota fiscal" nf
                             JOIN tccm t ON nf.processo = t.processo
                             JOIN infrator i ON i.id_infrator = t."infrator_id_infrator" """
                    try:
                        resultados = db.executar(sql)
                    except Exception:
                        return []

                notas = []
                if resultados:
                    for row in resultados.fetchall():
                        status = row[7] if len(row) > 7 and row[7] else "Pendente"
                        qtd_itens = row[10] if len(row) > 10 else 0
                        total_devido = float(row[8]) if len(row) > 8 and row[8] else 0
                        total_pago = float(row[9]) if len(row) > 9 and row[9] else 0
                        notas.append({
                            "nota_fiscal": row[0],
                            "data": _fmt_date(row[1]),
                            "valor_total": float(row[2]) if row[2] else 0,
                            "interessado": row[3],
                            "cpf": row[4],
                            "processo": row[5],
                            "matricula": row[6],
                            "status": status,
                            "itens": qtd_itens,
                            "total_devido": total_devido,
                            "total_pago": total_pago,
                        })
                return notas
        except Exception:
            return []

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for idx, nota in enumerate(self.notas, 1):
            self.adicionar_linha(idx, nota)

        self.atualizar_cards()

    def adicionar_linha(self, idx, nota):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=48)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

        cols = ctk.CTkFrame(linha, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

        weights = [1, 2, 2, 2, 2, 1, 2, 1, 1, 1]
        for i in range(9):
            cols.grid_columnconfigure(i, weight=weights[i])

        dados = [str(idx), nota["processo"], nota["interessado"], nota["cpf"],
                 nota["nota_fiscal"], nota["data"], f"R$ {nota['valor_total']:,.2f}",
                 str(nota["itens"]), nota["status"]]

        for i, valor in enumerate(dados):
            cor = COLORS["text"] if i == 0 else COLORS["text_muted"]
            ctk.CTkLabel(cols, text=valor,
                         font=ctk.CTkFont(size=FONTS["size_small"]),
                         text_color=cor, anchor="w").grid(row=0, column=i, sticky="w", padx=5)

        btn_frame = ctk.CTkFrame(linha, fg_color="transparent")
        btn_frame.pack(side="right", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="Ver", width=50, height=28, corner_radius=4,
                      fg_color=COLORS["white"], hover_color="#F0F0F0",
                      text_color=COLORS["text"], border_width=1, border_color=COLORS["border"],
                      font=ctk.CTkFont(size=11),
                      command=lambda n=nota: self.selecionar_nota(n)).pack(side="left", padx=2)

        linha.bind("<Button-1>", lambda e, n=nota: self.selecionar_nota(n))

    def selecionar_nota(self, nota):
        self.nf_selecionada = nota
        self.info_labels["No. Processo:"].configure(text=nota["processo"])
        self.info_labels["No. Nota Fiscal:"].configure(text=nota["nota_fiscal"])
        self.info_labels["Interessado:"].configure(text=nota["interessado"])
        self.info_labels["CPF/CNPJ:"].configure(text=nota["cpf"])
        self.info_labels["Data Envio:"].configure(text=nota["data"])
        self.info_labels["Valor Total:"].configure(text=f"R$ {nota['valor_total']:,.2f}")
        total_devido = nota.get("total_devido", 0)
        total_pago = nota.get("total_pago", 0)
        self.info_labels["Total Devido:"].configure(text=f"R$ {total_devido:,.2f}")
        self.info_labels["Total Pago:"].configure(text=f"R$ {total_pago:,.2f}")
        self.info_labels["Status:"].configure(text=nota["status"])
        self.itens_label.configure(text=f"{nota['itens']} itens declarados")

    def atualizar_cards(self):
        total = len(self.notas)
        pendentes = sum(1 for n in self.notas if n["status"] == "Pendente")
        aprovadas = sum(1 for n in self.notas if n["status"] == "Aprovada")
        rejeitadas = sum(1 for n in self.notas if n["status"] == "Rejeitada")
        valor_total = sum(n["valor_total"] for n in self.notas)

        self.stat_labels["Notas Fiscais Geral"].configure(text=str(total))
        self.stat_labels["Pendentes"].configure(text=str(pendentes))
        self.stat_labels["Aprovadas"].configure(text=str(aprovadas))
        self.stat_labels["Rejeitadas"].configure(text=str(rejeitadas))
        valor_fmt = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.stat_labels["Valor Total (Periodo)"].configure(text=valor_fmt)

    def _atualizar_status_nota(self, novo_status):
        if not self.nf_selecionada:
            return
        with Database() as db:
            if db.conexao:
                try:
                    nota_fiscal = self.nf_selecionada["nota_fiscal"]
                    matricula = self.nf_selecionada["matricula"]
                    processo = self.nf_selecionada["processo"]

                    sql_soma = """SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
                                 FROM produtos
                                 WHERE "nota fiscal_nota_fiscal" = ?
                                   AND "nota fiscal_agente ibama_matricula" = ?"""
                    r = db.executar(sql_soma, (nota_fiscal, matricula))
                    soma_produtos = float(r.fetchone()[0]) if r else 0

                    if soma_produtos > 0:
                        db.executar(
                            'UPDATE "nota fiscal" SET valor_total = ? WHERE nota_fiscal = ?',
                            (soma_produtos, nota_fiscal)
                        )

                    db.executar(
                        'UPDATE "nota fiscal" SET status_nota = ? WHERE nota_fiscal = ?',
                        (novo_status, nota_fiscal)
                    )

                    if novo_status == "Aprovada" and processo:
                        valor_adicionar = soma_produtos if soma_produtos > 0 else self.nf_selecionada["valor_total"]
                        sql_tccm = """UPDATE tccm
                                      SET total_pago = total_pago + ?,
                                          status = CASE
                                              WHEN (total_pago + ?) >= total_devido THEN 'concluido'
                                              ELSE 'pendente'
                                          END
                                      WHERE processo = ?"""
                        db.executar(sql_tccm, (valor_adicionar, valor_adicionar, processo))

                    db.commitar()
                except Exception:
                    pass
        self.nf_selecionada["status"] = novo_status
        self.notas = self.carregar_do_banco()
        self.render_rows()

    def filtrar(self):
        periodo = self.entry_periodo.get().strip().lower()
        status = self.entry_status.get().strip().lower()
        cpf = self.entry_cpf.get().strip().lower()
        processo = self.entry_processo.get().strip().lower()

        todos = self.carregar_do_banco()
        self.notas = [
            n for n in todos
            if (not processo or processo in n["processo"].lower())
            and (not cpf or cpf in n["cpf"].lower())
            and (not status or status in n["status"].lower())
            and (not periodo or periodo in n["data"])
        ]
        self.render_rows()

    def limpar_filtros(self):
        self.clear_entries(self.entry_periodo, self.entry_status, self.entry_cpf, self.entry_processo)
        self.notas = self.carregar_do_banco()
        self.render_rows()

    def aprovar(self):
        if not self.nf_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma nota fiscal primeiro.")
            return
        if messagebox.askyesno("Confirmar", "Deseja aprovar esta nota fiscal?"):
            self._atualizar_status_nota("Aprovada")
            messagebox.showinfo("Sucesso", "Nota fiscal aprovada com sucesso!")

    def solicitar_correcao(self):
        if not self.nf_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma nota fiscal primeiro.")
            return
        self._atualizar_status_nota("Correcao Solicitada")
        messagebox.showinfo("Informacao", "Solicitacao de correcao enviada.")

    def rejeitar(self):
        if not self.nf_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma nota fiscal primeiro.")
            return
        if messagebox.askyesno("Confirmar", "Deseja rejeitar esta nota fiscal?"):
            self._atualizar_status_nota("Rejeitada")
            messagebox.showinfo("Informacao", "Nota fiscal rejeitada.")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Monitoramento de Notas Fiscais")
    app.geometry("1400x800")
    app.configure(fg_color=COLORS["bg"])

    RelatoriosPage(app).pack(fill="both", expand=True)
    app.mainloop()
