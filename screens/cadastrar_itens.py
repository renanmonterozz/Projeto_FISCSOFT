import _path  # noqa: F401

import customtkinter as ctk
from tkinter import messagebox

from config.layout_system import LayoutSystem
from config.styles import COLORS, FONTS
from screens.service.itens_service import ItemService, RegraItemError, validar_dados_item
from screens.widgets import ComboBoxComSeta


class CadastrarItensWindow(ctk.CTkToplevel):
    def __init__(self, master=None, item=None, processo_tccm=None, usuario_logado=None):
        super().__init__(master)
        self.item_edicao = item
        self.processo_tccm = processo_tccm
        self.usuario_logado = usuario_logado
        self.service = ItemService()
        self.title("FISCSOFT - Cadastrar Item")
        self.geometry("820x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["border"])
        self.grab_set()

        self.build_ui()

        if self.item_edicao:
            self.preencher_campos()

    def build_ui(self):
        container = LayoutSystem.panel(
            self,
            fill="both",
            expand=True,
            padding=(20, 20),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )

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

        form = LayoutSystem.panel(
            container,
            fill="both",
            expand=True,
            padding=(25, (15, 30)),
            fg_color=COLORS["white"],
            border_color=COLORS["border"],
        )

        row1 = LayoutSystem.form_row(form, padding_x=20, padding_y=(18, 10), columns=2)
        self.entry_nome = self._criar_campo(row1, "Nome do Item*", 0, weight=3)
        self.entry_desc = self._criar_campo(row1, "Descricao", 1, weight=3)

        row2 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 10), columns=2)
        self.combo_tipo = self._criar_combobox(row2, "Tipo de Material*", 0,
                                               ["Consumivel", "Permanente"], default="Consumivel")
        self.combo_unidade = self._criar_combobox(row2, "Unidade de Medida*", 1,
                                                  ["Unidade", "Caixa", "Litro", "Kg"], default="Unidade")

        row3 = LayoutSystem.form_row(form, padding_x=20, padding_y=(0, 10), columns=2)
        self.entry_just = self._criar_campo(row3, "Justificativa*", 0, weight=3)
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
        return LayoutSystem.field(
            parent,
            label.rstrip("*"),
            column=col,
            weight=weight,
            required=label.endswith("*"),
        )

    def _criar_combobox(self, parent, label, col, values, default=None):
        return LayoutSystem.combobox_field(
            parent,
            label.rstrip("*"),
            values,
            column=col,
            weight=1,
            default=default if default is not None else values[0],
            border_width=1,
            button_color=COLORS["border"],
            button_hover_color=COLORS["hover"],
            dropdown_fg_color=COLORS["white"],
            text_color=COLORS["text"],
        )

    def salvar(self):
        try:
            dados = validar_dados_item(
                self.entry_nome.get(),
                self.entry_desc.get(),
                self.combo_tipo.get(),
                self.combo_unidade.get(),
                self.entry_just.get(),
                self.entry_qtd.get(),
            )
        except RegraItemError as exc:
            if "inteiro" in str(exc):
                messagebox.showerror("Erro", str(exc), parent=self)
            else:
                messagebox.showwarning("Atencao", str(exc), parent=self)
            return

        try:
            mensagem = self.service.salvar(
                dados,
                item_id=self.item_edicao["id"] if self.item_edicao else None,
                processo=self.processo_tccm,
                usuario_logado=self.usuario_logado,
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Nao foi possivel salvar o item:\n{exc}", parent=self)
            return

        messagebox.showinfo("Sucesso", mensagem, parent=self)
        self.destroy()
