import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from config.styles import COLORS, FONTS
from conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone


class ItensPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self._garantir_colunas_db()
        self.build_header("Itens", "Cadastre, visualize, edite e exclua itens do sistema")
        self._build_filter_bar()
        self._build_table()

    def _garantir_colunas_db(self):
        db = Database()
        if db.conectar():
            for sql in [
                "ALTER TABLE itens ADD COLUMN justificativa TEXT DEFAULT NULL",
                "ALTER TABLE itens ADD COLUMN unidade_medida VARCHAR(50) DEFAULT NULL",
            ]:
                try:
                    db.executar(sql)
                except:
                    pass
            db.commitar()
            db.desconectar()

    def _build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(row, "Buscar por item, descricao ou tipo...", 340)

        btn_frame = self.build_btn_frame(row)
        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        self.build_action_btn(btn_frame, "  Importar Excel", carregar_icone("mais.png"),
                              self.importar_excel)
        self.build_action_btn(btn_frame, "  Novo Item", carregar_icone("mais.png"),
                              self.abrir_formulario, fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"], text_color="white",
                              border=False, bold=True)

    def _build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))
        self.build_table_header(self.table_frame,
                                ["Item", "Tipo de Material", "Justificativa", "Unidade de Medida"],
                                [3, 2, 3, 2], has_checkbox=True)

        self.itens = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_excel(self, caminho):
        try:
            ext = Path(caminho).suffix.lower()
            engine = "odf" if ext == ".ods" else "openpyxl" if ext == ".xlsx" else None
            if not engine:
                raise ValueError(f"Formato n\u00e3o suportado: {ext}")
            df = pd.read_excel(caminho, engine=engine, sheet_name=0)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")
            return []

        col_map = {c.replace('\xa0', ' ').strip(): c for c in df.columns}
        itens = []

        for idx, row in df.iterrows():
            def get(col, d=None):
                c = col_map.get(col)
                if c is None:
                    return d
                v = row.get(c)
                return d if pd.isna(v) else v

            nome = get("ITEM") or get("DESCRI\u00c7\u00c3O") or "-"
            itens.append(dict(
                nome=str(nome)[:200],
                descricao=str(get("DESCRI\u00c7\u00c3O") or nome)[:200],
                tipo=str(get("TIPO DE MATERIAL") or ""),
                justificativa=str(get("JUSTIFICATIVA") or ""),
                unidade_medida=str(get("Unidade de Medida") or ""),
            ))
        return itens

    def carregar_do_banco(self):
        db = Database()
        if not db.conectar():
            return []
        try:
            r = db.executar(
                "SELECT id, nome, descricao, tipo, justificativa, unidade_medida "
                "FROM itens ORDER BY id"
            )
        except:
            r = db.executar(
                "SELECT id, nome, descricao, categoria, NULL, '' "
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
                ))
        db.desconectar()
        self._todos_os_itens = itens[:]
        return itens

    def render_rows(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        for item in self.itens:
            self._add_row(item)

    def _add_row(self, item):
        linha, data, _ = self.add_data_row()
        self.configure_data_columns(data, [3, 2, 3, 2])

        ctk.CTkLabel(data, text=item["nome"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w",
                      ).grid(row=0, column=0, sticky="w", padx=5)

        ctk.CTkLabel(data, text=item["tipo"],
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text_muted"], anchor="w",
                      ).grid(row=0, column=1, sticky="w", padx=5)

        just = item.get("justificativa", "")
        just_text = (just[:60] + "...") if len(just) > 60 else just
        ctk.CTkLabel(data, text=just_text or "-",
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text_muted"], anchor="w",
                      ).grid(row=0, column=2, sticky="w", padx=5)

        ctk.CTkLabel(data, text=item.get("unidade_medida", "") or "-",
                      font=ctk.CTkFont(size=FONTS["size_body"]),
                      text_color=COLORS["text"], anchor="w",
                      ).grid(row=0, column=3, sticky="w", padx=5)

        self.add_action_buttons(linha, [
            ("\U0001f441", lambda i=item: self.visualizar(i)),
            ("\u270f", lambda i=item: self.editar(i)),
            ("\U0001f5d1", lambda i=item: self.excluir(i)),
        ])

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

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.itens = self._todos_os_itens[:]
        self.render_rows()

    def importar_excel(self):
        caminho = Path(__file__).resolve().parent.parent / "telaitens.xlsx"
        if not caminho.exists():
            messagebox.showerror("Erro", f"Arquivo n\u00e3o encontrado:\n{caminho}")
            return

        itens_excel = self.carregar_do_excel(str(caminho))
        if not itens_excel:
            return

        db = Database()
        if not db.conectar():
            return
        db.executar("DELETE FROM itens")
        db.commitar()
        db.desconectar()

        for i, item in enumerate(itens_excel):
            self._inserir_item(item, codigo_interno=f"IT-{i+1:03d}")

        self.itens = self.carregar_do_banco()
        self.render_rows()
        messagebox.showinfo(
            "Sucesso",
            f"'{caminho.name}' carregado com {len(self.itens)} itens."
        )

    def _inserir_item(self, data, codigo_interno=None):
        db = Database()
        if not db.conectar():
            return False
        if codigo_interno is None:
            c = db.executar("SELECT COALESCE(MAX(id), 0) + 1 FROM itens")
            nid = c.fetchone()[0] if c else 1
            codigo_interno = f"IT-{nid:03d}"
        db.executar(
            "INSERT INTO itens (nome, descricao, codigo_interno, tipo, justificativa, unidade_medida, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                data.get("nome", "")[:200],
                data.get("descricao", "")[:200],
                codigo_interno,
                data.get("tipo", ""),
                data.get("justificativa", ""),
                data.get("unidade_medida", ""),
                "Ativo",
            ),
        )
        db.commitar()
        db.desconectar()
        return True

    def _atualizar_item(self, item_id, data):
        db = Database()
        if not db.conectar():
            return False
        db.executar(
            "UPDATE itens SET nome=%s, descricao=%s, tipo=%s, justificativa=%s, unidade_medida=%s WHERE id=%s",
            (
                data.get("nome", "")[:200],
                data.get("descricao", "")[:200],
                data.get("tipo", ""),
                data.get("justificativa", ""),
                data.get("unidade_medida", ""),
                item_id,
            ),
        )
        db.commitar()
        db.desconectar()
        return True

    def abrir_formulario(self, item=None):
        editando = item is not None
        modal = ctk.CTkToplevel(self)
        modal.title(f"{'Editar' if editando else 'Novo'} Item")
        modal.geometry("550x520")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text=f"{'Editar' if editando else 'Cadastrar Novo'} Item",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"],
        ).pack(pady=(20, 15))

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(padx=30, fill="x")

        campos = ["Nome do Item", "Descri\u00e7\u00e3o", "Tipo de Material", "Justificativa", "Unidade de Medida"]
        entries = {}
        for label in campos:
            ctk.CTkLabel(
                frame, text=label,
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            ).pack(fill="x", pady=(8, 2))
            e = ctk.CTkEntry(
                frame, height=36, corner_radius=4,
                fg_color=COLORS["white"], border_width=1, border_color=COLORS["border"],
            )
            e.pack(fill="x")
            entries[label] = e

        if editando:
            entries["Nome do Item"].insert(0, item.get("nome", ""))
            entries["Descri\u00e7\u00e3o"].insert(0, item.get("descricao", ""))
            entries["Tipo de Material"].insert(0, item.get("tipo", ""))
            entries["Justificativa"].insert(0, item.get("justificativa", ""))
            entries["Unidade de Medida"].insert(0, item.get("unidade_medida", ""))

        def salvar():
            nome = entries["Nome do Item"].get().strip()
            if not nome:
                return messagebox.showwarning("Aviso", "Nome do Item \u00e9 obrigat\u00f3rio!", parent=modal)
            data = dict(
                nome=nome,
                descricao=entries["Descri\u00e7\u00e3o"].get().strip() or nome,
                tipo=entries["Tipo de Material"].get().strip(),
                justificativa=entries["Justificativa"].get().strip(),
                unidade_medida=entries["Unidade de Medida"].get().strip(),
            )
            if editando:
                self._atualizar_item(item["id"], data)
            else:
                self._inserir_item(data)
            modal.destroy()
            self.itens = self.carregar_do_banco()
            self.render_rows()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 5))
        ctk.CTkButton(
            btn_frame, text="Salvar",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=salvar,
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            btn_frame, text="Cancelar",
            height=40, corner_radius=4,
            fg_color=COLORS["white"], hover_color="#F0F0F0",
            text_color=COLORS["text_muted"], border_width=1, border_color=COLORS["border"],
            command=modal.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

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
            ("N\u00ba", str(item["id"])),
            ("Item", item.get("nome", "-")),
            ("Tipo de Material", item.get("tipo", "-")),
            ("Descri\u00e7\u00e3o", item.get("descricao", "-")),
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
        db = Database()
        if db.conectar():
            db.executar("DELETE FROM itens WHERE id = %s", (item["id"],))
            db.commitar()
            db.desconectar()
        self.itens = self.carregar_do_banco()
        self.render_rows()

    def voltar(self):
        self.on_voltar() if self.on_voltar else self.master.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("FISCSOFT - Itens")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])
    ItensPage(app).pack(fill="both", expand=True)
    app.mainloop()
