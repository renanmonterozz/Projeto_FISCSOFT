import customtkinter as ctk

from config.styles import COLORS, FONTS
from config.permissoes import pode_acao
from database.conexaodb import Database
from screens.crud_base import CrudBase
from screens.tccm_dashboard import ModalCadastrarTCCM, _fmt_brl, COL_TCCM_CFG


class TccmDashboardPage(CrudBase, ctk.CTkFrame):
	def __init__(self, master, usuario_logado=None, perfil="admin", **kwargs):
		self.on_selecionar = kwargs.pop("on_selecionar", None)
		self.on_sair = kwargs.pop("on_sair", None)
		self.on_cadastrar = kwargs.pop("on_cadastrar", None)
		super().__init__(master, **kwargs)
		self.configure(fg_color=COLORS["bg"])
		self.usuario_logado = usuario_logado
		self.perfil = perfil
		self.is_post_login = True
		self.pode_criar_tccm = pode_acao(perfil, "criar_tccm")

		self.tccms_todos = []

		self._build_header_custom()
		self._build_status_cards()
		self._build_lista_tccms()

	def _build_header_custom(self):
		header = ctk.CTkFrame(self, fg_color="transparent")
		header.pack(fill="x", padx=30, pady=(25, 15))

		left = ctk.CTkFrame(header, fg_color="transparent")
		left.pack(side="left")

		ctk.CTkLabel(left, text="Painel Geral",
					  font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
					  text_color=COLORS["text"]).pack(side="left")

		ctk.CTkLabel(left, text="  Visão consolidada do controle de Termo de Cooperação e Controle de Multas",
					  font=ctk.CTkFont(size=FONTS["size_subtitle"]),
					  text_color=COLORS["text_muted"]).pack(side="left", padx=(8, 0))

		right = ctk.CTkFrame(header, fg_color="transparent")
		right.pack(side="right")

		self.build_alerta_nota(right, pack_direction="right")

		if self.pode_criar_tccm:
			ctk.CTkButton(
				right, text="+ Novo TCCM", height=36, corner_radius=6,
				fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
				text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
				command=self._navegar_cadastro,
			).pack(side="left", padx=(0, 8))

		ctk.CTkButton(
			right, text="Sair", height=36, corner_radius=6,
			fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
			text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
			command=self._sair,
		).pack(side="left")

	def _build_status_cards(self):
		self._cards_frame = ctk.CTkFrame(self, fg_color="transparent")
		self._cards_frame.pack(fill="x", padx=30, pady=(0, 15))

		for i in range(2):
			self._cards_frame.grid_columnconfigure(i, weight=1)

		self._card_pendentes = self._criar_card_status(self._cards_frame, "Pendentes", "0", COLORS["warning"], 0)
		self._card_concluidos = self._criar_card_status(self._cards_frame, "Concluidos", "0", COLORS["success_dark"], 1)

	def _criar_card_status(self, parent, titulo, valor, cor, col):
		card = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=4,
							border_width=1, border_color=COLORS["border"])
		card.grid(row=0, column=col, padx=5, sticky="nsew")

		top = ctk.CTkFrame(card, fg_color="transparent")
		top.pack(fill="x", padx=14, pady=(12, 4))

		dot = ctk.CTkFrame(top, fg_color=cor, width=8, height=8, corner_radius=4)
		dot.pack(side="left", padx=(0, 8))
		dot.pack_propagate(False)

		ctk.CTkLabel(top, text=titulo,
					  font=ctk.CTkFont(size=FONTS["size_small"]),
					  text_color=COLORS["text_muted"]).pack(side="left")

		lbl = ctk.CTkLabel(card, text=valor,
						   font=ctk.CTkFont(size=28, weight="bold"),
						   text_color=COLORS["text"])
		lbl.pack(anchor="w", padx=14, pady=(0, 12))

		return card, lbl

	def _build_progress_section(self):
		section = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=4,
							   border_width=1, border_color=COLORS["border"])
		section.pack(fill="x", padx=30, pady=(0, 15))

		hdr = ctk.CTkFrame(section, fg_color="transparent")
		hdr.pack(fill="x", padx=15, pady=(12, 4))

		dot = ctk.CTkFrame(hdr, fg_color=COLORS["primary"], width=8, height=8, corner_radius=4)
		dot.pack(side="left", padx=(0, 8))
		dot.pack_propagate(False)

		ctk.CTkLabel(hdr, text="Progresso Geral de Arrecadacao",
					  font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
					  text_color=COLORS["text"]).pack(side="left")

		self._lbl_pct = ctk.CTkLabel(hdr, text="0%",
									  font=ctk.CTkFont(size=14, weight="bold"),
									  text_color=COLORS["primary"])
		self._lbl_pct.pack(side="right")

		bar_frame = ctk.CTkFrame(section, fg_color="transparent")
		bar_frame.pack(fill="x", padx=15, pady=(4, 4))

		self._bar_bg = ctk.CTkFrame(bar_frame, fg_color=COLORS["border"], height=12, corner_radius=6)
		self._bar_bg.pack(fill="x")
		self._bar_bg.pack_propagate(False)

		self._bar_fg = ctk.CTkFrame(self._bar_bg, fg_color=COLORS["primary"], height=12, corner_radius=6)
		self._bar_fg.place(x=0, y=0, relwidth=0, relheight=1)

		totals_frame = ctk.CTkFrame(section, fg_color="transparent")
		totals_frame.pack(fill="x", padx=15, pady=(4, 12))
		totals_frame.grid_columnconfigure(0, weight=1)
		totals_frame.grid_columnconfigure(1, weight=1)
		totals_frame.grid_columnconfigure(2, weight=1)

		self._lbl_devido = ctk.CTkLabel(totals_frame, text="Total Devido: R$ 0,00",
										 font=ctk.CTkFont(size=FONTS["size_small"]),
										 text_color=COLORS["text_muted"])
		self._lbl_devido.grid(row=0, column=0, sticky="w")

		self._lbl_pago = ctk.CTkLabel(totals_frame, text="Total Pago: R$ 0,00",
									   font=ctk.CTkFont(size=FONTS["size_small"]),
									   text_color=COLORS["text_muted"])
		self._lbl_pago.grid(row=0, column=1, sticky="w")

		self._lbl_pendente = ctk.CTkLabel(totals_frame, text="Pendente: R$ 0,00",
										   font=ctk.CTkFont(size=FONTS["size_small"]),
										   text_color=COLORS["text_muted"])
		self._lbl_pendente.grid(row=0, column=2, sticky="w")

	def _build_lista_tccms(self):
		container = ctk.CTkFrame(self, fg_color="transparent")
		container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

		header_row = ctk.CTkFrame(container, fg_color="transparent")
		header_row.pack(fill="x", pady=(0, 8))

		ctk.CTkLabel(
			header_row,
			text="Todos os TCCMs",
			font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
			text_color=COLORS["text"],
		).pack(side="left")

		self.lbl_count = ctk.CTkLabel(
			header_row, text="",
			font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
			text_color=COLORS["primary"],
		)
		self.lbl_count.pack(side="right", padx=(0, 12))

		filter_frame = ctk.CTkFrame(header_row, fg_color="transparent")
		filter_frame.pack(side="right", padx=(0, 24))

		ctk.CTkLabel(filter_frame, text="Filtrar:",
					  font=ctk.CTkFont(size=FONTS["size_small"]),
					  text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 6))

		self.entry_filtro = ctk.CTkEntry(
			filter_frame, height=32, width=220, corner_radius=6,
			border_width=1, border_color=COLORS["border"],
			fg_color=COLORS["white"], text_color=COLORS["text"],
			placeholder_text="Processo, infrator ou status...",
		)
		self.entry_filtro.pack(side="left")
		self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tccms())

		col_header = ctk.CTkFrame(container, fg_color=COLORS["table_header"], height=36, corner_radius=4)
		col_header.pack(fill="x")
		col_header.pack_propagate(False)

		cols = ctk.CTkFrame(col_header, fg_color="transparent")
		cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

		colunas = ["Processo", "Infrator", "Total Devido", "Total Pago", "Validade", "Status"]

		for texto, (rx, rw, anchor) in zip(colunas, COL_TCCM_CFG):
			ctk.CTkLabel(
				cols, text=texto,
				font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
				text_color=COLORS["text_muted"],
				anchor=anchor,
			).place(relx=rx, relwidth=rw, rely=0, relheight=1)

		self.table_body = ctk.CTkScrollableFrame(container, fg_color="transparent")
		self.table_body.pack(fill="both", expand=True)

		self._carregar_tccms()

	def _carregar_tccms(self):
		for w in self.table_body.winfo_children():
			w.destroy()

		tccms = []
		qtd_pendentes = 0
		qtd_concluidos = 0

		with Database() as db:
			if not db.conexao:
				return
			try:
				sql = """SELECT t.processo, t.total_pago, t.total_devido, t.status,
								t.data_validade, t.intervalo,
								i.nome_infrator, i.cpf
						 FROM tccm t
						 LEFT JOIN infrator i ON i.id_infrator = t."infrator_id_infrator"
						 ORDER BY t.processo"""
				r = db.executar(sql)
				if r:
					for row in r.fetchall():
						status = row[3] or "pendente"
						td = float(row[2]) if row[2] else 0
						tp = float(row[1]) if row[1] else 0

						if status == "concluido":
							qtd_concluidos += 1
						else:
							qtd_pendentes += 1

						tccms.append({
							"processo": row[0] or "--",
							"total_pago": tp,
							"total_devido": td,
							"status": status,
							"data_validade": _fmt_brl(row[4]) if False else (row[4] or "--"),
							"intervalo": row[5] or 0,
							"infrator": row[6] or "--",
							"cpf": row[7] or "--",
						})
			except Exception:
				pass

		self.tccms_todos = tccms
		self.lbl_count.configure(text=f"{len(tccms)} TCCM(s)")

		self._card_pendentes[1].configure(text=str(qtd_pendentes))
		self._card_concluidos[1].configure(text=str(qtd_concluidos))

		self._filtrar_tccms()

	def _filtrar_tccms(self):
		for w in self.table_body.winfo_children():
			w.destroy()

		termo = self.entry_filtro.get().strip().lower()
		filtrados = self.tccms_todos
		if termo:
			filtrados = [t for t in self.tccms_todos
						 if termo in t["processo"].lower()
						 or termo in t["infrator"].lower()
						 or termo in t["status"].lower()
						 or termo in t["cpf"].lower()]

		self.lbl_count.configure(text=f"{len(filtrados)} TCCM(s)")

		if not filtrados:
			ctk.CTkLabel(self.table_body, text="Nenhum TCCM encontrado",
						  font=ctk.CTkFont(size=FONTS["size_body"]),
						  text_color=COLORS["text_muted"]).pack(pady=40)
			return

		for idx, t in enumerate(filtrados):
			row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["bg"]
			row = ctk.CTkFrame(self.table_body, fg_color=row_bg, height=40,
								corner_radius=0, cursor="hand2")
			row.pack(fill="x", pady=1)
			row.pack_propagate(False)

			row.bind("<Button-1>", lambda e, proc=t["processo"]: self._selecionar(proc))

			cols = ctk.CTkFrame(row, fg_color="transparent")
			cols.pack(side="left", fill="x", expand=True, padx=(15, 0))

			if t["status"] == "concluido":
				st_text = "Concluido"
				st_cor = COLORS["success_dark"]
			elif t["status"] == "pago_parcial":
				st_text = "Parcial"
				st_cor = "#FF9800"
			else:
				st_text = "Pendente"
				st_cor = COLORS["warning"]

			dados = [
				t["processo"], t["infrator"],
				_fmt_brl(t["total_devido"]), _fmt_brl(t["total_pago"]),
				t["data_validade"], st_text,
			]
			for i, valor in enumerate(dados):
				relx, relwidth, anchor = COL_TCCM_CFG[i]
				cor = COLORS["text"] if i == 0 else (st_cor if i == 5 else COLORS["text_muted"])
				weight = "bold" if i == 0 or i == 5 else "normal"
				ctk.CTkLabel(
					cols, text=valor,
					font=ctk.CTkFont(size=FONTS["size_small"], weight=weight),
					text_color=cor, anchor=anchor,
				).place(relx=relx, relwidth=relwidth, rely=0, relheight=1)

			ctk.CTkButton(
				row, text="\u25b6", width=32, height=28,
				corner_radius=4, fg_color=COLORS["primary"],
				hover_color=COLORS["primary_hover"], text_color="white",
				font=ctk.CTkFont(size=12),
				command=lambda proc=t["processo"]: self._selecionar(proc),
			).place(relx=1.0, rely=0.5, anchor="e", x=-15)

	def _selecionar(self, processo):
		if self.on_selecionar:
			self.on_selecionar(processo)

	def _navegar_cadastro(self):
		if self.on_cadastrar:
			self.on_cadastrar()
		else:
			ModalCadastrarTCCM(self, onSalvar=self._recarregar)

	def _recarregar(self):
		for w in self.table_body.winfo_children():
			w.destroy()
		self._carregar_tccms()

	def _sair(self):
		if self.on_sair:
			self.on_sair()

__all__ = ["TccmDashboardPage"]
