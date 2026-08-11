"""Componentes visuais reutilizaveis do FISCSOFT."""

import os

import customtkinter as ctk
from PIL import Image, ImageTk

from config.styles import ASSETS_DIR


class ComboBoxComSeta(ctk.CTkComboBox):
    """CTkComboBox que exibe a seta padrao visual do FISCSOFT."""

    def __init__(self, *args, **kwargs):
        caminho_seta = os.path.join(ASSETS_DIR, "arrow2.png")
        with Image.open(caminho_seta) as imagem:
            self._imagem_seta_original = imagem.convert("RGBA")

        self._imagem_seta_tk = None
        self._id_imagem_seta = None
        super().__init__(*args, **kwargs)

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        self._canvas.itemconfigure("dropdown_arrow", state="hidden")
        self._desenhar_imagem_seta()

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
