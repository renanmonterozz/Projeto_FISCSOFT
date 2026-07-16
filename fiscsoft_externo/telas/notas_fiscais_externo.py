import sys
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk

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

        self._build_header()
        self._build_form()
        self._build_upload_section()
        self._build_action_buttons()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 5))

        ctk.CTkLabel(
            header, text="Cadastrar Nota Fiscal",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text="Informe os dados da Nota Fiscal.",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def _build_form(self):
        form_card = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=6,
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

        col_produto = ctk.CTkFrame(row_meio, fg_color="transparent")
        col_produto.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            col_produto, text="Essa nota possui mais de um produto?",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 4))

        btn_frame = ctk.CTkFrame(col_produto, fg_color="transparent")
        btn_frame.pack(anchor="w")

        self.var_multi_produto = tk.StringVar(value="N")
        self.btn_sim = ctk.CTkButton(
            btn_frame, text="S", width=40, height=36, corner_radius=4,
            fg_color=COLORS["white"], hover_color=COLORS["primary_light"],
            text_color=COLORS["text"], border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=lambda: self._toggle_multi("S"),
        )
        self.btn_sim.pack(side="left", padx=(0, 4))

        self.btn_nao = ctk.CTkButton(
            btn_frame, text="N", width=40, height=36, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            command=lambda: self._toggle_multi("N"),
        )
        self.btn_nao.pack(side="left")

        self.entry_valor = self._criar_campo(form_card, "Valor Total da Nota Fiscal(R$)*")

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

    def _toggle_multi(self, valor):
        self.var_multi_produto.set(valor)
        if valor == "S":
            self.btn_sim.configure(fg_color=COLORS["primary"], text_color="white", border_width=0)
            self.btn_nao.configure(fg_color=COLORS["white"], text_color=COLORS["text"], border_width=1, border_color=COLORS["border"])
        else:
            self.btn_nao.configure(fg_color=COLORS["primary"], text_color="white", border_width=0)
            self.btn_sim.configure(fg_color=COLORS["white"], text_color=COLORS["text"], border_width=1, border_color=COLORS["border"])

    def _build_upload_section(self):
        upload_frame = ctk.CTkFrame(self, fg_color="transparent")
        upload_frame.pack(fill="x", padx=40, pady=(25, 0))

        ctk.CTkLabel(
            upload_frame, text="Anexar arquivo da Nota Fiscal *",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 10))

        btn_row = ctk.CTkFrame(upload_frame, fg_color="transparent")
        btn_row.pack(fill="x")

        self.btn_ler_pdf = ctk.CTkButton(
            btn_row, text="LER E ANEXAR PDF", height=70, corner_radius=8,
            fg_color="#CC0000", hover_color="#AA0000",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._ler_e_anexar_pdf,
        )
        self.btn_ler_pdf.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_anexar = ctk.CTkButton(
            btn_row, text="ANEXAR\nSEM LER", height=70, corner_radius=8,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            command=self._selecionar_arquivo,
        )
        self.btn_anexar.pack(side="right")

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

    def _ler_e_anexar_pdf(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Nota Fiscal para leitura automatica",
            filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        self.arquivo_selecionado = caminho
        nome = os.path.basename(caminho)
        tamanho = os.path.getsize(caminho)
        tamanho_kb = f"{tamanho / 1024:.1f} KB"
        self.lbl_arquivo_text.configure(text=f" Lendo {nome}...")

        try:
            dados = self._extrair_dados_pdf(caminho)
        except Exception as e:
            self.lbl_arquivo_text.configure(text=f"{nome}  ({tamanho_kb})")
            messagebox.showwarning(
                "Atencao",
                f"Nao foi possivel ler o PDF automaticamente.\n{e}\n\n"
                "Anexo salvo. Preencha os campos manualmente.",
            )
            return

        campos_preenchidos = 0
        if dados.get("numero"):
            self.entry_numero.delete(0, "end")
            self.entry_numero.insert(0, dados["numero"])
            campos_preenchidos += 1
        if dados.get("chave"):
            self.entry_chave.delete(0, "end")
            self.entry_chave.insert(0, dados["chave"])
            campos_preenchidos += 1
        if dados.get("data"):
            self.entry_data.delete(0, "end")
            self.entry_data.insert(0, dados["data"])
            campos_preenchidos += 1
        if dados.get("valor"):
            self.entry_valor.delete(0, "end")
            self.entry_valor.insert(0, dados["valor"])
            campos_preenchidos += 1

        self.lbl_arquivo_text.configure(text=f"{nome}  ({tamanho_kb})  -  {campos_preenchidos} campo(s) preenchido(s)")

        if campos_preenchidos > 0:
            messagebox.showinfo(
                "Leitura concluida",
                f"Campos preenchidos automaticamente: {campos_preenchidos}/4\n\n"
                "Revise os dados e clique em Salvar.",
            )
        else:
            messagebox.showwarning(
                "Atencao",
                "Nenhum campo foi reconhecido no PDF.\n"
                "Preencha os campos manualmente.",
            )

    def _extrair_dados_pdf(self, caminho):
        from pypdf import PdfReader

        reader = PdfReader(caminho)
        texto = "\n".join(page.extract_text() or "" for page in reader.pages)
        texto_lower = texto.lower()

        dados = {"numero": None, "chave": None, "data": None, "valor": None}

        m = re.search(r'nfe\s*n\.\s*(\d+)', texto, re.IGNORECASE)
        if not m:
            m = re.search(r'numero[:\s]+(\d+)', texto, re.IGNORECASE)
        if m:
            dados["numero"] = m.group(1)

        m = re.search(r'chave\s+de\s+acesso[:\s]+(\d{44})', texto, re.IGNORECASE)
        if not m:
            m = re.search(r'chave[:\s]+(\d{44})', texto, re.IGNORECASE)
        if not m:
            m = re.search(r'(\d{44})', texto)
        if m:
            dados["chave"] = m.group(1)

        m = re.search(
            r'data\s+de\s+(?:emiss[aã]o|emissao)[:\s]+(\d{2}/\d{2}/\d{4})',
            texto, re.IGNORECASE,
        )
        if not m:
            m = re.search(r'data[:\s]+(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if m:
            dados["data"] = m.group(1)

        m = re.search(
            r'valor\s+total\s+(?:da\s+nota|dos?\s+produtos?)[:\s]*r?\$?\s*([\d.,]+)',
            texto, re.IGNORECASE,
        )
        if not m:
            m = re.search(
                r'(?:total|valor\s+total)[:\s]*r?\$?\s*([\d.,]+)',
                texto, re.IGNORECASE,
            )
        if m:
            dados["valor"] = m.group(1).strip()

        return dados

    def _build_action_buttons(self):
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
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
        valor_str = self.entry_valor.get().strip()

        if not numero or not chave or not data_str or not valor_str:
            messagebox.showwarning("Atencao", "Preencha todos os campos obrigatorios.")
            return

        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atencao", "Data invalida. Use o formato dd/mm/aaaa.")
            return

        try:
            valor = float(valor_str.replace(".", "").replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atencao", "Valor invalido.")
            return

        with Database() as db:
            if not db.conexao:
                messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados.")
                return

            try:
                sql_mat = '''SELECT "agente ibama_matricula"
                             FROM tccm WHERE "infrator_id_infrator" = ?
                             LIMIT 1'''
                resultado = db.executar(sql_mat, (self.id_infrator,))
                row = resultado.fetchone() if resultado else None
                matricula = row[0] if row else 0

                sql = """INSERT INTO "nota fiscal"
                         (nota_fiscal, semestre, data, chave_de_acesso, valor_total,
                          "agente ibama_matricula", status_nota)
                         VALUES (?, ?, ?, ?, ?, ?, 'Pendente')"""
                db.executar(sql, (numero, 1, data, chave, valor, matricula))
                db.commitar()
                messagebox.showinfo("Sucesso", "Nota fiscal cadastrada com sucesso!")
                self._limpar_campos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar nota fiscal:\n{e}")

    def _limpar_campos(self):
        self.entry_numero.delete(0, "end")
        self.entry_chave.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.arquivo_selecionado = None
        self.lbl_arquivo_text.configure(text="Nenhum arquivo anexado")

    def _voltar(self):
        if self.on_voltar:
            self.on_voltar()
