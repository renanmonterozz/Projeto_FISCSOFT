import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: F401 — garante o root do projeto no sys.path
import pywinstyles

import os
from tkinter import messagebox

from PIL import Image

import customtkinter as ctk

from config.styles import ASSETS_DIR, COLORS
from screens.service.login_service import RegraLoginError, validar_credenciais

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Cores
DOURADO = "#c8b464"
AMARELO_BOTAO = "#FFF48C"
VERDE_POLIGONO = "#302F2F"


class TestLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FISCSOFT - Login (Teste)")
        self.configure(fg_color=COLORS["white"])
        self.after(0, self.state, "zoomed")

        # --- Imagem de fundo ---
        img_path = os.path.join(ASSETS_DIR, "Tela_Loginn.png")
        self._img_pil = None
        try:
            self._img_pil = Image.open(img_path)
        except Exception:
            self._img_pil = None

        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.after(100, self._ajustar_imagem_fundo)

        # --- Texto "ACESSE O SISTEMA!" ---
        self.label_titulo = ctk.CTkLabel(
            self,
            text="ACESSE O SISTEMA!",
            font=("Libre Baskerville", 36),
            text_color="#FFF9BE",
            fg_color="#000001",
            bg_color="#000001"
        )
        self.label_titulo.place(relx=0.5, rely=0.78, anchor="center")

        pywinstyles.set_opacity(self.label_titulo, color="#000001")

        # --- Botão 1: Entrar com Usuário e Senha ---
        self.btn_usuario = ctk.CTkButton(
            self,
            text="Entrar com Usuário e Senha",
            width=480,
            height=50,
            corner_radius=16,
            fg_color=VERDE_POLIGONO,
            bg_color="#000001",
            hover_color="#211E1E",
            text_color=AMARELO_BOTAO,
            font=ctk.CTkFont(family="Segoe UI", size=19),
            border_width=2,
            border_color="#000001",
            command=self._on_usuario_click
        )
        self.btn_usuario.place(relx=0.5, rely=0.86, anchor="center")
        pywinstyles.set_opacity(self.btn_usuario, color="#000001")


        # --- Botão 2: Entrar com Certificado Digital ---
        self.btn_certificado = ctk.CTkButton(
            self,
            text="Entrar com Certificado Digital",
            width=480,
            height=50,
            corner_radius=16,
            fg_color=VERDE_POLIGONO,
            bg_color="#000001",
            hover_color="#211E1E",
            text_color=AMARELO_BOTAO,
            font=ctk.CTkFont(family="Segoe UI", size=19),
            border_width=2,
            border_color="#000001",
            command=self._on_certificado_click
        )
        self.btn_certificado.place(relx=0.5, rely=0.93, anchor="center")
        pywinstyles.set_opacity(self.btn_certificado, color="#000001")


    def _ajustar_imagem_fundo(self):
        if self._img_pil is None:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            self.after(100, self._ajustar_imagem_fundo)
            return

        img_w, img_h = self._img_pil.size
        scale = max(w / img_w, h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized = self._img_pil.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        cropped = resized.crop((left, top, left + w, top + h))

        img = ctk.CTkImage(light_image=cropped, dark_image=cropped, size=(w, h))
        self.bg_label.configure(image=img)
        self.bg_label.image = img

    def _mostrar_formulario_login(self):
        # Frame para o formulário
        self.frame_login = ctk.CTkFrame(self, fg_color="#000001", bg_color="#000001", corner_radius=0)
        self.frame_login.place(relx=0.5, rely=0.90, anchor="center")
        self.frame_login.lift()
        pywinstyles.set_opacity(self.frame_login, color="#000001")

        # Entry - Usuário
        self.entry_usuario = ctk.CTkEntry(
            self.frame_login,
            width=480,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3",
            border_color="#16A34A",
            border_width=2,
            text_color="#2D8A4E",
            placeholder_text_color="#2D8A4E",
            placeholder_text="Digite seu usuário"
        )
        self.entry_usuario.pack(pady=(10, 10))

        # Frame wrapper para senha (campo + olho lado a lado)
        frame_senha = ctk.CTkFrame(self.frame_login, fg_color="transparent", width=586, height=45)
        frame_senha.pack(pady=(0, 10))
        frame_senha.pack_propagate(False)

        # Entry - Senha (centralizado, mesma posição do campo de usuário)
        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            width=480,
            height=45,
            corner_radius=8,
            font=("Segoe UI", 16),
            fg_color="#CFFFE3",
            border_color="#16A34A",
            border_width=2,
            text_color="#2D8A4E",
            placeholder_text_color="#2D8A4E",
            placeholder_text="Digite sua senha",
            show="*"
        )
        self.entry_senha.place(x=53, y=0)

        # Botão do olho (place: ao lado do campo, dentro do frame)
        self.btn_eye = ctk.CTkButton(
            frame_senha,
            text="👁",
            width=45,
            height=45,
            corner_radius=8,
            fg_color="#CFFFE3",
            hover_color="#b0e8c0",
            text_color="#2D8A4E",
            font=("Segoe UI", 18),
            border_width=2,
            border_color="#16A34A",
            command=self._toggle_senha
        )
        self.btn_eye.place(x=541, y=0)

        # Estado da visibilidade da senha
        self._senha_visivel = False

        # Botões em uma linha
        frame_botoes = ctk.CTkFrame(self.frame_login, fg_color="#000001")
        frame_botoes.pack()
        # Botão Entrar
        btn_entrar = ctk.CTkButton(
            frame_botoes,
            text="Entrar",
            width=100,
            height=40,
            corner_radius=12,
            fg_color=VERDE_POLIGONO,
            hover_color="#211E1E",
            text_color=AMARELO_BOTAO,
            font=("Segoe UI", 16),
            command=self._on_entrar_click
        )
        btn_entrar.pack(side="left", padx=5)

        # Botão Sair
        btn_sair = ctk.CTkButton(
            frame_botoes,
            text="Sair",
            width=100,
            height=40,
            corner_radius=12,
            fg_color="#8B0000",
            hover_color="#850202",
            text_color="white",
            font=("Segoe UI", 16),
            command=self._on_sair_click
        )
        btn_sair.pack(side="left", padx=5)

    def _on_entrar_click(self):
        try:
            usuario, _ = validar_credenciais(
                self.entry_usuario.get(),
                self.entry_senha.get(),
            )
        except RegraLoginError as exc:
            messagebox.showwarning("Aviso", str(exc), parent=self)
            return

        print(f"Usuário: {usuario}")

    def _on_sair_click(self):
        # Oculta o frame de login
        self.frame_login.place_forget()
        # Mostra novamente os botões iniciais
        self.btn_usuario.place(relx=0.5, rely=0.86, anchor="center")
        self.btn_certificado.place(relx=0.5, rely=0.93, anchor="center")

    def _toggle_senha(self):
        # Alterna a visibilidade da senha
        if self._senha_visivel:
            self.entry_senha.configure(show="*")
            self.btn_eye.configure(text="👁")
            self._senha_visivel = False
        else:
            self.entry_senha.configure(show="")
            self.btn_eye.configure(text="👁")
            self._senha_visivel = True

    def _on_usuario_click(self):
        # Esconde os botões iniciais
        self.btn_usuario.place_forget()
        self.btn_certificado.place_forget()

        # Mostra o formulário de login
        self._mostrar_formulario_login()

    def _on_certificado_click(self):
        print("Clicou em: Entrar com Certificado Digital")


if __name__ == "__main__":
    app = TestLoginApp()
    app.mainloop()
