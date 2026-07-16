import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.sidebar import carregar_icone
from utils import registrar_log


class LocaisPage(CrudBase, ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.locais = []
        self.local_edicao = None

        self.build_header("Locais Cadastrados", "Gerencie os locais de destino de materiais")
        self.build_filter_bar()
        self.build_table()

    def build_filter_bar(self):
        inner = self.build_filter_container()
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self.entry_busca = self.build_search_entry(row, "Buscar por instituicao, endereco ou CEP...", 400)

        btn_frame = self.build_btn_frame(row)

        self.build_action_btn(btn_frame, "  Pesquisar", carregar_icone("lupa.png"), self.pesquisar)
        self.build_action_btn(btn_frame, "  Limpar", carregar_icone("apagar.png"), self.limpar_filtros)
        self.build_action_btn(btn_frame, "  Novo Local", carregar_icone("mais.png"),
                              self.novo_local, fg_color=COLORS["primary"],
                              hover_color=COLORS["primary_hover"], text_color="white",
                              border=False, bold=True)

    def build_table(self):
        CrudBase.build_table(self, pad_y=(0, 30))

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

        colunas = ["CEP", "Endereco", "Instituicao", "Responsavel", "Telefone"]
        col_cfg = [
            (0.0, 0.15, "w"),    # CEP
            (0.15, 0.25, "w"),   # Endereco
            (0.40, 0.25, "w"),   # Instituicao
            (0.65, 0.20, "w"),   # Responsavel
            (0.85, 0.15, "w"),   # Telefone
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

        self.locais = self.carregar_do_banco()
        self.render_rows()

    def carregar_do_banco(self):
        with Database() as db:
            if not db.conexao:
                return []
            sql = """SELECT id, cep, endereco, instituicao, responsavel, telefone
                     FROM locais ORDER BY id"""
            resultados = db.executar(sql)
            locais = []
            if resultados:
                for row in resultados.fetchall():
                    locais.append({
                        "id": row[0],
                        "cep": row[1],
                        "endereco": row[2],
                        "instituicao": row[3],
                        "responsavel": row[4],
                        "telefone": row[5] or "-",
                    })
            return locais

    def render_rows(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for local in self.locais:
            self._add_row(local)

    def _add_row(self, local):
        linha, data, _ = self.add_data_row(has_checkbox=False)

        # pesos → relx / relwidth (idêntico ao cabeçalho)
        col_cfg = [
            (0.0,  0.15, "w"),      # CEP
            (0.15, 0.25, "w"),      # Endereco
            (0.40, 0.25, "w"),      # Instituicao
            (0.65, 0.20, "w"),      # Responsavel
            (0.85, 0.15, "w"),      # Telefone
        ]

        endereco = local["endereco"][:40] + ("..." if len(local["endereco"]) > 40 else "")

        valores = [
            local["cep"],
            endereco,
            local["instituicao"],
            local["responsavel"],
            local["telefone"],
        ]

        for (rx, rw, anchor), texto in zip(col_cfg, valores):
            ctk.CTkLabel(
                data, text=texto,
                font=ctk.CTkFont(size=FONTS["size_body"]),
                text_color=COLORS["text"] if anchor == "w" else COLORS["text_muted"],
                anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        self.add_action_buttons(linha, [
            ("\U0001f441", lambda l=local: self.visualizar_local(l)),
            ("\u270f", lambda l=local: self.editar_local(l)),
            ("\U0001f5d1", lambda l=local: self.excluir(l)),
        ])

    def novo_local(self):
        self.local_edicao = None
        self._abrir_formulario()

    def visualizar_local(self, local):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Local #{local['id']}")
        modal.geometry("450x350")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=25, pady=20)

        campos = [
            ("CEP", local.get("cep", "-")),
            ("Endereco", local.get("endereco", "-")),
            ("Instituicao", local.get("instituicao", "-")),
            ("Responsavel", local.get("responsavel", "-")),
            ("Telefone", local.get("telefone", "-")),
        ]
        for i, (l, v) in enumerate(campos):
            ctk.CTkLabel(
                frame, text=f"{l}:",
                font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            ).grid(row=i, column=0, sticky="w", pady=3, padx=(0, 10))
            ctk.CTkLabel(
                frame, text=v,
                text_color=COLORS["text_muted"],
                wraplength=300,
            ).grid(row=i, column=1, sticky="w", pady=3)

        ctk.CTkButton(
            modal, text="Fechar", height=34, width=100,
            fg_color=COLORS["border"], hover_color="#C0C0C0",
            text_color=COLORS["text"], command=modal.destroy,
        ).pack(pady=(15, 10))

    def editar_local(self, local):
        self.local_edicao = local
        self._abrir_formulario()

    def excluir(self, local):
        if messagebox.askyesno("Excluir", f"Deseja excluir o local da {local['instituicao']}?"):
            with Database() as db:
                if db.conexao:
                    db.executar(
                        "DELETE FROM locais WHERE id = ?",
                        (local["id"],)
                    )
                    db.commitar()
            registrar_log(
                self.usuario_logado or "Sistema",
                "exclusao",
                "locais",
                f"Local '{local['instituicao']}' (ID: {local['id']}) excluido"
            )
            self.locais = self.carregar_do_banco()
            self.render_rows()

    def pesquisar(self):
        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self.locais = self.carregar_do_banco()
        else:
            self.locais = [
                l for l in self.carregar_do_banco()
                if termo in l["instituicao"].lower()
                or termo in l["endereco"].lower()
                or termo in l["cep"].lower()
                or termo in l["responsavel"].lower()
            ]
        self.render_rows()

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.locais = self.carregar_do_banco()
        self.render_rows()

    def _abrir_formulario(self):
        form = ctk.CTkToplevel(self)
        form.title("Novo Local" if not self.local_edicao else "Editar Local")
        form.geometry("500x400")
        form.configure(fg_color=COLORS["bg"])
        form.transient(self.winfo_toplevel())
        form.grab_set()

        container = ctk.CTkFrame(form, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            container,
            text="Cadastrar Local de Destino" if not self.local_edicao else "Editar Local",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 20))

        fields = [
            ("CEP", "cep", "00000-000"),
            ("Endereco Completo", "endereco", "Rua, numero, bairro, cidade-UF"),
            ("Instituicao", "instituicao", "Nome da instituicao"),
            ("Responsavel", "responsavel", "Nome do responsavel"),
            ("Telefone", "telefone", "(00) 00000-0000"),
        ]

        entries = {}
        for label_text, key, placeholder in fields:
            ctk.CTkLabel(
                container, text=label_text,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                text_color=COLORS["text_muted"],
            ).pack(anchor="w", pady=(10, 2))

            entry = ctk.CTkEntry(
                container,
                placeholder_text=placeholder,
                height=38, border_width=1,
                border_color=COLORS["border"], corner_radius=4,
                fg_color=COLORS["white"], text_color=COLORS["text"],
            )
            entry.pack(fill="x")
            entries[key] = entry

        if self.local_edicao:
            entries["cep"].insert(0, self.local_edicao["cep"])
            entries["endereco"].insert(0, self.local_edicao["endereco"])
            entries["instituicao"].insert(0, self.local_edicao["instituicao"])
            entries["responsavel"].insert(0, self.local_edicao["responsavel"])
            if self.local_edicao["telefone"] and self.local_edicao["telefone"] != "-":
                entries["telefone"].insert(0, self.local_edicao["telefone"])

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        def salvar():
            cep = entries["cep"].get().strip()
            endereco = entries["endereco"].get().strip()
            instituicao = entries["instituicao"].get().strip()
            responsavel = entries["responsavel"].get().strip()
            telefone = entries["telefone"].get().strip()

            if not all([cep, endereco, instituicao, responsavel]):
                messagebox.showwarning("Aviso", "Preencha CEP, Endereco, Instituicao e Responsavel.")
                return

            with Database() as db:
                if not db.conexao:
                    messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")
                    return

                if self.local_edicao:
                    sql = """UPDATE locais SET cep=?, endereco=?, instituicao=?, responsavel=?, telefone=?
                             WHERE id=?"""
                    params = (cep, endereco, instituicao, responsavel, telefone or None, self.local_edicao["id"])
                    mensagem = "Local atualizado com sucesso!"
                else:
                    sql = """INSERT INTO locais (cep, endereco, instituicao, responsavel, telefone)
                             VALUES (?, ?, ?, ?, ?)"""
                    params = (cep, endereco, instituicao, responsavel, telefone or None)
                    mensagem = "Local cadastrado com sucesso!"

                db.executar(sql, params)
                db.commitar()

            registrar_log(
                self.usuario_logado or "Sistema",
                "edicao" if self.local_edicao else "cadastro",
                "locais",
                mensagem
            )

            messagebox.showinfo("Sucesso", mensagem)
            form.destroy()
            self.locais = self.carregar_do_banco()
            self.render_rows()

        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40, corner_radius=4,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=form.destroy,
        ).pack(side="left")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Locais Cadastrados")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    LocaisPage(app).pack(fill="both", expand=True)
    app.mainloop()
