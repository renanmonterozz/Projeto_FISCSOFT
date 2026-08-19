"""Componentes visuais reutilizaveis do FISCSOFT."""

import os

import calendar as cal_mod
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

from config.styles import ASSETS_DIR, COLORS, FONTS


class ComboBoxComSeta(ctk.CTkComboBox):
    """CTkComboBox que exibe a seta padrao visual do FISCSOFT."""

    def __init__(self, *args, **kwargs):
        caminho_seta = os.path.join(ASSETS_DIR, "arrow2.png")
        with Image.open(caminho_seta) as imagem:
            self._imagem_seta_original = imagem.convert("RGBA")

        self._imagem_seta_tk = None
        self._id_imagem_seta = None
        super().__init__(*args, **kwargs)
        self.after(100, self._desenhar_imagem_seta)

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        try:
            self._canvas.itemconfigure("dropdown_arrow", state="hidden")
        except Exception:
            pass
        self.after(100, self._desenhar_imagem_seta)

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        self.after(100, self._desenhar_imagem_seta)
        return self

    def set(self, value):
        super().set(value)
        self.after(100, self._desenhar_imagem_seta)
        return self

    def _desenhar_imagem_seta(self):
        altura = max(10, min(14, int(self._apply_widget_scaling(self._current_height * 0.38))))
        largura = max(1, round(altura * self._imagem_seta_original.width / self._imagem_seta_original.height))
        imagem = self._imagem_seta_original.resize((largura, altura), Image.Resampling.LANCZOS)
        self._imagem_seta_tk = ImageTk.PhotoImage(imagem)

        x = self._apply_widget_scaling(self._current_width - self._current_height / 2)
        y = self._apply_widget_scaling(self._current_height / 2)

        if self._id_imagem_seta is None:
            self._id_imagem_seta = self._canvas.create_image(
                x, y, image=self._imagem_seta_tk, tags="imagem_seta_combobox"
            )
            self._canvas.tag_bind("imagem_seta_combobox", "<Enter>", self._on_enter)
            self._canvas.tag_bind("imagem_seta_combobox", "<Leave>", self._on_leave)
            self._canvas.tag_bind("imagem_seta_combobox", "<Button-1>", self._clicked)
        else:
            self._canvas.coords(self._id_imagem_seta, x, y)
            self._canvas.itemconfigure(self._id_imagem_seta, image=self._imagem_seta_tk)


