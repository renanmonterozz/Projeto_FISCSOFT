import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from utils import registrar_log


class CadastrarItensWindow(ctk.CTkToplevel):
    def __init__(self, master=None, item=None, processo_tccm=None, usuario_logado=None):
        super().__init__(master)
        self.item_edicao = item
        self.processo_tccm = processo_tccm
        self.usuario_logado = usuario_logado
        self.title("FISCSOFT - Cadastrar Item")
        self.geometry("820x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.item_edicao:
            self.preencher_campos()

    def build_ui(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            header,
            text="Cadastro Item",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Informe os dados do item.",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(2, 0))

        form = ctk.CTkFrame(
            container, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        form.pack(fill="both", expand=True, padx=25, pady=(15, 30))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(18, 10))

        self.entry_nome = self._criar_campo(row1, "Nome do Item*", 0, weight=3)
        self.entry_desc = self._criar_campo(row1, "Descricao", 1, weight=3)

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(0, 10))

        self.combo_tipo = self._criar_combobox(row2, "Tipo de Material*", 0,
                                               ["Consumivel", "Permanente"], default="Consumivel")
        self.combo_unidade = self._criar_combobox(row2, "Unidade de Medida*", 1,
                                                  ["Unidade", "Caixa", "Litro", "Kg"], default="Unidade")

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_just = self._criar_campo(row3, "Justificativa*", 0, weight=3)
        # quantidade prevista is per-semester
        qtd_frame = ctk.CTkFrame(row3, fg_color="transparent")
        qtd_frame.grid_columnconfigure(0, weight=1)
        qtd_frame.grid(row=0, column=1, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(qtd_frame, text="Qtd. Prevista (por semestre)*", font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        self.entry_qtd = ctk.CTkEntry(qtd_frame, height=36, corner_radius=4, border_width=1, border_color=COLORS["border"], fg_color=COLORS["white"], text_color=COLORS["text"]) 
        self.entry_qtd.pack(fill="x", side="left", expand=True)

        self.btn_gerenciar_semestres = ctk.CTkButton(qtd_frame, text="Gerenciar Semestres", width=160, height=36, command=self._abrir_gerenciador_semestres)
        self.btn_gerenciar_semestres.pack(side="right", padx=(8,0))

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(25, 20))

        ctk.CTkButton(
            btn_frame,
            text="  Salvar Item",
            height=40, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40, corner_radius=4,
            fg_color=COLORS["border"], hover_color="#C8C8C8",
            text_color=COLORS["text"], border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.destroy,
        ).pack(side="right")

    def preencher_campos(self):
        it = self.item_edicao
        self.entry_nome.insert(0, it.get("nome") or "")
        self.entry_desc.insert(0, it.get("descricao") or "")
        self.combo_tipo.set(it.get("tipo") or "Consumivel")
        self.combo_unidade.set(it.get("unidade_medida") or "Unidade")
        self.entry_just.insert(0, it.get("justificativa") or "")
        self.entry_qtd.insert(0, str(it.get("quantidade_prevista") or 0))
        # enable gerenciador for existing items
        try:
            self.btn_gerenciar_semestres.configure(state="normal")
        except Exception:
            pass

    def _criar_campo(self, parent, label, col, weight=1):
        parent.grid_columnconfigure(col, weight=weight)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame, height=36, corner_radius=4,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        entry.pack(fill="x")
        return entry

    def _criar_combobox(self, parent, label, col, values, default=None):
        parent.grid_columnconfigure(col, weight=1)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=(0, 15), sticky="ew")

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 4))

        combo = ctk.CTkComboBox(
            frame, values=values, height=36,
            corner_radius=4, border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["white"], button_color=COLORS["border"],
            button_hover_color=COLORS["hover"],
            dropdown_fg_color=COLORS["white"],
            text_color=COLORS["text"],
        )
        combo.pack(fill="x")
        combo.set(default if default is not None else values[0])
        return combo

    def salvar(self):
        nome = self.entry_nome.get().strip()
        desc = self.entry_desc.get().strip() or nome
        tipo = self.combo_tipo.get().strip()
        unidade = self.combo_unidade.get().strip()
        just = self.entry_just.get().strip()
        qtd = self.entry_qtd.get().strip()

        if not all([nome, just, qtd]):
            messagebox.showwarning("Atencao", "Preencha nome, justificativa e quantidade prevista!", parent=self)
            return

        try:
            qtd_int = int(qtd)
        except ValueError:
            messagebox.showerror("Erro", "Qtd. Prevista deve ser um numero inteiro!", parent=self)
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!", parent=self)
                return

            if self.item_edicao:
                sql = """UPDATE itens SET nome=?, descricao=?, tipo=?, justificativa=?,
                         unidade_medida=?, quantidade_prevista=? WHERE id=?"""
                params = (nome, desc, tipo, just, unidade, qtd_int, self.item_edicao["id"])
                mensagem = f"Item '{nome}' atualizado com sucesso!"
            else:
                c = db.executar("SELECT COALESCE(MAX(id), 0) + 1 FROM itens")
                nid = c.fetchone()[0] if c else 1
                codigo = f"IT-{nid:03d}"
                sql = """INSERT INTO itens (nome, descricao, codigo_interno, tipo, justificativa,
                                            unidade_medida, quantidade_prevista, status, processo)
                         VALUES (?, ?, ?, ?, ?, ?, ?, 'Ativo', ?)"""
                params = (nome, desc, codigo, tipo, just, unidade, qtd_int, self.processo_tccm)
                mensagem = f"Item '{nome}' cadastrado com sucesso!"

            db.executar(sql, params)
            cur = db.executar("SELECT last_insert_rowid()")
            try:
                # try to obtain last inserted id; if editing, use existing id
                if self.item_edicao:
                    item_id = self.item_edicao["id"]
                else:
                    # fetch last row id from connection
                    lr = cur.fetchone()
                    item_id = int(lr[0]) if lr else nid
            except Exception:
                item_id = self.item_edicao["id"] if self.item_edicao else nid

            # persist per-semester quantidade in item_semestre
            try:
                from datetime import datetime as _dt
                now = _dt.now()
                ano = now.year
                semestre = 1 if now.month <= 6 else 2
                db.executar(
                    "INSERT OR REPLACE INTO item_semestre (itens_id, ano, semestre, quantidade_prevista, processo) VALUES (?, ?, ?, ?, ?)",
                    (item_id, ano, semestre, qtd_int, self.processo_tccm),
                )
            except Exception:
                pass

            db.commitar()

        registrar_log(self.usuario_logado or "Sistema", "edicao" if self.item_edicao else "cadastro", "itens", mensagem)
        messagebox.showinfo("Sucesso", mensagem, parent=self)
        self.destroy()

    def _abrir_gerenciador_semestres(self):
        # only for existing items
        if not self.item_edicao:
            messagebox.showinfo("Info", "Salve o item primeiro para gerenciar quantidades por semestre.", parent=self)
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Gerenciar Quantidades por Semestre")
        modal.geometry("520x400")
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color=COLORS["white"])
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # listbox for existing entries
        list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True)

        self.sem_list = ctk.CTkScrollableFrame(list_frame, fg_color=COLORS["white"])
        self.sem_list.pack(fill="both", expand=True, side="left")

        ctrl_frame = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=(8,0))

        # inputs
        ano_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        ano_frame.pack(side="left", padx=6)
        ctk.CTkLabel(ano_frame, text="Ano", font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w")
        self.input_ano = ctk.CTkEntry(ano_frame, width=80, height=28)
        self.input_ano.pack()

        sem_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        sem_frame.pack(side="left", padx=6)
        ctk.CTkLabel(sem_frame, text="Semestre", font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w")
        self.input_sem = ctk.CTkComboBox(sem_frame, values=["1","2"], width=80)
        self.input_sem.set("1")
        self.input_sem.pack()

        qtd_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        qtd_frame.pack(side="left", padx=6)
        ctk.CTkLabel(qtd_frame, text="Qtd.", font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w")
        self.input_qtd_sem = ctk.CTkEntry(qtd_frame, width=100, height=28)
        self.input_qtd_sem.pack()

        btn_add = ctk.CTkButton(ctrl_frame, text="Adicionar/Atualizar", command=lambda: self._add_or_update_semestre(modal))
        btn_add.pack(side="left", padx=6)

        btn_refresh = ctk.CTkButton(ctrl_frame, text="Fechar", command=modal.destroy)
        btn_refresh.pack(side="right", padx=6)

        self._load_semestres_list()

    def _load_semestres_list(self):
        if not hasattr(self, 'sem_list'):
            return
        for w in self.sem_list.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        try:
            with Database() as db:
                if not db.conexao:
                    return
                rows = db.executar("SELECT ano, semestre, quantidade_prevista FROM item_semestre WHERE itens_id = ? ORDER BY ano DESC, semestre DESC", (self.item_edicao["id"],))
                if rows:
                    for r in rows.fetchall():
                        ano, sem, qtd = r[0], r[1], r[2]
                        entry = ctk.CTkFrame(self.sem_list, fg_color=COLORS["border"])
                        entry.pack(fill="x", padx=6, pady=6)
                        ctk.CTkLabel(entry, text=f"{ano} - S{sem}", width=120).pack(side="left", padx=(8,0))
                        ctk.CTkLabel(entry, text=str(qtd)).pack(side="left", padx=(8,0))
                        ctk.CTkButton(entry, text="Editar", width=80, command=lambda a=ano, s=sem: self._fill_sem_inputs(a, s)).pack(side="right", padx=6)
                        ctk.CTkButton(entry, text="Remover", width=80, command=lambda a=ano, s=sem: self._remove_semestre(a, s)).pack(side="right")
        except Exception:
            pass

    def _fill_sem_inputs(self, ano, sem):
        try:
            with Database() as db:
                r = db.executar("SELECT quantidade_prevista FROM item_semestre WHERE itens_id = ? AND ano = ? AND semestre = ?", (self.item_edicao["id"], ano, sem))
                row = r.fetchone() if r else None
                if row:
                    self.input_ano.delete(0, 'end')
                    self.input_ano.insert(0, str(ano))
                    self.input_sem.set(str(sem))
                    self.input_qtd_sem.delete(0, 'end')
                    self.input_qtd_sem.insert(0, str(row[0] or 0))
        except Exception:
            pass

    def _add_or_update_semestre(self, modal):
        try:
            ano = int(self.input_ano.get())
            sem = int(self.input_sem.get())
            qtd = int(self.input_qtd_sem.get())
        except Exception:
            messagebox.showerror("Erro", "Preencha ano, semestre e quantidade correta.", parent=modal)
            return
        try:
            with Database() as db:
                if not db.conexao:
                    messagebox.showerror("Erro", "Nao foi possivel conectar ao banco.", parent=modal)
                    return
                db.executar("INSERT OR REPLACE INTO item_semestre (itens_id, ano, semestre, quantidade_prevista, processo) VALUES (?, ?, ?, ?, ?)", (self.item_edicao["id"], ano, sem, qtd, self.processo_tccm))
                db.commitar()
            self._load_semestres_list()
        except Exception:
            messagebox.showerror("Erro", "Falha ao atualizar banco.", parent=modal)

    def _remove_semestre(self, ano, sem):
        try:
            with Database() as db:
                db.executar("DELETE FROM item_semestre WHERE itens_id = ? AND ano = ? AND semestre = ?", (self.item_edicao["id"], ano, sem))
                db.commitar()
            self._load_semestres_list()
        except Exception:
            pass
