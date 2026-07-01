import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from datetime import datetime

from screens.sidebar import Sidebar
from screens.usuarios import UsuariosPage
from screens.itens import ItensPage
from screens.infratores import InfratoresPage
from config.styles import ASSETS_DIR, COLORS
from database.connection import Database

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FISCSOFT - Login")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["white"])
        self.mostrando_form = False

        try:
            self.img_bg = ctk.CTkImage(
                light_image=Image.open(os.path.join(ASSETS_DIR, "tela_de_login_adm.png")),
                dark_image=Image.open(os.path.join(ASSETS_DIR, "tela_de_login_adm.png")),
                size=(1000, 600),
            )
        except Exception:
            self.img_bg = None

        self.bg_label = ctk.CTkLabel(self, text="", image=self.img_bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.image = self.img_bg

        self.bg_label.bind("<Button-1>", self.on_click)

        self.form_frame = None

    def on_click(self, event):
        if self.mostrando_form:
            self.voltar_menu()
            return
        x, y = event.x, event.y

        if 650 < x < 970 and 240 < y < 360:
            self.mostrar_formulario()
        elif 650 < x < 970 and 370 < y < 490:
            self.login_certificado()

    def mostrar_formulario(self):
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=300, height=270)
        self.form_frame.place(x=660, y=290)

        frame_user = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#bbbbbb")
        frame_user.pack(pady=(10, 8), padx=25, fill="x")
        frame_user.pack_propagate(False)
        frame_user.configure(height=40)

        ctk.CTkLabel(frame_user, text="\U0001f464", font=ctk.CTkFont(size=16), text_color="#999999").pack(side="left", padx=(12, 5))
        self.entry_usuario = ctk.CTkEntry(
            frame_user,
            placeholder_text="Usuario",
            height=36,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color="#aaaaaa",
        )
        self.entry_usuario.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        frame_senha = ctk.CTkFrame(self.form_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#bbbbbb")
        frame_senha.pack(pady=8, padx=25, fill="x")
        frame_senha.pack_propagate(False)
        frame_senha.configure(height=40)

        ctk.CTkLabel(frame_senha, text="\U0001f512", font=ctk.CTkFont(size=16), text_color="#999999").pack(side="left", padx=(12, 5))
        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Senha",
            show="*",
            height=36,
            border_width=0,
            fg_color="white",
            text_color="black",
            placeholder_text_color="#aaaaaa",
        )
        self.entry_senha.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=2)

        ctk.CTkButton(
            self.form_frame,
            text="Entrar",
            height=38,
            corner_radius=8,
            fg_color="#66BB6A",
            hover_color="#43A047",
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.fazer_login,
        ).pack(pady=(18, 6), padx=25, fill="x")

        ctk.CTkButton(
            self.form_frame,
            text="Sair",
            height=28,
            corner_radius=6,
            fg_color="#2c2c2c",
            hover_color="#555555",
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=4, padx=25, fill="x")

    def voltar_menu(self):
        self.mostrando_form = False
        if self.form_frame:
            self.form_frame.destroy()
            self.form_frame = None

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showwarning("Atencao", "Preencha todos os campos!")
            return

        db = Database()
        if db.conectar():
            sql = "SELECT nome_agente, status FROM `agente ibama` WHERE login = %s AND senha = %s"
            resultado = db.executar(sql, (usuario, senha))
            registro = resultado.fetchone() if resultado else None
            db.desconectar()

            if registro:
                if registro[1] == "ativo":
                    self.usuario_logado = registro[0]
                    self.abrir_principal()
                else:
                    messagebox.showerror("Erro", "Usuario inativo! Contate o administrador.")
            else:
                messagebox.showerror("Erro", "Usuario ou senha incorretos!")
        else:
            messagebox.showerror("Erro", "Nao foi possivel conectar ao banco de dados!")

    def abrir_principal(self):
        self.destroy()

        main_app = ctk.CTk()
        main_app.title("FISCSOFT")
        main_app.geometry("1200x700")
        main_app.configure(fg_color=COLORS["white"])
        main_app.usuario_logado = self.usuario_logado

        content_frame = ctk.CTkFrame(main_app, fg_color=COLORS["bg"])
        content_frame.pack(side="right", fill="both", expand=True)

        def navegar(pagina):
            for w in content_frame.winfo_children():
                w.destroy()
            if pagina == "Usuarios Externos":
                UsuariosPage(content_frame).pack(fill="both", expand=True)
            elif pagina == "Itens":
                ItensPage(content_frame, on_voltar=lambda: navegar("Menu Inicial")).pack(fill="both", expand=True)
            elif pagina == "Agente Ibama":
                InfratoresPage(content_frame).pack(fill="both", expand=True)
            else:
                ctk.CTkLabel(
                    content_frame,
                    text=pagina,
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=COLORS["text"],
                ).pack(expand=True)

        sidebar = Sidebar(main_app, width=210, on_navigate=navegar)
        sidebar.pack(side="left", fill="y")

        navegar("Usuarios Externos")
        main_app.mainloop()

    def login_certificado(self):
        self.mostrando_form = True

        self.form_frame = ctk.CTkFrame(self.bg_label, fg_color="transparent", width=300, height=270)
        self.form_frame.place(x=660, y=290)

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
            height=30,
            corner_radius=6,
            fg_color="#2c2c2c",
            hover_color="#555555",
            text_color="white",
            border_width=0,
            font=ctk.CTkFont(size=12),
            command=self.voltar_menu,
        ).pack(pady=(20, 10))


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