class CalendarioPopup(ctk.CTkToplevel):
    def __init__(self, master, title="Selecionar Periodo", on_confirm=None):
        super().__init__(master)
        self.title(title)
        self.geometry("420x480+{}+{}".format(
            (self.winfo_screenwidth() - 420) // 2,
            (self.winfo_screenheight() - 480) // 2
        ))
        self.resizable(False, False)
        self.configure(fg_color=COLORS["white"])
        self.transient(master)
        self.grab_set()

        self.on_confirm = on_confirm
        self.data_inicio = None
        self.data_fim = None
        self.selecionando_fim = False

        today = date.today()
        self.mes_atual = today.month
        self.ano_atual = today.year

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            container, text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        self.lbl_selecao = ctk.CTkLabel(
            container, text="Clique na data de INICIO",
            font=ctk.CTkFont(size=FONTS["size_small"]),
            text_color=COLORS["primary"]
        )
        self.lbl_selecao.pack(anchor="w", pady=(2, 10))

        nav = ctk.CTkFrame(container, fg_color="transparent")
        nav.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            nav, text="<", width=36, height=32, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._mes_anterior
        ).pack(side="left")

        self.lbl_mes_ano = ctk.CTkLabel(
            nav, text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        )
        self.lbl_mes_ano.pack(side="left", expand=True)

        ctk.CTkButton(
            nav, text=">", width=36, height=32, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._mes_seguinte
        ).pack(side="right")

        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
        hdr = ctk.CTkFrame(container, fg_color="transparent")
        hdr.pack(fill="x")
        for d in dias_semana:
            ctk.CTkLabel(
                hdr, text=d, width=48, height=28,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(side="left", expand=True)

        self.frame_dias = ctk.CTkFrame(container, fg_color="transparent")
        self.frame_dias.pack(fill="both", expand=True, pady=(4, 0))

        self.lbl_datas = ctk.CTkLabel(
            container, text="Inicio: --/--/----  Fim: --/--/----",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text"]
        )
        self.lbl_datas.pack(pady=(10, 5))

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            btns, text="Limpar", height=34, corner_radius=4,
            fg_color="#6B7280", hover_color="#4B5563",
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self._limpar
        ).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btns, text="Confirmar", height=34, corner_radius=4,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self._confirmar
        ).pack(side="right", expand=True, padx=(5, 0))

        self.btns_dias = []
        self._renderizar_calendario()

    def _mes_anterior(self):
        self.mes_atual -= 1
        if self.mes_atual < 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        self._renderizar_calendario()

    def _mes_seguinte(self):
        self.mes_atual += 1
        if self.mes_atual > 12:
            self.mes_atual = 1
            self.ano_atual += 1
        self._renderizar_calendario()

    def _renderizar_calendario(self):
        for w in self.frame_dias.winfo_children():
            w.destroy()
        self.btns_dias = []

        meses_pt = ["", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.mes_atual]} {self.ano_atual}")

        primeiro_dia, dias_no_mes = cal_mod.monthrange(self.ano_atual, self.mes_atual)

        semana = ctk.CTkFrame(self.frame_dias, fg_color="transparent")
        semana.pack(fill="x")
        self.btns_dias.append([])

        for _ in range(primeiro_dia):
            ctk.CTkLabel(semana, text="", width=48, height=32).pack(side="left", expand=True)
            self.btns_dias[-1].append(None)

        for dia in range(1, dias_no_mes + 1):
            if len(self.btns_dias[-1]) >= 7:
                semana = ctk.CTkFrame(self.frame_dias, fg_color="transparent")
                semana.pack(fill="x")
                self.btns_dias.append([])

            d = dia
            btn = ctk.CTkButton(
                semana, text=str(dia), width=48, height=32, corner_radius=4,
                fg_color="transparent", hover_color=COLORS["primary_light"],
                text_color=COLORS["text"], border_width=0,
                font=ctk.CTkFont(size=FONTS["size_small"]),
                command=lambda dia=d: self._selecionar_dia(dia)
            )
            btn.pack(side="left", expand=True)
            self.btns_dias[-1].append(btn)

        self._atualizar_destaque()

    def _selecionar_dia(self, dia):
        dt = date(self.ano_atual, self.mes_atual, dia)
        if not self.selecionando_fim:
            self.data_inicio = dt
            self.data_fim = None
            self.selecionando_fim = True
            self.lbl_selecao.configure(text="Clique na data de FIM")
        else:
            if dt < self.data_inicio:
                self.data_fim = self.data_inicio
                self.data_inicio = dt
            else:
                self.data_fim = dt
            self.selecionando_fim = False
            self.lbl_selecao.configure(text="Periodo selecionado")

        self._atualizar_destaque()
        self._atualizar_lbl_datas()

    def _atualizar_destaque(self):
        for semana in self.btns_dias:
            for btn in semana:
                if btn is None:
                    continue
                btn.configure(fg_color="transparent", text_color=COLORS["text"])

        if self.data_inicio and self.data_inicio.year == self.ano_atual and self.data_inicio.month == self.mes_atual:
            for semana in self.btns_dias:
                for btn in semana:
                    if btn is None:
                        continue
                    try:
                        if int(btn.cget("text")) == self.data_inicio.day:
                            btn.configure(fg_color=COLORS["primary"], text_color="white")
                    except Exception:
                        pass

        if self.data_fim and self.data_fim.year == self.ano_atual and self.data_fim.month == self.mes_atual:
            for semana in self.btns_dias:
                for btn in semana:
                    if btn is None:
                        continue
                    try:
                        if int(btn.cget("text")) == self.data_fim.day:
                            btn.configure(fg_color=COLORS["primary"], text_color="white")
                    except Exception:
                        pass

    def _atualizar_lbl_datas(self):
        i = self.data_inicio.strftime("%d/%m/%Y") if self.data_inicio else "--/--/----"
        f = self.data_fim.strftime("%d/%m/%Y") if self.data_fim else "--/--/----"
        self.lbl_datas.configure(text=f"Inicio: {i}  Fim: {f}")

    def _limpar(self):
        self.data_inicio = None
        self.data_fim = None
        self.selecionando_fim = False
        self.lbl_selecao.configure(text="Clique na data de INICIO")
        self._atualizar_destaque()
        self._atualizar_lbl_datas()

    def _confirmar(self):
        if not self.data_inicio or not self.data_fim:
            messagebox.showwarning("Aviso", "Selecione both data de inicio e fim.", parent=self)
            return
        if self.on_confirm:
            self.on_confirm(self.data_inicio, self.data_fim)
        self.destroy()
