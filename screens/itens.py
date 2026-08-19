import _path  # noqa: F401

from tkinter import messagebox

import customtkinter as ctk

from config.styles import COLORS, FONTS
from config.permissoes import pode_acao
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from services.itens_service import ItemService


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
        self.service = ItemService()

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
        itens = self.service.listar(
            self.processo_tccm,
            getattr(self, "semestre_option", "Todos") == "Semestre Atual",
        )
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
        self.itens = self.service.pesquisar(self._todos_os_itens, self.entry_busca.get())
        self.render_rows()

    def exportar_por_semestre(self):
        from tkinter import filedialog
        try:
            import openpyxl
            from openpyxl.styles import Font
        except Exception:
            messagebox.showerror("Erro", "Biblioteca openpyxl nao encontrada.", parent=self)
            return

        items, sem_list, quantities = self.service.listar_para_exportacao(self.processo_tccm)
        if not items:
            messagebox.showwarning("Atencao", "Nenhum item para exportar.", parent=self)
            return

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
                for a, b in sem_list:
                    v = quantities.get((it["id"], a, b), 0)
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
        self.service.excluir(item, self.usuario_logado)
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
