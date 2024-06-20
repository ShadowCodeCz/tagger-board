import re

from PyQt6.QtGui import QDoubleValidator, QFont
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from . import core
from . import notificator
from . import tag


class TagWidgetBuilderParams:
    def __init__(self):
        self.tag = None
        self.parsed_tag = None
        self.tag_item = None


class TagWidgetBuilder:
    def __init__(self):
        pass

    def build(self, params):
        widget = TagItem()
        widget.set_tag(params.parsed_tag)
        return widget

# TODO: Pouze vykreslovaci
# TODO: Podmineny obsah [preklad MAC adresy na prostredi]
# TODO: Podminen stylovani (castecne se da nahradit klici v konfiguraci coby regularni vyrazy) [test.result@pass, test.result@fail, test.result@exluded] [run.type@preparation - ovlivni stylovani i ostatnich tagu]
# TODO: Akce navazana na kliknuti [jira.ticket@T-1]


class TagItem(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tags_render_cfg = core.container.cfg.render.tag()
        self.tag_parser = tag.TagParser()
        self.custom_layout = QHBoxLayout(self)
        self.label = QLabel()
        self.custom_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.custom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(3)
        self.custom_layout.setContentsMargins(2, 2, 2, 2)

    def set_tag(self, parsed_tag):
        self.label.setText(parsed_tag.value if parsed_tag.value is not None else parsed_tag.name)
        tag_render_cfg = self.tags_render_cfg.get(parsed_tag.name)

        if tag_render_cfg is None:
            tag_render_cfg = self.tags_render_cfg.get("__default__")

        self.label.setStyleSheet(f"""
            QLabel {{
                font-family: '{tag_render_cfg.get("font_family")}'; 
                font-size: {tag_render_cfg.get("font_size")}; 
                font-weight: {tag_render_cfg.get("font_weight")}; 
                color: {tag_render_cfg.get("text_color")};
                background-color: {tag_render_cfg.get("background_color")};
            }}
        """)

        self.setObjectName("TagItem")
        self.setStyleSheet(
            f"""#TagItem {{
                border: {tag_render_cfg.get("border_width")} {tag_render_cfg.get("border_style")} {tag_render_cfg.get("border_color")}; 
                background-color: {tag_render_cfg.get("background_color")}
                }}
            QToolTip {{
                background-color: {tag_render_cfg.get("background_color")};
                color: {tag_render_cfg.get("text_color")};
                border:  {tag_render_cfg.get("border_width")} {tag_render_cfg.get("border_style")} {tag_render_cfg.get("border_color")};
                font: {tag_render_cfg.get("font_weight")} {tag_render_cfg.get("font_size")} '{tag_render_cfg.get("font_family")}';
            }}"""
        )

        fixed_width = tag_render_cfg.get("fixed_width")
        if fixed_width != "" and fixed_width is not None and fixed_width != 0:
            self.setFixedWidth(int(fixed_width))

        self.setToolTipDuration(5000)
        self.setToolTip(f"""{parsed_tag.name}@<b>{parsed_tag.value}</b""")


# ----------------------------------------------------------------------------------------------------------------------
class TagItemWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.side = "left"
        self.custom_layout = QHBoxLayout(self)
        self.label = QLabel()
        self.custom_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.custom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(3)
        self.custom_layout.setContentsMargins(2, 2, 2, 2)


class DefaultTagBuilder:
    def __init__(self):
        self.tags_render_cfg = core.container.cfg.render.tag()
        self.tag_parser = tag.TagParser()

    def build(self, tag, tagged_directory):
        parsed_tag = self.tag_parser.parse(tag)
        tag_cfg = self.get_cfg(parsed_tag)
        if tag_cfg is None:
            return None
        else:
            widget = TagItemWidget()
            self.set_tag_widget(widget, parsed_tag)
            return widget

    def get_cfg(self, parsed_tag):
        cfgs_for_tags = self.tags_render_cfg.get(parsed_tag.name)

        if cfgs_for_tags is None:
            return None

        for cfg in cfgs_for_tags:
            if re.match(cfg.get("value_expression"), parsed_tag.value):
                return cfg

        return None

    def set_tag_widget(self, widget, parsed_tag):
        widget.label.setText(parsed_tag.value if parsed_tag.value is not None else parsed_tag.name)
        tag_render_cfg = self.get_cfg(parsed_tag)

        alignment = tag_render_cfg.get("alignment")
        widget.side = "left" if alignment is None or alignment.lower().strip() == "left" else "right"

        if tag_render_cfg is None:
            tag_render_cfg = self.tags_render_cfg.get("__default__")

        widget.label.setStyleSheet(f"""
            QLabel {{
                font-family: '{tag_render_cfg.get("font_family")}'; 
                font-size: {tag_render_cfg.get("font_size")}; 
                font-weight: {tag_render_cfg.get("font_weight")}; 
                color: {tag_render_cfg.get("text_color")};
                background-color: {tag_render_cfg.get("background_color")};
            }}
        """)

        widget.setObjectName("TagItem")
        widget.setStyleSheet(
            f"""#TagItem {{
                border: {tag_render_cfg.get("border_width")} {tag_render_cfg.get("border_style")} {tag_render_cfg.get("border_color")}; 
                background-color: {tag_render_cfg.get("background_color")}
                }}
            QToolTip {{
                background-color: {tag_render_cfg.get("background_color")};
                color: {tag_render_cfg.get("text_color")};
                border:  {tag_render_cfg.get("border_width")} {tag_render_cfg.get("border_style")} {tag_render_cfg.get("border_color")};
                font: {tag_render_cfg.get("font_weight")} {tag_render_cfg.get("font_size")} '{tag_render_cfg.get("font_family")}';
            }}"""
        )

        fixed_width = tag_render_cfg.get("fixed_width")
        if fixed_width != "" and fixed_width is not None and fixed_width != 0:
            widget.setFixedWidth(int(fixed_width))

        widget.setToolTipDuration(5000)
        widget.setToolTip(f"""{parsed_tag.name}@<b>{parsed_tag.value}</b""")


class DefaultTagBuilderSelector:
    def __init__(self):
        self.tag_parser = tag.TagParser()

    def select(self, tag):
        return DefaultTagBuilder()



class DefaultTagsBuilder:
    def __init__(self):
        self.selector = DefaultTagBuilderSelector()

    def build(self, tagged_directory):
        left_widgets = []
        right_widgets = []
        for tag in tagged_directory.tags:
            builder = self.selector.select(tag)
            widget = builder.build(tag, tagged_directory)

            if widget is not None and widget.side == "left":
                left_widgets.append(widget)

            if widget is not None and widget.side == "right":
                right_widgets.append(widget)

        return [left_widgets, right_widgets]


class SpecificTagsBuilderSelector:
    def __init__(self):
        pass

    def select(self, tagged_directory):
        return DefaultTagsBuilder()


class TagsBuilder:
    def __init__(self):
        self.selector = SpecificTagsBuilderSelector()

    def build(self, tagged_directory):
        specific_builder = self.selector.select(tagged_directory)
        return specific_builder.build(tagged_directory)