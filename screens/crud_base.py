import _path  # noqa: F401

import customtkinter as ctk
from config.styles import COLORS, FONTS


class CrudBase:
    def build_header(self, title, subtitle):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text=subtitle,
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def build_filter_container(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="x", padx=30, pady=(0, 20))
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)
        return inner

    def build_search_entry(self, parent, placeholder, width=340):
        frame = ctk.CTkFrame(
            parent, fg_color=COLORS["white"], border_width=1,
            border_color=COLORS["border"], corner_radius=4
        )
        frame.pack(side="left", padx=(0, 10))

        entry = ctk.CTkEntry(
            frame, placeholder_text=placeholder,
            width=width, height=38, border_width=0,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        entry.pack(side="left", padx=(12, 4), pady=2)
        ctk.CTkLabel(
            frame, text="\U0001f50d",
            font=ctk.CTkFont(size=14), text_color="#999999"
        ).pack(side="right", padx=(0, 10))
        return entry

    def build_filter_entry(self, parent, placeholder, width=200):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            width=width, height=38, border_width=1,
            border_color=COLORS["border"], corner_radius=4,
            fg_color=COLORS["white"], text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
        )
        entry.pack(side="left", padx=(0, 10))
        return entry

    def build_btn_frame(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(side="left", padx=(5, 0))
        return btn_frame

    def build_action_btn(self, parent, text, icon, command,
                         fg_color=COLORS["white"], hover_color="#F0F0F0",
                         text_color=COLORS["text"], border=True, bold=False):
        btn = ctk.CTkButton(
            parent,
            image=icon,
            text=text,
            height=38, corner_radius=4,
            fg_color=fg_color, hover_color=hover_color,
            text_color=text_color,
            border_width=1 if border else 0,
            border_color=COLORS["border"],
            font=ctk.CTkFont(
                size=FONTS["size_body"],
                weight="bold" if bold else "normal"
            ),
            compound="left",
            command=command,
        )
        btn.pack(side="left", padx=(0, 8))
        return btn

    def build_table(self, pad_y=(0, 30)):
        self.table_frame = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=4,
            border_width=1, border_color=COLORS["border"]
        )
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=pad_y)
        return self.table_frame

    def build_table_header(self, parent, columns, weights, has_checkbox=True, alignments=None):
        header = ctk.CTkFrame(parent, fg_color=COLORS["table_header"], height=44, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        if has_checkbox:
            ctk.CTkLabel(header, text="", width=20).pack(side="left", padx=(17, 0))

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(10, 0))

        for i, w in enumerate(weights):
            cols.grid_columnconfigure(i, weight=w)

        if alignments is None:
            alignments = ["w"] * len(columns)

        for i, col_text in enumerate(columns):
            padx = (10, 5) if i == 0 else (5, 5) if i < len(columns) - 1 else (5, 10)
            ctk.CTkLabel(
                cols, text=col_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                anchor=alignments[i]
            ).grid(row=0, column=i, sticky="ew", padx=padx)

        ctk.CTkLabel(
            header, text="Açoes",
            font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            text_color=COLORS["text_muted"],
            width=120
        ).pack(side="right", padx=(0, 15))

        self.table_body = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)
        return self.table_body

    def add_data_row(self, has_checkbox=True):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=52)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(self.table_body, fg_color="#E0E0E0", height=1).pack(fill="x")

        cb = None
        if has_checkbox:
            cb = ctk.CTkCheckBox(linha, text="", width=20, height=20,
                                  border_width=2, corner_radius=4)
            cb.pack(side="left", padx=(17, 0))

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(10, 0))

        return linha, data, cb

    def add_action_buttons(self, parent, actions, width=120):
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=width)
        frame.pack(side="right", padx=(0, 15))
        frame.pack_propagate(False)

        for icon, cmd in actions:
            ctk.CTkButton(
                frame,
                text=icon, width=32, height=32,
                corner_radius=4, fg_color=COLORS["white"],
                hover_color="#F0F0F0", text_color=COLORS["text"],
                border_width=1, border_color=COLORS["border"],
                font=ctk.CTkFont(size=14),
                command=cmd,
            ).pack(side="left", padx=2)

    def clear_entries(self, *entries):
        for entry in entries:
            entry.delete(0, "end")

    def refresh_from_db(self, carregar_fn):
        self.data = carregar_fn()
        self.render_rows()

    def configure_data_columns(self, data_frame, weights):
        for i, w in enumerate(weights):
            data_frame.grid_columnconfigure(i, weight=w)
