import customtkinter as ctk

from config.styles import COLORS, FONTS, LAYOUT


class LayoutSystem:
    """Padrões globais para containers, formulários e tabelas do sistema."""

    BASE_WIDTH = LAYOUT["base_width"]
    BASE_HEIGHT = LAYOUT["base_height"]

    @staticmethod
    def scale(value, *, width=None, height=None, min_ratio=0.82, max_ratio=1.15):
        """Escala valores para manter proporções em 1920x1080 e 1366x768."""
        if isinstance(value, (tuple, list)):
            return type(value)(
                LayoutSystem.scale(
                    item,
                    width=width,
                    height=height,
                    min_ratio=min_ratio,
                    max_ratio=max_ratio,
                )
                for item in value
            )

        if width is None and height is None:
            return value
        target = width if width is not None else height
        if target is None or target <= 0:
            return value

        ratio = target / LayoutSystem.BASE_WIDTH if width is not None else target / LayoutSystem.BASE_HEIGHT
        ratio = max(min_ratio, min(max_ratio, ratio))
        return max(1, int(round(value * ratio)))

    @staticmethod
    def responsive(value, *, parent=None, width=None, height=None):
        """Retorna um valor dimensionado de acordo com a janela ativa do widget.

        Quando o contêiner ainda não foi exibido, mantém o valor original para evitar
        problemas de dimensionamento antes do primeiro draw.
        """
        if value is None:
            return None

        if isinstance(value, (tuple, list)):
            return type(value)(
                LayoutSystem.responsive(
                    item,
                    parent=parent,
                    width=width,
                    height=height,
                )
                for item in value
            )

        if parent is not None:
            try:
                w = parent.winfo_width()
                h = parent.winfo_height()
            except Exception:
                w = width
                h = height
            if w and w > 1:
                width = w
            if h and h > 1:
                height = h

        if width is None and height is None:
            return value

        return LayoutSystem.scale(value, width=width, height=height)

    @staticmethod
    def normalize_padding(padding, *, parent=None):
        if padding is None:
            return (0, 0)
        if not isinstance(padding, (tuple, list)):
            return (padding, padding)
        if len(padding) != 2:
            return (padding[0], padding[0])

        pad_x, pad_y = padding
        return (
            LayoutSystem.responsive(
                pad_x,
                parent=parent,
                width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
            ),
            LayoutSystem.responsive(
                pad_y,
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            ),
        )

    @staticmethod
    def page_container(parent, *, padding_x=None, padding_y=None, bg_color=None):
        padding_x = LAYOUT["page_padding_x"] if padding_x is None else padding_x
        padding_y = LAYOUT["page_padding_y"] if padding_y is None else padding_y
        padding_x = LayoutSystem.responsive(
            padding_x,
            parent=parent,
            width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
        )
        padding_y = LayoutSystem.responsive(
            padding_y,
            parent=parent,
            height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
        )
        return ctk.CTkFrame(
            parent,
            fg_color=bg_color or COLORS["bg"],
            corner_radius=LAYOUT["panel_radius"],
        ), padding_x, padding_y

    @staticmethod
    def panel(parent, *, height=None, width=None, fill="both", expand=False, padding=(0, 0), fg_color=None,
              border_color=None, border_width=None, radius=None):
        # Avoid passing None for width/height to CTkFrame because some customtkinter
        # versions multiply these values by a float factor during scaling, which
        # raises TypeError when they are None. Only include width/height if provided.
        frame_kwargs = {
            "fg_color": fg_color or COLORS["white"],
            "corner_radius": radius if radius is not None else LAYOUT["panel_radius"],
            "border_width": border_width if border_width is not None else LAYOUT["panel_border"],
            "border_color": border_color or COLORS["border"],
        }
        if width is not None:
            frame_kwargs["width"] = LayoutSystem.responsive(
                value=width,
                parent=parent,
                width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
            )
        if height is not None:
            frame_kwargs["height"] = LayoutSystem.responsive(
                value=height,
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            )

        panel = ctk.CTkFrame(parent, **frame_kwargs)
        pad_x, pad_y = LayoutSystem.normalize_padding(padding, parent=parent)
        panel.pack(fill=fill, expand=expand, padx=pad_x, pady=pad_y)
        return panel

    @staticmethod
    def section_header(parent, title, subtitle="", *, align="w", badge=None, text_color=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, LAYOUT["section_spacing"]))

        if badge is not None:
            badge_btn = ctk.CTkButton(
                frame,
                text=badge,
                height=32,
                corner_radius=16,
                fg_color=COLORS["primary_light"],
                hover_color=COLORS["primary_light_hover"],
                text_color=COLORS["primary"],
                border_width=0,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
            )
            badge_btn.pack(anchor=align, pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=text_color or COLORS["text"],
            anchor=align,
        ).pack(anchor=align)

        if subtitle:
            ctk.CTkLabel(
                frame,
                text=subtitle,
                font=ctk.CTkFont(size=FONTS["size_subtitle"]),
                text_color=COLORS["text_muted"],
                anchor=align,
            ).pack(anchor=align, pady=(4, 0))
        return frame

    @staticmethod
    def form_row(parent, *, padding_x=0, padding_y=(0, 10), columns=1):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=padding_x, pady=padding_y)
        for index in range(columns):
            row.grid_columnconfigure(index, weight=1)
        return row

    @staticmethod
    def field(parent, label_text, *, column=0, weight=1, width=None, required=False, show=None, height=None,
              placeholder=None, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=(0, 15), sticky="ew")
        frame.grid_columnconfigure(0, weight=weight)
        if width is not None:
            frame.configure(
                width=LayoutSystem.responsive(
                    value=width,
                    parent=parent,
                    width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
                )
            )

        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}{' *' if required else ''}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        )
        label.pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame,
            height=LayoutSystem.responsive(
                value=height or LAYOUT["field_height"],
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            ),
            corner_radius=LAYOUT["field_radius"],
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["white"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
            placeholder_text=placeholder,
            show=show,
            **kwargs,
        )
        entry.pack(fill="x")
        return entry

    @staticmethod
    def combobox_field(parent, label_text, values, *, column=0, weight=1, width=None,
                       default=None, entry_kwargs=None, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=(0, 15), sticky="ew")
        frame.grid_columnconfigure(0, weight=weight)
        if width is not None:
            frame.configure(
                width=LayoutSystem.responsive(
                    value=width,
                    parent=parent,
                    width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
                )
            )

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 4))

        combo_kwargs = {
            "height": LayoutSystem.responsive(
                value=LAYOUT["field_height"],
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            ),
            "corner_radius": LAYOUT["field_radius"],
            "border_width": 1,
            "border_color": COLORS["border"],
            "fg_color": COLORS["white"],
            "button_color": COLORS["border"],
            "button_hover_color": COLORS["hover"],
            "dropdown_fg_color": COLORS["white"],
            "text_color": COLORS["text"],
        }
        combo_kwargs.update(kwargs)
        combo = ctk.CTkComboBox(frame, values=values, **combo_kwargs)
        combo.pack(fill="x")
        if default is not None:
            try:
                combo.set(default)
            except Exception:
                pass
        return combo

    @staticmethod
    def button(parent, text, *, command=None, width=None, height=None, fg_color=None, hover_color=None,
               text_color=None, border_width=0, border_color=None, corner_radius=None, font_size=None,
               font_weight=None, compound=None, image=None):
        button_kwargs = {
            "text": text,
            "command": command,
            "fg_color": fg_color or COLORS["primary"],
            "hover_color": hover_color or COLORS["primary_hover"],
            "text_color": text_color or COLORS["white"],
            "border_width": border_width,
            "border_color": border_color or COLORS["border"],
            "corner_radius": corner_radius if corner_radius is not None else LAYOUT["field_radius"],
            "font": ctk.CTkFont(size=font_size or FONTS["size_body"], weight=font_weight or "normal"),
            "compound": compound,
            "image": image,
        }
        if width is not None:
            button_kwargs["width"] = LayoutSystem.responsive(
                value=width,
                parent=parent,
                width=parent.winfo_width() if hasattr(parent, "winfo_width") else None,
            )
        if height is not None:
            button_kwargs["height"] = LayoutSystem.responsive(
                value=height,
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            )
        else:
            button_kwargs["height"] = LayoutSystem.responsive(
                value=LAYOUT["field_height"],
                parent=parent,
                height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
            )

        return ctk.CTkButton(parent, **button_kwargs)

    @staticmethod
    def label(parent, text, *, font_size=None, weight="normal", text_color=None, anchor="w", justify=None,
              fg_color=None, bg_color=None):
        label_kwargs = {
            "text": text,
            "font": ctk.CTkFont(size=font_size or FONTS["size_body"], weight=weight),
            "text_color": text_color or COLORS["text"],
            "anchor": anchor,
            "justify": justify,
        }
        if fg_color is not None:
            label_kwargs["fg_color"] = fg_color
        if bg_color is not None:
            label_kwargs["bg_color"] = bg_color
        label = ctk.CTkLabel(parent, **label_kwargs)
        return label

    @staticmethod
    def table_shell(parent, *, header_title=None, columns=None, weights=None, height=None, padding=(0, 0),
                    with_actions=True, border_color=None):
        table = ctk.CTkFrame(
            parent,
            fg_color=COLORS["white"],
            corner_radius=LAYOUT["panel_radius"],
            border_width=1,
            border_color=border_color or COLORS["border"],
            height=(
                LayoutSystem.responsive(
                    value=height,
                    parent=parent,
                    height=parent.winfo_height() if hasattr(parent, "winfo_height") else None,
                )
                if height is not None
                else None
            ),
        )
        table.pack(fill="both", expand=True, padx=padding[0], pady=padding[1])
        table.pack_propagate(False)

        header = ctk.CTkFrame(table, fg_color=COLORS["table_header"], height=LAYOUT["table_header_height"],
                              corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        if columns and weights:
            cols = ctk.CTkFrame(header, fg_color="transparent")
            cols.pack(side="left", fill="x", expand=True, padx=(10, 0))
            for i, w in enumerate(weights):
                cols.grid_columnconfigure(i, weight=w)
            for i, col_text in enumerate(columns):
                ctk.CTkLabel(
                    cols,
                    text=col_text,
                    font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                    text_color=COLORS["text_muted"],
                ).grid(row=0, column=i, sticky="ew", padx=(10, 5))

        if with_actions:
            ctk.CTkLabel(
                header,
                text="Ações",
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"],
                width=120,
            ).pack(side="right", padx=(0, 15))

        body = ctk.CTkScrollableFrame(table, fg_color=COLORS["white"], corner_radius=0)
        body.pack(fill="both", expand=True)
        return table, body


DEFAULT_LAYOUT = LayoutSystem
