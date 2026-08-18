import _path  # noqa: F401

from tkinter import messagebox

import customtkinter as ctk

from config.styles import COLORS, FONTS
from config.permissoes import pode_acao
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from utils import registrar_log


class ItensPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, usuario_logado=None, processo_tccm=None,
                 perfil="admin", table_height=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.usuario_logado = usuario_logado
        self.processo_tccm = processo_tccm
        self.perfil = perfil
        self.table_height = table_height
        self.pode_editar = pode_acao(perfil, "gerenciar_itens")

        titulo = "Itens do TCCM" if processo_tccm else "Itens"
        subtitulo = f"Itens vinculados ao processo {processo_tccm}" if processo_tccm else "Cadastre, visualize, edite e exclua itens do sistema"
        self.build_header(titulo, subtitulo)
        self._build_filter_bar()
        self._build_table()

    def _build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        # semestre filter: Todos or Semestre Atual
        from datetime import datetime as _dt
        ano_atual = _dt.now().year
        self.semestre_option = "Todos"
        self.combo_semestre = ctk.CTkComboBox(
            row, values=["Todos", "Semestre Atual"], height=38, width=180,
            border_width=1, border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            command=lambda v: self._on_semestre_changed(v)
        )
        self.combo_semestre.pack(side="left", padx=(0, 10))
        try:
            self.combo_semestre.set("Todos")
        except Exception:
            pass

        self.entry_busca = self.build_search_entry(row, "Buscar por item, descricao ou tipo...", 340)

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        # export per-semester button
        self.build_action_btn(btn_frame, "  Exportar por Semestre", None, self.exportar_por_semestre)

        if self.pode_editar:
            self.build_action_btn(btn_frame, "  Novo Item", carregar_icone("mais.png"),
                                  self.abrir_formulario, fg_color=COLORS["primary"],
                                  hover_color=COLORS["primary_hover"], text_color="white",
                                  border=False, bold=True)

    def _on_semestre_changed(self, val):
        self.semestre_option = val
        # reload items with new semester filter
        self.itens = self.carregar_do_banco()
        self.render_rows()

    def _build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30), height=self.table_height)

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

        colunas = ["Item", "Tipo de Material", "Justificativa", "Unidade de Medida",
                   "Qtd. Prevista", "", "Qtd Entregue"]
        # pesos [3, 2, 3, 2] → relx / relwidth
        col_cfg = [
            (0.0,  0.22, "w"),      # Item
            (0.22, 0.14, "center"), # Tipo de Material
            (0.36, 0.22, "center"), # Justificativa
            (0.58, 0.11, "center"), # Unidade de Medida
            (0.69, 0.10, "center"), # Qtd. Prevista
            (0.79, 0.13, "center"), # barra de progresso
            (0.92, 0.08, "center"), # Qtd Entregue
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

        self.itens = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        with Database() as db:
            if not db.conexao:
                return []
            # Determine if semester filter is active
            semestre_range = None
            if getattr(self, 'semestre_option', 'Todos') == 'Semestre Atual':
                from datetime import datetime as _dt
                now = _dt.now()
                year = now.year
                if now.month <= 6:
                    inicio = f"{year}-01-01"
                    fim = f"{year}-06-30"
                    sem_num = 1
                else:
                    inicio = f"{year}-07-01"
                    fim = f"{year}-12-31"
                    sem_num = 2
                semestre_range = (inicio, fim)
                sem_year = year

            # Build SQL with optional semestre filtering for qtd_entregue
            def sum_subquery(sem_range=None):
                if sem_range:
                    return "COALESCE((SELECT SUM(p.quantidade) FROM produtos p JOIN \"nota fiscal\" nf ON p.\"nota fiscal_nota_fiscal\" = nf.nota_fiscal WHERE p.itens_id = i.id AND nf.data >= ? AND nf.data <= ?), 0)"
                else:
                    return "COALESCE((SELECT SUM(p.quantidade) FROM produtos p WHERE p.itens_id = i.id), 0)"

            if self.processo_tccm:
                try:
                    if semestre_range:
                        sql = (
                            "SELECT DISTINCT i.id, i.nome, i.descricao, i.tipo, i.justificativa, i.unidade_medida, "
                            "COALESCE((SELECT quantidade_prevista FROM item_semestre WHERE itens_id = i.id AND ano = ? AND semestre = ?), i.quantidade_prevista) as quantidade_prevista, "
                            + sum_subquery(semestre_range) + " "
                            "FROM itens i "
                            "WHERE i.processo = ? "
                            "   OR i.notas_fiscais IN ("
                            "  SELECT nf.nota_fiscal FROM \"nota fiscal\" nf WHERE nf.processo = ? AND nf.data >= ? AND nf.data <= ?"
                            ") ORDER BY i.id"
                        )
                        params = (sem_year, sem_num, semestre_range[0], semestre_range[1], self.processo_tccm, self.processo_tccm, semestre_range[0], semestre_range[1])
                    else:
                        sql = (
                            "SELECT DISTINCT i.id, i.nome, i.descricao, i.tipo, i.justificativa, i.unidade_medida, "
                            "i.quantidade_prevista, " + sum_subquery(None) + " "
                            "FROM itens i "
                            "WHERE i.processo = ? "
                            "   OR i.notas_fiscais IN ("
                            "  SELECT nf.nota_fiscal FROM \"nota fiscal\" nf WHERE nf.processo = ?"
                            ") ORDER BY i.id"
                        )
                        params = (self.processo_tccm, self.processo_tccm)
                    r = db.executar(sql, params)
                except Exception:
                    # fallback simple query
                    r = db.executar(
                        "SELECT DISTINCT i.id, i.nome, i.descricao, i.categoria, NULL, '', 0, 0 "
                        "FROM itens i "
                        "WHERE i.processo = ? "
                        "   OR i.notas_fiscais IN ("
                        "  SELECT nf.nota_fiscal FROM \"nota fiscal\" nf WHERE nf.processo = ?"
                        ") ORDER BY i.id",
                        (self.processo_tccm, self.processo_tccm)
                    )
            else:
                try:
                    if semestre_range:
                        sql = (
                            "SELECT id, nome, descricao, tipo, justificativa, unidade_medida, "
                            "COALESCE((SELECT quantidade_prevista FROM item_semestre WHERE itens_id = itens.id AND ano = ? AND semestre = ?), quantidade_prevista) as quantidade_prevista, "
                            + sum_subquery(semestre_range) +
                            " FROM itens ORDER BY id"
                        )
                        params = (sem_year, sem_num, semestre_range[0], semestre_range[1])
                        r = db.executar(sql, params)
                    else:
                        sql = (
                            "SELECT id, nome, descricao, tipo, justificativa, unidade_medida, quantidade_prevista, "
                            + sum_subquery(None) +
                            " FROM itens ORDER BY id"
                        )
                        r = db.executar(sql)
                except Exception:
                    r = db.executar(
                        "SELECT id, nome, descricao, categoria, NULL, '', 0, 0 "
                        "FROM itens ORDER BY id"
                    )

            itens = []
            if r:
                for row in r.fetchall():
                    itens.append(dict(
                        id=row[0],
                        nome=row[1] or "-",
                        descricao=row[2] or "-",
                        tipo=row[3] or "-",
                        justificativa=row[4] or "",
                        unidade_medida=row[5] or "",
                        quantidade_prevista=row[6] or 0,
                        qtd_entregue=row[7] or 0,
                    ))
            self._todos_os_itens = itens[:]
            return itens

    def render_rows(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        for item in self.itens:
            self._add_row(item)

    def _add_row(self, item):
        linha, data, _ = self.add_data_row(has_checkbox=False)

        # pesos [3, 2, 3, 2] → relx / relwidth (idêntico ao cabeçalho)
        col_cfg = [
            (0.0,  0.22, "w"),      # Item
            (0.22, 0.14, "center"), # Tipo de Material
            (0.36, 0.22, "center"), # Justificativa
            (0.58, 0.11, "center"), # Unidade de Medida
            (0.69, 0.10, "center"), # Qtd. Prevista
            (0.79, 0.13, "center"), # barra de progresso
            (0.92, 0.08, "center"), # Qtd Entregue
        ]

        just = item.get("justificativa", "")
        just_text = (just[:60] + "...") if len(just) > 60 else just

        try:
            prevista = float(item.get("quantidade_prevista", 0) or 0)
        except Exception:
            prevista = 0.0
        try:
            entregue = float(item.get("qtd_entregue", 0) or 0)
        except Exception:
            entregue = 0.0
        progresso = 0.0
        if prevista > 0:
            progresso = min(max(entregue / prevista, 0.0), 1.0)

        valores = [
            item["nome"],
            item["tipo"],
            just_text or "-",
            item.get("unidade_medida", "") or "-",
            str(prevista),
            "",
            str(entregue),
        ]

        for (rx, rw, anchor), texto in zip(col_cfg, valores):
            if anchor == "w":
                ctk.CTkLabel(
                    data, text=texto,
                    font=ctk.CTkFont(size=FONTS["size_body"]),
                    text_color=COLORS["text"] if rx == 0 else COLORS["text_muted"],
                    anchor=anchor,
                ).place(relx=rx, relwidth=rw, rely=0, relheight=1)
            elif rx == 0.79:
                bar = ctk.CTkProgressBar(
                    data, progress_color=COLORS["success_dark"],
                    fg_color=COLORS["border"], height=8, corner_radius=4,
                )
                bar.place(relx=rx + 0.02, relwidth=rw - 0.04, rely=0.42, relheight=0.16)
                bar.set(progresso)
            else:
                ctk.CTkLabel(
                    data, text=texto,
                    font=ctk.CTkFont(size=FONTS["size_body"]),
                    text_color=COLORS["text_muted"],
                    anchor=anchor,
                ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        acoes = [("\U0001f441", lambda i=item: self.visualizar(i))]
        if self.pode_editar:
            acoes += [
                ("\u270f", lambda i=item: self.editar(i)),
                ("\U0001f5d1", lambda i=item: self.excluir(i)),
            ]
        self.add_action_buttons(linha, acoes)

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        if not busca:
            self.itens = self._todos_os_itens[:]
        else:
            self.itens = [
                i for i in self._todos_os_itens
                if busca in i["nome"].lower()
                or busca in i["descricao"].lower()
                or busca in i["tipo"].lower()
                or busca in i.get("justificativa", "").lower()
                or busca in i.get("unidade_medida", "").lower()
            ]
        self.render_rows()

    def exportar_por_semestre(self):
        from tkinter import filedialog
        try:
            import openpyxl
            from openpyxl.styles import Font
        except Exception:
            messagebox.showerror("Erro", "Biblioteca openpyxl nao encontrada.", parent=self)
            return

        # load items (respecting current processo_tccm if set)
        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco.", parent=self)
                return
            try:
                if self.processo_tccm:
                    r = db.executar("SELECT id, nome, descricao, tipo, justificativa, unidade_medida FROM itens WHERE processo = ? ORDER BY id", (self.processo_tccm,))
                else:
                    r = db.executar("SELECT id, nome, descricao, tipo, justificativa, unidade_medida FROM itens ORDER BY id")
                items = [dict(id=row[0], nome=row[1], descricao=row[2], tipo=row[3], justificativa=row[4], unidade_medida=row[5]) for row in (r.fetchall() if r else [])]
            except Exception:
                items = []

            if not items:
                messagebox.showwarning("Atencao", "Nenhum item para exportar.", parent=self)
                return

            ids = [i["id"] for i in items]
            # collect distinct semesters
            q_marks = ",".join("?" for _ in ids)
            sem_rows = db.executar(f"SELECT DISTINCT ano, semestre FROM item_semestre WHERE itens_id IN ({q_marks}) ORDER BY ano, semestre", tuple(ids))
            sems = sem_rows.fetchall() if sem_rows else []
            sem_list = [(r[0], r[1]) for r in sems]

            # map (itens_id -> {(ano,sem): qty})
            sem_map = {}
            if ids:
                rows = db.executar(f"SELECT itens_id, ano, semestre, quantidade_prevista FROM item_semestre WHERE itens_id IN ({q_marks})", tuple(ids))
                if rows:
                    for r in rows.fetchall():
                        iid, ano, sem, q = r[0], r[1], r[2], r[3]
                        sem_map.setdefault(iid, {})[(ano, sem)] = q

        caminho = filedialog.asksaveasfilename(title="Exportar itens por semestre", defaultextension=".xlsx", filetypes=[("Planilha Excel", "*.xlsx")], initialfile="itens_por_semestre.xlsx")
        if not caminho:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Itens por Semestre"
            # headers
            base_headers = ["Nome", "Descricao", "Tipo", "Justificativa", "Unidade de Medida", "Total Prevista"]
            sem_headers = [f"{a}-S{b}" for a, b in sem_list]
            headers = base_headers + sem_headers
            ws.append(headers)
            for cel in ws[1]:
                cel.font = Font(bold=True)

            for it in items:
                row = [it.get("nome"), it.get("descricao"), it.get("tipo"), it.get("justificativa"), it.get("unidade_medida")] 
                totals = 0
                row_sem = []
                m = sem_map.get(it["id"], {})
                for a, b in sem_list:
                    v = m.get((a, b), 0)
                    row_sem.append(v)
                    totals += (v or 0)
                row = row + [totals] + row_sem
                ws.append(row)
            wb.save(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {e}", parent=self)
            return

        messagebox.showinfo("Sucesso", f"Planilha exportada: {caminho}", parent=self)

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.itens = self._todos_os_itens[:]
        self.render_rows()

    def _inserir_item_db(self, db, data, codigo_interno=None):
        if codigo_interno is None:
            c = db.executar("SELECT COALESCE(MAX(id), 0) + 1 FROM itens")
            nid = c.fetchone()[0] if c else 1
            codigo_interno = f"IT-{nid:03d}"
        db.executar(
            "INSERT INTO itens (nome, descricao, codigo_interno, tipo, justificativa, unidade_medida, quantidade_prevista, status, processo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data.get("nome", "")[:200],
                data.get("descricao", "")[:200],
                codigo_interno,
                data.get("tipo", ""),
                data.get("justificativa", ""),
                data.get("unidade_medida", ""),
                data.get("quantidade_prevista", 0),
                "Ativo",
                data.get("processo"),
            ),
        )
        # try to persist per-semester quantidade
        try:
            cur = db.executar("SELECT last_insert_rowid()")
            lr = cur.fetchone()
            item_id = int(lr[0]) if lr else None
            if item_id:
                from datetime import datetime as _dt
                now = _dt.now()
                ano = now.year
                semestre = 1 if now.month <= 6 else 2
                db.executar(
                    "INSERT OR REPLACE INTO item_semestre (itens_id, ano, semestre, quantidade_prevista, processo) VALUES (?, ?, ?, ?, ?)",
                    (item_id, ano, semestre, data.get("quantidade_prevista", 0), data.get("processo")),
                )
        except Exception:
            pass
        db.commitar()

    def _inserir_item(self, data, codigo_interno=None):
        with Database() as db:
            if not db.conexao:
                return False
            self._inserir_item_db(db, data, codigo_interno)
        return True

    def _atualizar_item(self, item_id, data):
        with Database() as db:
            if not db.conexao:
                return False
            db.executar(
                "UPDATE itens SET nome=?, descricao=?, tipo=?, justificativa=?, unidade_medida=?, quantidade_prevista=? WHERE id=?",
                (
                    data.get("nome", "")[:200],
                    data.get("descricao", "")[:200],
                    data.get("tipo", ""),
                    data.get("justificativa", ""),
                    data.get("unidade_medida", ""),
                    data.get("quantidade_prevista", 0),
                    item_id,
                ),
            )
            # update per-semester table for current semester
            try:
                from datetime import datetime as _dt
                now = _dt.now()
                ano = now.year
                semestre = 1 if now.month <= 6 else 2
                db.executar(
                    "INSERT OR REPLACE INTO item_semestre (itens_id, ano, semestre, quantidade_prevista, processo) VALUES (?, ?, ?, ?, ?)",
                    (item_id, ano, semestre, data.get("quantidade_prevista", 0), data.get("processo")),
                )
            except Exception:
                pass
            db.commitar()
        return True

    def abrir_formulario(self, item=None):
        from screens.cadastrar_itens import CadastrarItensWindow
        janela = CadastrarItensWindow(self, item=item, processo_tccm=self.processo_tccm,
                                      usuario_logado=self.usuario_logado)
        self.wait_window(janela)
        self.itens = self.carregar_do_banco()
        self.render_rows()

    def visualizar(self, item):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Item #{item['id']}")
        modal.geometry("550x400")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=25, pady=20)

        campos = [
            ("No.", str(item["id"])),
            ("Item", item.get("nome", "-")),
            ("Tipo de Material", item.get("tipo", "-")),
            ("Descricao", item.get("descricao", "-")),
            ("Justificativa", item.get("justificativa", "-") or "-"),
            ("Unidade de Medida", item.get("unidade_medida", "") or "-"),
        ]
        for i, (l, v) in enumerate(campos):
            ctk.CTkLabel(
                frame, text=f"{l}:",
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            ).grid(row=i, column=0, sticky="w", pady=3, padx=(0, 10))
            ctk.CTkLabel(
                frame, text=v,
                text_color=COLORS["text_muted"],
                wraplength=380,
            ).grid(row=i, column=1, sticky="w", pady=3)

        ctk.CTkButton(
            modal, text="Fechar", height=34, width=100,
            fg_color=COLORS["border"], hover_color="#C0C0C0",
            text_color=COLORS["text"], command=modal.destroy,
        ).pack(pady=(15, 10))

    def editar(self, item):
        self.abrir_formulario(item=item)

    def excluir(self, item):
        if not messagebox.askyesno("Excluir", f"Deseja excluir o item \"{item['nome']}\"?"):
            return
        with Database() as db:
            if db.conexao:
                db.executar("DELETE FROM itens WHERE id = ?", (item["id"],))
                db.commitar()
        registrar_log(self.usuario_logado or "Sistema", "exclusao", "itens", f"Item '{item['nome']}' (ID: {item['id']}) excluido")
        self.itens = self.carregar_do_banco()
        self.render_rows()

    def voltar(self):
        if self.on_voltar:
            self.on_voltar()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("FISCSOFT - Itens")
    app.configure(fg_color=COLORS["bg"])
    app.after(0, app.state, "zoomed")
    ItensPage(app).pack(fill="both", expand=True)
    app.mainloop()
