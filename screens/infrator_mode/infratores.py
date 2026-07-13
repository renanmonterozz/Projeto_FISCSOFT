import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from config.styles import COLORS, FONTS, ASSETS_DIR
from database.conexaodb import Database


class InfratoresPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])

        self.build_header()
        self.build_filter_bar()
        self.build_table()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header,
            text="Agentes IBAMA",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Gerencie os infratores cadastrados no sistema",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def build_filter_bar(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=8,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="x", padx=30, pady=(0, 20))

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        busca_container = ctk.CTkFrame(
            row, fg_color=COLORS["white"], border_width=1,
            border_color=COLORS["border"], corner_radius=6
        )
        busca_container.pack(side="left", padx=(0, 10))

        self.entry_busca = ctk.CTkEntry(
            busca_container,
            placeholder_text="Buscar por nome, CPF ou email...",
            width=340, height=38,
            border_width=0, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_busca.pack(side="left", padx=(12, 4), pady=2)

        try:
            lupa_busca_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                size=(18, 18),
            )
        except Exception:
            lupa_busca_icon = None

        ctk.CTkLabel(
            busca_container, image=lupa_busca_icon, text="",
        ).pack(side="right", padx=(0, 10))

        self.entry_filtro1 = ctk.CTkEntry(
            row,
            placeholder_text="Email",
            width=200, height=38,
            border_width=1, border_color=COLORS["border"],
            corner_radius=6, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_filtro1.pack(side="left", padx=(0, 10))

        self.entry_filtro2 = ctk.CTkEntry(
            row,
            placeholder_text="Telefone",
            width=200, height=38,
            border_width=1, border_color=COLORS["border"],
            corner_radius=6, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_filtro2.pack(side="left", padx=(0, 10))

        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="left", padx=(5, 0))

        try:
            lupa_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "lupa.png")),
                size=(18, 18),
            )
        except Exception:
            lupa_icon = None

        ctk.CTkButton(
            btn_frame,
            image=lupa_icon,
            text="  Pesquisar",
            height=38, corner_radius=6,
            fg_color=COLORS["white"], hover_color="#F0F0F0",
            text_color=COLORS["text"],
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"], weight="normal"),
            compound="left",
            command=self.pesquisar,
        ).pack(side="left", padx=(0, 8))

        try:
            apagar_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "apagar.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "apagar.png")),
                size=(18, 18),
            )
        except Exception:
            apagar_icon = None

        ctk.CTkButton(
            btn_frame,
            image=apagar_icon,
            text="  Limpar",
            height=38, corner_radius=6,
            fg_color=COLORS["white"], hover_color="#F0F0F0",
            text_color=COLORS["text"],
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"], weight="normal"),
            compound="left",
            command=self.limpar_filtros,
        ).pack(side="left", padx=(0, 8))

        try:
            mais_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "mais.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "mais.png")),
                size=(18, 18),
            )
        except Exception:
            mais_icon = None

        ctk.CTkButton(
            btn_frame,
            image=mais_icon,
            text="  Novo Infrator",
            height=38, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            compound="left",
            command=self.novo_infrator,
        ).pack(side="left")

    def build_table(self):
        self.table_frame = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=8,
            border_width=1, border_color=COLORS["border"]
        )
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        header = ctk.CTkFrame(
            self.table_frame, fg_color="#FAFAFA",
            height=44, corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="", width=40).pack(side="left", padx=(15, 0))

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(5, 20))
        cols.grid_columnconfigure(0, weight=3)
        cols.grid_columnconfigure(1, weight=2)
        cols.grid_columnconfigure(2, weight=2)
        cols.grid_columnconfigure(3, weight=2)

        for col_text in ["Nome", "CPF", "Email", "Telefone"]:
            ctk.CTkLabel(
                cols, text=col_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=["Nome", "CPF", "Email", "Telefone"].index(col_text), sticky="w")

        ctk.CTkLabel(
            header, text="Acoes",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
            width=120
        ).pack(side="right", padx=(0, 15))

        self.table_body = ctk.CTkScrollableFrame(
            self.table_frame, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.infratores = self.carregar_do_banco()
        self.carregar_infratores()

    def carregar_do_banco(self):
        db = Database()
        if db.conectar():
            resultados = db.executar("SELECT id_infrator, nome_infrator, cpf, email, telefone_infrator FROM infrator")
            infratores = []
            if resultados:
                for row in resultados.fetchall():
                    infratores.append({
                        "id": row[0],
                        "nome": row[1],
                        "cpf": row[2],
                        "email": row[3],
                        "telefone": row[4] or "-",
                    })
            db.desconectar()
            return infratores
        return []

    def carregar_infratores(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for infrator in self.infratores:
            self.adicionar_linha(infrator)

    def adicionar_linha(self, infrator):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(
            self.table_body, fg_color="#F0F0F0", height=1
        ).pack(fill="x")

        cb = ctk.CTkCheckBox(
            linha, text="", width=20, height=20,
            border_width=2, corner_radius=4
        )
        cb.pack(side="left", padx=(17, 0))

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(10, 0))
        data.grid_columnconfigure(0, weight=3)
        data.grid_columnconfigure(1, weight=2)
        data.grid_columnconfigure(2, weight=2)
        data.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(
            data, text=infrator["nome"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            data, text=infrator["cpf"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text_muted"], anchor="w"
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            data, text=infrator["email"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text_muted"], anchor="w"
        ).grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(
            data, text=infrator["telefone"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=3, sticky="w")

        actions = ctk.CTkFrame(linha, fg_color="transparent")
        actions.pack(side="right", padx=(0, 10))

        botoes_acoes = [
            ("\U0001f441", lambda u=infrator: self.visualizar(u)),
            ("\u270f", lambda u=infrator: self.editar(u)),
            ("\U0001f5d1", lambda u=infrator: self.excluir(u)),
        ]
        for icon, cmd in botoes_acoes:
            ctk.CTkButton(
                actions,
                text=icon, width=32, height=32,
                corner_radius=6, fg_color=COLORS["white"],
                hover_color="#F0F0F0", text_color=COLORS["text"],
                border_width=1, border_color=COLORS["border"],
                font=ctk.CTkFont(size=14),
                command=cmd,
            ).pack(side="left", padx=2)

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        filtro_email = self.entry_filtro1.get().strip().lower()
        filtro_tel = self.entry_filtro2.get().strip().lower()

        todos = self.carregar_do_banco()
        self.infratores = [
            i for i in todos
            if (not busca or busca in i["nome"].lower() or busca in i["cpf"] or busca in i["email"].lower())
            and (not filtro_email or filtro_email in i["email"].lower())
            and (not filtro_tel or filtro_tel in i["telefone"])
        ]
        self.carregar_infratores()

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.entry_filtro1.delete(0, "end")
        self.entry_filtro2.delete(0, "end")
        self.infratores = self.carregar_do_banco()
        self.carregar_infratores()

    def novo_infrator(self):
        self.abrir_formulario()

    def visualizar(self, infrator):
        messagebox.showinfo(
            "Visualizar",
            f"Nome: {infrator['nome']}\nCPF: {infrator['cpf']}\nEmail: {infrator['email']}\nTelefone: {infrator['telefone']}"
        )

    def editar(self, infrator):
        self.abrir_formulario(infrator)

    def excluir(self, infrator):
        if messagebox.askyesno("Excluir", f"Deseja excluir {infrator['nome']}?"):
            db = Database()
            if db.conectar():
                db.executar("DELETE FROM infrator WHERE id_infrator = %s", (infrator["id"],))
                db.commitar()
                db.desconectar()
            self.infratores = self.carregar_do_banco()
            self.carregar_infratores()

    def abrir_formulario(self, infrator=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Infrator" if infrator else "Novo Infrator")
        modal.geometry("420x480")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        titulo = "Editar Infrator" if infrator else "Novo Infrator"
        ctk.CTkLabel(
            modal, text=titulo,
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(20, 15))

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(padx=30, fill="x")

        campos = {
            "Nome": infrator["nome"] if infrator else "",
            "CPF": infrator["cpf"] if infrator else "",
            "Email": infrator["email"] if infrator else "",
            "Telefone": infrator["telefone"] if infrator else "",
            "Senha": "",
        }

        entries = {}
        for label, valor in campos.items():
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                          text_color=COLORS["text"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(frame, height=36, corner_radius=6,
                                  fg_color=COLORS["white"], border_width=1, border_color=COLORS["border"],
                                  show="*" if label == "Senha" else "")
            entry.pack(fill="x")
            if valor:
                entry.insert(0, valor)
            entries[label] = entry

        if not infrator:
            entries["Senha"].configure(show="")

        def salvar():
            nome = entries["Nome"].get().strip()
            cpf = entries["CPF"].get().strip()
            email = entries["Email"].get().strip()
            telefone = entries["Telefone"].get().strip()
            senha = entries["Senha"].get().strip()

            if not nome or not cpf or not email:
                messagebox.showwarning("Aviso", "Nome, CPF e Email são obrigatórios!", parent=modal)
                return

            db = Database()
            if db.conectar():
                if infrator:
                    if senha:
                        db.executar(
                            "UPDATE infrator SET nome_infrator=%s, cpf=%s, email=%s, telefone_infrator=%s, senha=%s WHERE id_infrator=%s",
                            (nome, cpf, email, telefone, senha, infrator["id"])
                        )
                    else:
                        db.executar(
                            "UPDATE infrator SET nome_infrator=%s, cpf=%s, email=%s, telefone_infrator=%s WHERE id_infrator=%s",
                            (nome, cpf, email, telefone, infrator["id"])
                        )
                else:
                    if not senha:
                        messagebox.showwarning("Aviso", "Senha é obrigatória para novo infrator!", parent=modal)
                        return
                    db.executar(
                        "INSERT INTO infrator (nome_infrator, cpf, email, telefone_infrator, senha) VALUES (%s,%s,%s,%s,%s)",
                        (nome, cpf, email, telefone, senha)
                    )
                db.commitar()
                db.desconectar()

            modal.destroy()
            self.infratores = self.carregar_do_banco()
            self.carregar_infratores()

        ctk.CTkButton(
            frame, text="Salvar", height=40, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=salvar
        ).pack(fill="x", pady=(20, 5))

        ctk.CTkButton(
            frame, text="Cancelar", height=34, corner_radius=6,
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color="#F0F0F0", font=ctk.CTkFont(size=FONTS["size_body"]),
            command=modal.destroy
        ).pack(fill="x")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Agentes IBAMA")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    InfratoresPage(app).pack(fill="both", expand=True)
    app.mainloop()
