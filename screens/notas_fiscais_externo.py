import _path  # noqa: F401

import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

import customtkinter as ctk
from screens.widgets import ComboBoxComSeta

try:
    from PyPDF2 import PdfReader
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

from config.styles import ASSETS_DIR, ASSETS_DIR, COLORS, FONTS
from services.notas_service import (
    NotasFiscaisService,
    RegraNotaError,
    preparar_item_nota,
)
from screens.widgets import ComboBoxComSeta

ANEXOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "anexos")


class NotasFiscaisExterno(ctk.CTkFrame):
    def __init__(self, master, usuario_logado=None, id_infrator=None, on_voltar=None, nota_edicao=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.usuario_logado = usuario_logado
        self.id_infrator = id_infrator
        self.on_voltar = on_voltar
        self.nota_edicao = nota_edicao
        self.arquivo_selecionado = None
        self.itens_lista = []
        self._processo_map = {}
        self.service = NotasFiscaisService()

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        self.scroll.pack(fill="both", expand=True)

        self._build_header()
        self._build_form()
        self._build_upload_section()
        self._build_itens_section()
        self._build_action_buttons()
        self._carregar_processos()
        self._carregar_itens_tccm()
        if self.nota_edicao:
            self._preencher_edicao()

    def _preencher_edicao(self):
        processo = self.nota_edicao.get("processo")
        for display, valor in self._processo_map.items():
            if valor == processo:
                self.combo_processo.set(display)
                break
        self._carregar_itens_tccm()

        self.entry_numero.insert(0, self.nota_edicao.get("nota_fiscal", ""))
        self.entry_chave.insert(0, self.nota_edicao.get("chave", ""))
        data = self.nota_edicao.get("data")
        if hasattr(data, "strftime"):
            data = data.strftime("%d/%m/%Y")
        self.entry_data.insert(0, data or "")

        itens_por_id = {item["id"]: item for item in self.itens_tccm}
        self.itens_lista = []
        for item in self.nota_edicao.get("itens", []):
            catalogo = itens_por_id.get(item.get("item_id"))
            if catalogo is None:
                continue
            self.itens_lista.append({
                "item_id": catalogo["id"],
                "nome": catalogo["nome"],
                "descricao": catalogo["descricao"],
                "quantidade": item["quantidade"],
                "preco_unitario": float(item["preco_unitario"]),
                "subtotal": item["subtotal"],
            })
        self._render_itens()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(14, 6))

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
        form_card.pack(fill="x", padx=30, pady=(10, 0))

        ctk.CTkLabel(
            form_card, text="Dados da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(12, 10))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(0, 14))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.entry_numero = self._criar_campo_grid(form, 0, 0, "Numero da Nota Fiscal*")
        self.entry_chave = self._criar_campo_grid(form, 0, 1, "Chave de Acesso*")
        self.entry_data = self._criar_campo_grid(form, 1, 0, "Data de Emissao*", "dd/mm/aaaa")

        col_processo = ctk.CTkFrame(form, fg_color="transparent")
        col_processo.grid(row=1, column=1, sticky="ew", padx=(8, 0))

        ctk.CTkLabel(
            col_processo, text="Processo (TCCM)*",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        self.combo_processo = ComboBoxComSeta(
            col_processo, values=["Carregando..."],
            height=38, border_width=1, border_color=COLORS["primary"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            command=self._on_processo_changed,
        )
        self.combo_processo.pack(fill="x")
        self.combo_processo.set("")

    def _criar_campo_grid(self, parent, row, col, label_text, placeholder=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=(0, 8) if col == 0 else (8, 0), pady=(0, 12))

        ctk.CTkLabel(
            frame, text=label_text,
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        entry = ctk.CTkEntry(
            frame, height=38, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text=placeholder or "",
            placeholder_text_color=COLORS["text_muted"],
        )
        entry.pack(fill="x")
        return entry

    def _carregar_processos(self):
        try:
            rows = self.service.listar_processos(self.id_infrator)
            if rows:
                self._processo_map = {}
                opcoes = []
                for processo, nome_infrator in rows:
                    display = f"{processo} - {nome_infrator}"
                    self._processo_map[display] = processo
                    opcoes.append(display)
                self.combo_processo.configure(values=opcoes)
                self.combo_processo.set(opcoes[0])
            else:
                self.combo_processo.configure(values=["Nenhum TCCM encontrado"])
        except Exception:
            pass

    def _get_processo_real(self):
        display = self.combo_processo.get().strip()
        if not display or "Nenhum TCCM" in display:
            return ""
        if hasattr(self, '_processo_map') and display in self._processo_map:
            return self._processo_map[display]
        if " - " in display:
            return display.split(" - ")[0].strip()
        return display

    def _carregar_itens_tccm(self):
        processo = self._get_processo_real()
        if not processo or "Nenhum TCCM" in processo:
            self.itens_tccm = []
            self.combo_item.configure(values=["Selecione um processo primeiro"])
            self.combo_item.set("Selecione um processo primeiro")
            return

        try:
            self.itens_tccm = self.service.listar_itens_processo(processo)
            if self.itens_tccm:
                nomes = [f"{i['nome']} ({i['descricao']})" for i in self.itens_tccm]
                self.combo_item.configure(values=nomes)
                self.combo_item.set(nomes[0])
            else:
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
        itens_card.pack(fill="x", padx=30, pady=(10, 0))

        ctk.CTkLabel(
            itens_card, text="Itens da Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(10, 6))

        add_frame = ctk.CTkFrame(itens_card, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 5))

        col_item = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_item.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkLabel(
            col_item, text="Item (itens vinculados ao TCCM selecionado)",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        self.itens_tccm = []
        nomes_itens = ["Selecione um processo primeiro"]
        self.combo_item = ComboBoxComSeta(
            col_item, values=nomes_itens,
            height=34, border_width=1, border_color=COLORS["primary"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"], dropdown_hover_color=COLORS["primary_light"],
            width=280,
        )
        self.combo_item.pack(anchor="w")
        self.combo_item.set(nomes_itens[0])

        btn_refresh = ctk.CTkButton(
            col_item, text="Atualizar", height=34, width=70, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._carregar_itens_tccm,
        )
        btn_refresh.pack(side="left", padx=(6, 0), pady=(16, 0))

        col_qtd = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_qtd.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            col_qtd, text="Qtd.",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        self.entry_qtd = ctk.CTkEntry(
            col_qtd, height=34, width=60, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="0",
        )
        self.entry_qtd.pack(anchor="w")

        col_preco = ctk.CTkFrame(add_frame, fg_color="transparent")
        col_preco.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            col_preco, text="Preco Unit. (R$)",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 3))

        self.entry_preco = ctk.CTkEntry(
            col_preco, height=34, width=100, border_width=1, border_color=COLORS["border"],
            corner_radius=4, fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text="0,00",
        )
        self.entry_preco.pack(anchor="w")

        btn_add = ctk.CTkButton(
            add_frame, text="+ Adicionar", height=34, width=110, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=self._adicionar_item,
        )
        btn_add.pack(side="left", pady=(16, 0))

        tree_frame = ctk.CTkFrame(itens_card, fg_color=COLORS["white"])
        tree_frame.pack(fill="x", padx=20, pady=(0, 0))

        # --- Cabeçalho separado ---
        table_wrapper = ctk.CTkFrame(
            tree_frame, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        table_wrapper.pack(fill="x")

        header_frame = ctk.CTkFrame(table_wrapper, fg_color=COLORS["table_header"],
                                     height=36, corner_radius=3)
        header_frame.pack(fill="x", padx=1, pady=(1, 0))
        header_frame.pack_propagate(False)

        header_cols = [
            (0.0,  0.46, "w",     "Item"),
            (0.46, 0.14, "w",     "Qtd."),
            (0.60, 0.20, "w",     "Preco Unit. (R$)"),
            (0.80, 0.20, "w",     "Subtotal (R$)"),
        ]

        for rx, rw, anchor, texto in header_cols:
            ctk.CTkLabel(
                header_frame, text=texto,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor=anchor,
            ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

        # --- Container das linhas (substitui o Treeview) ---
        self.table_body = ctk.CTkScrollableFrame(
            table_wrapper, fg_color=COLORS["white"], corner_radius=0,
            height=120
        )
        self.table_body.pack(fill="x", padx=1, pady=(0, 1))

        btn_row = ctk.CTkFrame(itens_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(5, 8))

        self.btn_remover_item = ctk.CTkButton(
            btn_row, text="Remover selecionado", height=30, width=150, corner_radius=4,
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

        try:
            item = preparar_item_nota(idx, qtd_str, preco_str, self.itens_tccm)
        except RegraNotaError as exc:
            messagebox.showwarning("Atencao", str(exc))
            return

        self.itens_lista.append(item)

        self._render_itens()
        self.entry_qtd.delete(0, "end")
        self.entry_preco.delete(0, "end")

    def _remover_item_selecionado(self):
        if not self.item_selecionado_idx is None:
            idx = self.item_selecionado_idx
            if 0 <= idx < len(self.itens_lista):
                self.itens_lista.pop(idx)
                self.item_selecionado_idx = None
                self._render_itens()

    def _render_itens(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        self.item_selecionado_idx = None

        if not self.itens_lista:
            self.lbl_total_geral.configure(text="Total Itens: R$ 0,00")
            return

        col_cfg = [
            (0.0,  0.46, "w"),
            (0.46, 0.14, "w"),
            (0.60, 0.20, "w"),
            (0.80, 0.20, "w"),
        ]

        for idx, item in enumerate(self.itens_lista):
            preco_fmt = f"R$ {item['preco_unitario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            subtotal_fmt = f"R$ {item['subtotal']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            row_frame = ctk.CTkFrame(self.table_body, fg_color="transparent")
            row_frame.pack(fill="x")

            linha = ctk.CTkFrame(row_frame, fg_color="white", corner_radius=0,
                                 border_width=1, border_color=COLORS["border"])
            linha.pack(fill="x", padx=1, pady=(1, 0))
            linha.configure(height=32)
            linha.pack_propagate(False)

            valores = [item["nome"], str(item["quantidade"]), preco_fmt, subtotal_fmt]

            for (rx, rw, anchor), texto in zip(col_cfg, valores):
                ctk.CTkLabel(
                    linha, text=texto,
                    font=ctk.CTkFont(size=FONTS["size_small"]),
                    text_color=COLORS["text"], anchor=anchor,
                ).place(relx=rx, relwidth=rw, rely=0, relheight=1)

            def _selecionar(i=idx, frame=linha):
                for w in self.table_body.winfo_children():
                    for c in w.winfo_children():
                        c.configure(fg_color="white")
                frame.configure(fg_color=COLORS["primary_light"])
                self.item_selecionado_idx = i

            linha.bind("<Button-1>", lambda e, i=idx, f=linha: _selecionar(i, f))
            for child in linha.winfo_children():
                child.bind("<Button-1>", lambda e, i=idx, f=linha: _selecionar(i, f))

        self.item_selecionado_idx = None
        total_geral = sum(item["subtotal"] for item in self.itens_lista)
        total_fmt = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_total_geral.configure(text=f"Total Itens: {total_fmt}")

    def _build_upload_section(self):
        upload_card = ctk.CTkFrame(
            self.scroll, fg_color=COLORS["white"], corner_radius=6,
            border_width=1, border_color=COLORS["border"]
        )
        upload_card.pack(fill="x", padx=30, pady=(10, 0))

        row = ctk.CTkFrame(upload_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(10, 8))

        ctk.CTkLabel(
            row, text="Anexar arquivo da Nota Fiscal *",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        self.btn_anexar = ctk.CTkButton(
            row, text="ANEXAR PDF", height=36, corner_radius=6,
            fg_color="#CC0000", hover_color="#AA0000",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            command=self._selecionar_arquivo,
        )
        self.btn_anexar.pack(side="right")

        self.btn_limpar = ctk.CTkButton(
            row, text="REMOVER ANEXO", height=36, corner_radius=6,
            fg_color="#CC0000", hover_color="#AA0000",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=140,
            command=self._limpar_arquivo,
        )
        self.btn_limpar.pack(side="right", padx=(0, 8))

        self.lbl_arquivo = ctk.CTkFrame(
            upload_card, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"],
            height=30,
        )
        self.lbl_arquivo.pack(fill="x", padx=20, pady=(0, 12))
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
            self.item_selecionado_idx = None
            for item_pdf in dados['itens']:
                item_match = None
                for item_tccm in self.itens_tccm:
                    if item_tccm['nome'].lower() in item_pdf['nome'].lower() or \
                       item_pdf['nome'].lower() in item_tccm['nome'].lower():
                        item_match = item_tccm
                        break

                self.itens_lista.append({
                    "item_id": item_match["id"] if item_match else None,
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
        btn_container.pack(fill="x", padx=30, pady=(14, 20))

        ctk.CTkButton(
            btn_container, text="Enviar para Agente", height=40, corner_radius=6,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            width=200,
            command=self._salvar,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_container, text="  Limpar Tudo", height=40, corner_radius=6,
            fg_color=COLORS["success_dark"], hover_color=COLORS["success_dark_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            width=140,
            command=self._limpar_campos,
        ).pack(side="left")


    def _salvar(self):
        numero = self.entry_numero.get().strip()
        chave = self.entry_chave.get().strip()
        data_str = self.entry_data.get().strip()
        processo = self._get_processo_real()

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

        arquivo_path = None
        if self.arquivo_selecionado:
            try:
                os.makedirs(ANEXOS_DIR, exist_ok=True)
                ext = os.path.splitext(self.arquivo_selecionado)[1] or ".pdf"
                nome_arquivo = f"{numero}{ext}"
                destino = os.path.join(ANEXOS_DIR, nome_arquivo)
                shutil.copy2(self.arquivo_selecionado, destino)
                arquivo_path = destino
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar o arquivo anexado:\n{e}")
                return

        try:
            if self.nota_edicao:
                valor_total = self.service.reenviar_nota(
                    self.nota_edicao["nota_fiscal"], processo, self.id_infrator,
                    {
                        "numero": numero,
                        "chave": chave,
                        "data": data,
                        "arquivo": arquivo_path or self.nota_edicao.get("arquivo"),
                    }, self.itens_lista,
                )
            else:
                valor_total = self.service.salvar(
                    numero,
                    chave,
                    data_str,
                    processo,
                    self.itens_lista,
                    arquivo_path,
                    usuario_id=self.id_infrator,
                )
            messagebox.showinfo("Sucesso",
                f"Nota fiscal {'reenviada' if self.nota_edicao else 'enviada'} para o agente responsavel pela validacao!\n"
                f"Valor Total: R$ {valor_total:,.2f}\n"
                f"Itens: {len(self.itens_lista)}")
            self._limpar_campos()
            if self.nota_edicao and self.on_voltar:
                self.on_voltar()
        except RegraNotaError as exc:
            messagebox.showwarning("Atencao", str(exc))
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao salvar nota fiscal:\n{exc}")

    def _limpar_arquivo(self):
        self.arquivo_selecionado = None
        self.lbl_arquivo_text.configure(text="Nenhum arquivo anexado")

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
