import sys
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

import customtkinter as ctk

try:
    from PyPDF2 import PdfReader
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

from config.styles import COLORS, FONTS
from database.conexaodb import Database


class NotasFiscaisExterno(ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, on_voltar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator
        self.on_voltar = on_voltar
        self.arquivo_selecionado = None
        self.itens_lista = []

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        self.scroll.pack(fill="both", expand=True)

        self._build_header()
        self._build_form()
        self._build_itens_section()
        self._build_upload_section()
        self._build_action_buttons()
        self._carregar_processos()
        self._carregar_itens_tccm()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 5))

        ctk.CTkLabel(
            header, text="Cadastrar Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text="Informe os dados da Nota Fiscal e adicione os itens.",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def _build_form(self):
        form_card = ctk.CTkFrame(
            self.scroll, fg_color=COLORS["white"], corner_radius=6,
            border_width=1, border_color=COLORS["border"]
        )
        form_card.pack(fill="x", padx=40, pady=(20, 0))

        ctk.CTkLabel(
            form_card, text="Dados da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=25, pady=(20, 10))

        self.entry_numero = self._criar_campo(form_card, "Numero da Nota Fiscal*")
        self.entry_chave = self._criar_campo(form_card, "Chave de Acesso*")

        row_meio = ctk.CTkFrame(form_card, fg_color="transparent")
        row_meio.pack(fill="x", padx=25, pady=(0, 10))

        col_data = ctk.CTkFrame(row_meio, fg_color="transparent")
        col_data.pack(side="left", fill="x", expand=True, padx=(0, 20))

        ctk.CTkLabel(
            col_data, text="Data de Emissao*",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        self.entry_data = ctk.CTkEntry(
            col_data, placeholder_text="dd/mm/aaaa",
            height=38, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"], width=200,
        )
        self.entry_data.pack(anchor="w")

        col_processo = ctk.CTkFrame(row_meio, fg_color="transparent")
        col_processo.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            col_processo, text="Processo (TCCM)*",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        self.combo_processo = ctk.CTkComboBox(
            col_processo, values=["Carregando..."],
            height=38, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            width=250,
        )
        self.combo_processo.pack(anchor="w")
        self.combo_processo.set("")
        self.combo_processo.bind("<<ComboboxSelected>>", self._on_processo_changed)

    def _criar_campo(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(
            frame, text=label_text,
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame, height=38, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        entry.pack(fill="x")
        return entry

    def _carregar_processos(self):
        try:
            with Database() as db:
                if not db.conexao:
                    return
                sql = """SELECT processo FROM tccm
                         WHERE "infrator_id_infrator" = ?
                         ORDER BY processo"""
                resultado = db.executar(sql, (self.id_infrator,))
                if resultado:
                    processos = [row[0] for row in resultado.fetchall()]
                    if processos:
                        self.combo_processo.configure(values=processos)
                        self.combo_processo.set(processos[0])
                    else:
                        self.combo_processo.configure(values=["Nenhum TCCM encontrado"])
        except Exception:
            pass

    def _carregar_itens_tccm(self):
        processo = self.combo_processo.get().strip()
        if not processo or "Nenhum TCCM" in processo:
            self.itens_tccm = []
            self.combo_item.configure(values=["Selecione um processo primeiro"])
            self.combo_item.set("Selecione um processo primeiro")
            return

        try:
            with Database() as db:
                if not db.conexao:
                    return
                sql = """SELECT DISTINCT i.id, i.nome, i.descricao, i.unidade_medida
                         FROM produtos p
                         JOIN itens i ON p.itens_id = i.id
                         JOIN "nota fiscal" nf ON p."nota fiscal_nota_fiscal" = nf.nota_fiscal
                         WHERE nf.processo = ? AND i.status = 'Ativo'
                         ORDER BY i.nome"""
                resultado = db.executar(sql, (processo,))
                if resultado:
                    rows = resultado.fetchall()
                    self.itens_tccm = [
                        {"id": row[0], "nome": row[1], "descricao": row[2], "unidade": row[3]}
                        for row in rows
                    ]
                    if self.itens_tccm:
                        nomes = [f"{i['nome']} ({i['descricao']})" for i in self.itens_tccm]
                        self.combo_item.configure(values=nomes)
                        self.combo_item.set(nomes[0])
                    else:
                        self.combo_item.configure(values=["Nenhum item vinculado ao TCCM"])
                        self.combo_item.set("Nenhum item vinculado ao TCCM")
                else:
                    self.itens_tccm = []
                    self.combo_item.configure(values=["Nenhum item vinculado ao TCCM"])
                    self.combo_item.set("Nenhum item vinculado ao TCCM")
        except Exception:
            self.itens_tccm = []
            self.combo_item.configure(values=["Erro ao carregar itens"])
            self.combo_item.set("Erro ao carregar itens")

    def _on_processo_changed(self, event=None):
        self._carregar_itens_tccm()

    def _build_itens_section(self):
        itens_card = ctk.CTkFrame(
            self.scroll, fg_color=COLORS["white"], corner_radius=6,
            border_width=1, border_color=COLORS["border"]
        )
        itens_card.pack(fill="x", padx=40, pady=(15, 0))

        ctk.CTkLabel(
            itens_card, text="Itens da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=25, pady=(20, 10))

        add_frame = ctk.CTkFrame(itens_card, fg_color="transparent")
        add_frame.pack(fill="x", padx=25, pady=(0, 10))

        col_item = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_item.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            col_item, text="Item (itens vinculados ao TCCM selecionado)",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        self.itens_tccm = []
        nomes_itens = ["Selecione um processo primeiro"]
        self.combo_item = ctk.CTkComboBox(
            col_item, values=nomes_itens,
            height=36, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            width=300,
        )
        self.combo_item.pack(anchor="w")
        self.combo_item.set(nomes_itens[0])

        btn_refresh = ctk.CTkButton(
            col_item, text="Atualizar", height=36, width=80, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._carregar_itens_tccm,
        )
        btn_refresh.pack(side="left", padx=(8, 0), pady=(18, 0))

        col_qtd = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_qtd.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            col_qtd, text="Qtd.",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        self.entry_qtd = ctk.CTkEntry(
            col_qtd, height=36, width=70, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="0",
        )
        self.entry_qtd.pack(anchor="w")

        col_preco = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_preco.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            col_preco, text="Preco Unit. (R$)",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        self.entry_preco = ctk.CTkEntry(
            col_preco, height=36, width=120, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="0,00",
        )
        self.entry_preco.pack(anchor="w")

        btn_add = ctk.CTkButton(
            add_frame, text="+ Adicionar", height=36, width=120, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._adicionar_item,
        )
        btn_add.pack(side="left", pady=(20, 0))

        tree_frame = ctk.CTkFrame(itens_card, fg_color="transparent")
        tree_frame.pack(fill="x", padx=25, pady=(10, 0))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Itens.Treeview",
                         background=COLORS["white"],
                         foreground=COLORS["text"],
                         rowheight=32,
                         fieldbackground=COLORS["white"],
                         borderwidth=0,
                         font=(None, FONTS["size_small"]))
        style.configure("Itens.Treeview.Heading",
                         background=COLORS["table_header"],
                         foreground=COLORS["text_muted"],
                         borderwidth=0,
                         font=(None, FONTS["size_small"], "bold"))
        style.map("Itens.Treeview",
                   background=[("selected", COLORS["primary_light"])],
                   foreground=[("selected", COLORS["text"])])

        tree_container = ctk.CTkFrame(tree_frame, fg_color=COLORS["border"], corner_radius=4)
        tree_container.pack(fill="x")

        colunas = ("item", "qtd", "preco", "subtotal")
        self.tree_itens = ttk.Treeview(
            tree_container, columns=colunas, show="headings",
            style="Itens.Treeview", height=5, selectmode="browse"
        )
        self.tree_itens.heading("item", text="Item", anchor="w")
        self.tree_itens.heading("qtd", text="Qtd.", anchor="w")
        self.tree_itens.heading("preco", text="Preco Unit. (R$)", anchor="w")
        self.tree_itens.heading("subtotal", text="Subtotal (R$)", anchor="w")

        self.tree_itens.column("item", width=300, minwidth=200, anchor="w")
        self.tree_itens.column("qtd", width=60, minwidth=50, anchor="w")
        self.tree_itens.column("preco", width=140, minwidth=100, anchor="w")
        self.tree_itens.column("subtotal", width=140, minwidth=100, anchor="w")

        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical",
                                     command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=tree_scroll.set)

        self.tree_itens.pack(side="left", fill="x", expand=True, padx=(4, 0), pady=4)
        tree_scroll.pack(side="right", fill="y", pady=4, padx=(0, 4))

        btn_row = ctk.CTkFrame(itens_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(8, 10))

        self.btn_remover_item = ctk.CTkButton(
            btn_row, text="Remover selecionado", height=32, width=160, corner_radius=4,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._remover_item_selecionado,
        )
        self.btn_remover_item.pack(side="left")

        self.lbl_total_geral = ctk.CTkLabel(
            btn_row, text="Total Itens: R$ 0,00",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        )
        self.lbl_total_geral.pack(side="right")

    def _adicionar_item(self):
        idx = self.combo_item.get()
        qtd_str = self.entry_qtd.get().strip()
        preco_str = self.entry_preco.get().strip()

        if not idx or "Nenhum item" in idx or "Selecione" in idx or "Erro" in idx:
            messagebox.showwarning("Atencao", "Selecione um item do TCCM.")
            return
        if not qtd_str or not preco_str:
            messagebox.showwarning("Atencao", "Preencha quantidade e preco unitario.")
            return

        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atencao", "Quantidade invalida.")
            return

        try:
            preco = float(preco_str.replace(".", "").replace(",", "."))
            if preco <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atencao", "Preco unitario invalido.")
            return

        item_idx = None
        for i, item in enumerate(self.itens_tccm):
            display = f"{item['nome']} ({item['descricao']})"
            if display == idx:
                item_idx = i
                break

        if item_idx is None:
            messagebox.showwarning("Atencao", "Item nao encontrado no TCCM.")
            return

        item_info = self.itens_tccm[item_idx]
        subtotal = qtd * preco

        self.itens_lista.append({
            "item_id": item_info["id"],
            "nome": item_info["nome"],
            "descricao": item_info["descricao"],
            "quantidade": qtd,
            "preco_unitario": preco,
            "subtotal": subtotal,
        })

        self._render_itens()
        self.entry_qtd.delete(0, "end")
        self.entry_preco.delete(0, "end")

    def _remover_item_selecionado(self):
        sel = self.tree_itens.selection()
        if not sel:
            messagebox.showwarning("Atencao", "Selecione um item na tabela para remover.")
            return
        idx = self.tree_itens.index(sel[0])
        if 0 <= idx < len(self.itens_lista):
            self.itens_lista.pop(idx)
            self._render_itens()

    def _render_itens(self):
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)

        if not self.itens_lista:
            self.lbl_total_geral.configure(text="Total Itens: R$ 0,00")
            return

        for item in self.itens_lista:
            preco_fmt = f"R$ {item['preco_unitario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            subtotal_fmt = f"R$ {item['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.tree_itens.insert("", "end", values=(
                item["nome"], item["quantidade"], preco_fmt, subtotal_fmt
            ))

        total_geral = sum(item["subtotal"] for item in self.itens_lista)
        total_fmt = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_total_geral.configure(text=f"Total Itens: {total_fmt}")

    def _build_upload_section(self):
        upload_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        upload_frame.pack(fill="x", padx=40, pady=(25, 0))

        ctk.CTkLabel(
            upload_frame, text="Anexar arquivo da Nota Fiscal *",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 10))

        btn_row = ctk.CTkFrame(upload_frame, fg_color="transparent")
        btn_row.pack(fill="x")

        self.btn_anexar = ctk.CTkButton(
            btn_row, text="ANEXAR PDF", height=70, corner_radius=8,
            fg_color="#CC0000", hover_color="#AA0000",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            command=self._selecionar_arquivo,
        )
        self.btn_anexar.pack(side="right")

        self.btn_limpar = ctk.CTkButton(
            btn_row, text="LIMPAR", height=70, corner_radius=8,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            command=self._limpar_campos,
        )
        self.btn_limpar.pack(side="right", padx=(0, 10))

        self.lbl_arquivo = ctk.CTkFrame(
            upload_frame, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"],
            height=36,
        )
        self.lbl_arquivo.pack(fill="x", padx=0, pady=(10, 0))
        self.lbl_arquivo.pack_propagate(False)

        self.lbl_arquivo_text = ctk.CTkLabel(
            self.lbl_arquivo, text="Nenhum arquivo anexado",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self.lbl_arquivo_text.pack(side="left", padx=10, fill="both", expand=True)

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Nota Fiscal",
            filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.arquivo_selecionado = caminho
            nome = os.path.basename(caminho)
            tamanho = os.path.getsize(caminho)
            tamanho_kb = f"{tamanho / 1024:.1f} KB"
            self.lbl_arquivo_text.configure(text=f"{nome}  ({tamanho_kb})")

            dados_pdf = self._extrair_dados_pdf(caminho)
            if dados_pdf:
                self._auto_preencher(dados_pdf)

    def _extrair_dados_pdf(self, caminho):
        if not PDF_DISPONIVEL:
            return None

        try:
            reader = PdfReader(caminho)
            texto_completo = ""
            for page in reader.pages:
                texto_completo += page.extract_text() or ""

            if not texto_completo.strip():
                return None

            dados = {}

            padroes_numero = [
                r'NFe\s+N[º°o.\s]*[:\-]?\s*(\d{1,20})',
                r'N[º°o]\s*(?:da\s+)?(?:Nota(?:\s+Fiscal)?|NF-e?)\s*[:\-]?\s*(\d{1,9})',
                r'Numero\s*(?:da\s+)?(?:Nota(?:\s+Fiscal)?|NF-e?)\s*[:\-]?\s*(\d{1,9})',
                r'NF[\s\-:]*(\d{1,9})',
                r'(?:N[º°o]|Number)\s*[:\-]?\s*(\d{9,20})',
            ]
            for padrao in padroes_numero:
                match = re.search(padrao, texto_completo, re.IGNORECASE)
                if match:
                    dados['numero'] = match.group(1).strip()
                    break

            padroes_chave = [
                r'(?:Chave\s+de\s+Acesso|Chave\s+NF-e?)\s*[:\-]?\s*(\d{44})',
                r'(\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4})',
                r'\b(\d{44})\b',
            ]
            for padrao in padroes_chave:
                match = re.search(padrao, texto_completo, re.IGNORECASE)
                if match:
                    chave = re.sub(r'\s', '', match.group(1))
                    if len(chave) == 44:
                        dados['chave'] = chave
                        break

            padroes_data = [
                r'(?:Data\s+de\s+Emiss[aã]o|Emiss[aã]o)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})',
                r'(?:Data\s+de\s+Emiss[aã]o|Emiss[aã]o)\s*[:\-]?\s*(\d{2}-\d{2}-\d{4})',
                r'(?:Data\s+de\s+Emiss[aã]o|Emiss[aã]o)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})',
            ]
            for padrao in padroes_data:
                match = re.search(padrao, texto_completo, re.IGNORECASE)
                if match:
                    raw = match.group(1).strip()
                    if re.match(r'\d{2}/\d{2}/\d{4}', raw):
                        dados['data'] = raw
                    elif re.match(r'\d{2}-\d{2}-\d{4}', raw):
                        dados['data'] = raw.replace('-', '/')
                    elif re.match(r'\d{4}-\d{2}-\d{2}', raw):
                        d = datetime.strptime(raw, "%Y-%m-%d")
                        dados['data'] = d.strftime("%d/%m/%Y")
                    break

            itens = self._extrair_itens_pdf(texto_completo)
            if itens:
                dados['itens'] = itens

            return dados if dados else None

        except Exception as e:
            print(f"[FISCSOFT] Erro ao extrair PDF: {e}")
            return None

    def _extrair_itens_pdf(self, texto):
        itens = []
        linhas = texto.split('\n')

        for i, linha in enumerate(linhas):
            match = re.search(
                r'(\d+)\s+(.{3,60}?)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)',
                linha
            )
            if match:
                nome = match.group(2).strip()
                try:
                    qtd = int(match.group(3).replace('.', ''))
                    preco_str = match.group(4).replace('.', '').replace(',', '.')
                    preco = float(preco_str)
                except (ValueError, IndexError):
                    continue

                if qtd > 0 and preco > 0:
                    itens.append({
                        "nome": nome,
                        "quantidade": qtd,
                        "preco_unitario": preco,
                    })

        return itens if itens else None

    def _auto_preencher(self, dados):
        if 'numero' in dados:
            self.entry_numero.delete(0, "end")
            self.entry_numero.insert(0, dados['numero'])

        if 'chave' in dados:
            self.entry_chave.delete(0, "end")
            self.entry_chave.insert(0, dados['chave'])

        if 'data' in dados:
            self.entry_data.delete(0, "end")
            self.entry_data.insert(0, dados['data'])

        if 'itens' in dados:
            self.itens_lista = []
            for item_pdf in dados['itens']:
                item_match = None
                for item_tccm in self.itens_tccm:
                    if item_tccm['nome'].lower() in item_pdf['nome'].lower() or \
                       item_pdf['nome'].lower() in item_tccm['nome'].lower():
                        item_match = item_tccm
                        break

                self.itens_lista.append({
                    "item_id": item_match["id"] if item_match else 0,
                    "nome": item_match["nome"] if item_match else item_pdf['nome'],
                    "descricao": item_match["descricao"] if item_match else "Extraido do PDF",
                    "quantidade": item_pdf['quantidade'],
                    "preco_unitario": item_pdf['preco_unitario'],
                    "subtotal": item_pdf['quantidade'] * item_pdf['preco_unitario'],
                })
            self._render_itens()

        campos_preenchidos = [k for k in ['numero', 'chave', 'data', 'itens'] if k in dados]
        if campos_preenchidos:
            campos_nomes = {'numero': 'Numero NF', 'chave': 'Chave', 'data': 'Data', 'itens': 'Itens'}
            lista = ', '.join(campos_nomes[k] for k in campos_preenchidos)
            messagebox.showinfo("PDF Importado",
                f"Campos preenchidos automaticamente:\n{lista}")

    def _build_action_buttons(self):
        btn_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_container.pack(fill="x", padx=40, pady=(30, 30))

        ctk.CTkButton(
            btn_container, text="Salvar Nota Fiscal", height=40, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            width=200,
            command=self._salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_container, text="  Voltar", height=40, corner_radius=6,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            width=140,
            command=self._voltar,
        ).pack(side="left")

    def _salvar(self):
        numero = self.entry_numero.get().strip()
        chave = self.entry_chave.get().strip()
        data_str = self.entry_data.get().strip()
        processo = self.combo_processo.get().strip()

        if not numero or not chave or not data_str or not processo:
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios.")
            return

        if "Nenhum TCCM" in processo:
            messagebox.showwarning("Atencao", "Nenhum TCCM encontrado para este infrator.")
            return

        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atencao", "Data invalida. Use o formato dd/mm/aaaa.")
            return

        if not self.itens_lista:
            messagebox.showwarning("Atencao", "Adicione pelo menos um item a nota fiscal.")
            return

        valor_total = sum(item["subtotal"] for item in self.itens_lista)

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados.")
                return

            try:
                sql_mat = '''SELECT "agente ibama_matricula"
                             FROM tccm WHERE processo = ?
                             LIMIT 1'''
                resultado = db.executar(sql_mat, (processo,))
                row = resultado.fetchone() if resultado else None
                matricula = row[0] if row else 0

                sql = """INSERT INTO "nota fiscal"
                         (nota_fiscal, semestre, data, chave_de_acesso, valor_total,
                          "agente ibama_matricula", status_nota, processo)
                         VALUES (?, ?, ?, ?, ?, ?, 'Pendente', ?)"""
                db.executar(sql, (numero, 1, data, chave, valor_total, matricula, processo))

                for idx, item in enumerate(self.itens_lista):
                    lote = f"{numero}-ITEM-{idx+1}"
                    sql_produto = """INSERT INTO produtos
                                    (lote, quantidade, preco_unitario,
                                     "nota fiscal_nota_fiscal",
                                     "nota fiscal_agente ibama_matricula",
                                     itens_id, nome_item)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
                    db.executar(sql_produto, (
                        lote, item["quantidade"], item["preco_unitario"],
                        numero, matricula, item["item_id"], item["nome"],
                    ))

                db.commitar()
                messagebox.showinfo("Sucesso",
                    f"Nota fiscal cadastrada com sucesso!\n"
                    f"Valor Total: R$ {valor_total:,.2f}\n"
                    f"Itens: {len(self.itens_lista)}")
                self._limpar_campos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar nota fiscal:\n{e}")

    def _limpar_campos(self):
        self.entry_numero.delete(0, "end")
        self.entry_chave.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.entry_preco.delete(0, "end")
        if self.itens_tccm:
            nomes = [f"{i['nome']} ({i['descricao']})" for i in self.itens_tccm]
            self.combo_item.set(nomes[0])
        else:
            self.combo_item.set("Selecione um processo primeiro")
        self.itens_lista = []
        self._render_itens()
        self.arquivo_selecionado = None
        self.lbl_arquivo_text.configure(text="Nenhum arquivo anexado")

    def _voltar(self):
        if self.on_voltar:
            self.on_voltar()
