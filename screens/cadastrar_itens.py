import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.conexaodb import Database
from screens.widgets import ComboBoxComSeta
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

        ctk.CTkLabel(qtd_frame, text="Qtd. Prevista para o TCCM*", font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        self.entry_qtd = ctk.CTkEntry(qtd_frame, height=36, corner_radius=4, border_width=1, border_color=COLORS["border"], fg_color=COLORS["white"], text_color=COLORS["text"]) 
        self.entry_qtd.pack(fill="x")

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

        combo = ComboBoxComSeta(
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

            # persist per-semester quantities based on TCCM semesters
            try:
                from datetime import datetime as _dt
                r_tccm = db.executar(
                    "SELECT data_inicio, semestres FROM tccm WHERE processo = ?",
                    (self.processo_tccm,),
                )
                tccm_row = r_tccm.fetchone() if r_tccm else None

                if tccm_row and tccm_row[1]:
                    data_inicio = tccm_row[0]
                    semestres_total = int(tccm_row[1]) or 1

                    try:
                        if hasattr(data_inicio, "year"):
                            start_dt = data_inicio
                        else:
                            start_dt = _dt.strptime(str(data_inicio), "%Y-%m-%d")
                    except Exception:
                        start_dt = _dt.now()

                    start_sem = 1 if start_dt.month <= 6 else 2

                    base = qtd_int // semestres_total
                    rem = qtd_int % semestres_total

                    for i in range(semestres_total):
                        offset = (start_sem - 1) + i
                        ano = start_dt.year + (offset // 2)
                        sem_num = (offset % 2) + 1
                        qtd_sem = base + (1 if i < rem else 0)
                        db.executar(
                            "INSERT OR REPLACE INTO item_semestre "
                            "(itens_id, ano, semestre, quantidade_prevista, processo) "
                            "VALUES (?, ?, ?, ?, ?)",
                            (item_id, ano, sem_num, qtd_sem, self.processo_tccm),
                        )
                else:
                    now = _dt.now()
                    ano = now.year
                    semestre = 1 if now.month <= 6 else 2
                    db.executar(
                        "INSERT OR REPLACE INTO item_semestre "
                        "(itens_id, ano, semestre, quantidade_prevista, processo) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (item_id, ano, semestre, qtd_int, self.processo_tccm),
                    )
            except Exception:
                pass

            db.commitar()

        registrar_log(self.usuario_logado or "Sistema", "edicao" if self.item_edicao else "cadastro", "itens", mensagem)
        messagebox.showinfo("Sucesso", mensagem, parent=self)
        self.destroy()
