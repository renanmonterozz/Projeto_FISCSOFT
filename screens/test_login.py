import _path

import os
import sys
from tkinter import messagebox

from PIL import Image
import customtkinter as ctk

from config.styles import ASSETS_DIR, COLORS

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class TestLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FISCSOFT - Login (Teste)")
        self.geometry("1280x860")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["white"])
        self.mostrando_form = False

        try:
            self.img_bg = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "login.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "login.png")),
                size=(1280, 860),
            )
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.img_bg = None

        self.bg_label = ctk.CTkLabel(self, text="", image=self.img_bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.image = self.img_bg

        self.form_frame = None

        self.bg_label.bind("<Button-1>", self.clique_bg)

    def clique_bg(self, event):
        if self.mostrando_form:
            return
        x, y = event.x, event.y
        if 850 <= x <= 1200 and 300 <= y <= 450:
            self.mostrar_formulario()
        elif 850 <= x <= 1200 and 470 <= y <= 600:
            self.login_certificado()

    def mostrar_formulario(self):
        if self.mostrando_form:
            self.voltar_menu()
            return
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=320, height=280)
        self.form_frame.place(x=870, y=300)

        frame_user = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=4, border_width=1, border_color=COLORS["border"])
        frame_user.pack(pady=(10, 8), padx=30, fill="x")
        frame_user.pack_propagate(False)
        frame_user.configure(height=42)

        ctk.CTkLabel(frame_user, text="\U0001f464", font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]).pack(side="left", padx=(12, 5))
        self.entry_usuario = ctk.CTkEntry(
            frame_user,
            placeholder_text="Usuario",
            height=38,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_usuario.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        frame_senha = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=4, border_width=1, border_color=COLORS["border"])
        frame_senha.pack(pady=8, padx=30, fill="x")
        frame_senha.pack_propagate(False)
        frame_senha.configure(height=42)

        ctk.CTkLabel(frame_senha, text="\U0001f512", font=ctk.CTkFont(size=16), text_color=COLORS["text_muted"]).pack(side="left", padx=(12, 5))
        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Senha",
            show="*",
            height=38,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color=COLORS["text_muted"],
        )
        self.entry_senha.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        self.entry_usuario.bind("<Return>", lambda e: self.fazer_login())
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())
        self.bind("<Return>", lambda e: self.fazer_login())

        ctk.CTkButton(
            self.form_frame,
            text="Entrar",
            height=40,
            corner_radius=4,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.fazer_login,
        ).pack(pady=(18, 6), padx=30, fill="x")

        ctk.CTkButton(
            self.form_frame,
            text="Sair",
            height=30,
            corner_radius=4,
            fg_color=COLORS["dark"],
            hover_color=COLORS["dark_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=4, padx=30, fill="x")

    def voltar_menu(self):
        self.mostrando_form = False
        self.unbind("<Return>")
        if self.form_frame:
            self.form_frame.destroy()
            self.form_frame = None

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showwarning("Atencao", "Preencha todos os campos!")
            return

        messagebox.showinfo("Teste", f"Login: {usuario}\n(Senha oculta)\n\nConexao com BD nao implementada neste teste.")

    def login_certificado(self):
        if self.mostrando_form:
            self.voltar_menu()
            return
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=320, height=280)
        self.form_frame.place(x=870, y=300)

        ctk.CTkLabel(
            self.form_frame,
            text="\U0001f510",
            font=ctk.CTkFont(size=40),
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            self.form_frame,
            text="Funcionalidade em\ndesenvolvimento",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_muted"],
        ).pack(pady=10)

        ctk.CTkButton(
            self.form_frame,
            text="Voltar",
            height=32,
            corner_radius=4,
            fg_color=COLORS["dark"],
            hover_color=COLORS["dark_hover"],
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=(20, 10))


if __name__ == "__main__":
    app = TestLoginApp()
    app.mainloop()
