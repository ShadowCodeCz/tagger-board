import datetime

from PyQt6.QtGui import QDoubleValidator, QFont
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from . import core
from . import notificator
from . import tag

from . import builder

def clear_layout(layout):
    if layout:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        cfg = core.container.cfg

        self.notifier = core.container.notifier()
        self.main_layout = QVBoxLayout(self)

        filter_frame = FilterFrame(self)
        self.main_layout.addWidget(filter_frame)

        scroll_area = QScrollArea(self)
        scroll_area.setObjectName("TaggerScrollArea")
        scroll_area.setStyleSheet("#TaggerScrollArea {border: 0px solid black}")
        scroll_area.setWidgetResizable(True)
        view = ViewFrame(self)
        scroll_area.setWidget(view)

        self.main_layout.addWidget(scroll_area)
        status_frame = StatusFrame(self)
        self.main_layout.addWidget(status_frame)
        self.setLayout(self.main_layout)
        self.resize(cfg.window.open_width(), cfg.window.open_height())
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        render_cfg = core.container.cfg.render.main_window
        # self.setObjectName("MainWindow")
        # self.setStyleSheet(f"#MainWindow {{background-color:{render_cfg.background_color()}}}")
        self.setStyleSheet(f"background-color:{render_cfg.background_color()}")

    def keyPressEvent(self, event):
        modifier = ''
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifier += 'Ctrl+'
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifier += 'Shift+'
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifier += 'Alt+'

        # key = event.text().upper()
        # if not key:
        key = Qt.Key(event.key()).name

        notification = notificator.Notification(notificator.Messages.key_event)
        notification.key = f"{modifier}{key}"
        self.notifier.notify(notification)

        super().keyPressEvent(event)


class StatusFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        notifier = core.container.notifier()
        notifier.subscribe(notificator.Messages.new_status, self.refresh_handler)

        self.status_render_cfg = core.container.cfg.render.status

        self.custom_layout = QVBoxLayout(self)
        self.setLayout(self.custom_layout)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.label.setStyleSheet("""
        #     QLabel {
        #         color: gray;
        #         font-size: 14px;
        #         font-weight: bold;
        #     }
        # """)
        self.custom_layout.addWidget(self.label)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

        self.setObjectName("StatusFrame")
        self.setStyleSheet("#StatusFrame {border: 0px solid black;}")

    def refresh_handler(self, notification):
        self.label.setText(f"[{notification.status.handler}] {datetime.datetime.now()}: {notification.status.short_msg}")
        self.set_style(self.status_render_cfg)

        if notification.status.success == True:
            self.set_style(self.status_render_cfg.success())
        else:
            self.set_style(self.status_render_cfg.error())

    def set_style(self, render_cfg):
        self.setStyleSheet(f"""
            #{self.objectName()} QLabel
            {{
                        font-family: '{render_cfg.get("font_family")}'; 
                        font-size: {render_cfg.get("font_size")}; 
                        font-weight: {render_cfg.get("font_weight")}; 
                        color: {render_cfg.get("text_color")};
            }} 
            
            #{self.objectName()}
            {{
                        border-top: 0px {render_cfg.get("border_style")} {render_cfg.get("border_color")}; 
                        border-left: 0px {render_cfg.get("border_style")} {render_cfg.get("background_color")}; 
                        border-right: 0px {render_cfg.get("border_style")} {render_cfg.get("background_color")}; 
                        border-bottom: 0px {render_cfg.get("border_style")} {render_cfg.get("border_color")}; 
                        background-color: {render_cfg.get("background_color")}
            }}          
            """)

    # def set_red_status(self):
    #     self.label.setStyleSheet("""
    #         QLabel {
    #             color: gray;
    #             font-size: 15px;
    #             font-weight: normal;
    #         }
    #     """)
    #     self.setStyleSheet("#StatusFrame {border: 0px solid red;}")
    #
    # def set_green_status(self):
    #     self.label.setStyleSheet("""
    #         QLabel {
    #             color: gray;
    #             font-size: 15px;
    #             font-weight: normal;
    #         }
    #     """)
    #     self.setStyleSheet("#StatusFrame {border: 0px solid green;}")

class FilterFocus:
    def __init__(self, filter_type, focused):
        self.filter_type = filter_type
        self.focused = focused


class FilterLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_type = None
        self.notifier = core.container.notifier()

    def focusOutEvent(self, event):
        notification = notificator.Notification(notificator.Messages.sub_filter_focus_changed)
        notification.obj = FilterFocus(self.filter_type, False)
        self.notifier.notify(notification)
        super().focusOutEvent(event)

    def focusInEvent(self, event):
        notification = notificator.Notification(notificator.Messages.sub_filter_focus_changed)
        notification.obj = FilterFocus(self.filter_type, True)
        self.notifier.notify(notification)
        super().focusInEvent(event)


class FilterFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cfg = core.container.cfg
        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.focus_filter, self.focus_filter)
        # self.notifier.subscribe(notificator.Messages.hide_filter_frame, self.hide_filter_frame)
        self.notifier.subscribe(notificator.Messages.sub_filter_focus_changed, self.sub_filter_focus_changed)

        self.custom_layout = QHBoxLayout(self)

        self.included_edit = FilterLineEdit(str(cfg.filter.included()))
        self.included_edit.filter_type = "included"
        self.included_edit.setObjectName("IncludedFilterLineEdit")

        self.excluded_edit = FilterLineEdit(str(cfg.filter.excluded()))
        self.excluded_edit.filter_type = "excluded"
        self.excluded_edit.setObjectName("ExcludedFilterLineEdit")

        self.group_edit = FilterLineEdit(str(cfg.filter.group()))
        self.group_edit.filter_type = "group"
        self.group_edit.setObjectName("GroupFilterLineEdit")

        filter_render_cfg = core.container.cfg.render.filter
        self.set_edit_style(self.included_edit, filter_render_cfg.included())
        self.set_edit_style(self.excluded_edit, filter_render_cfg.excluded())
        self.set_edit_style(self.group_edit, filter_render_cfg.group())

        self.included_edit.textChanged.connect(self.included_filter_changed)
        self.excluded_edit.textChanged.connect(self.excluded_filter_changed)
        self.group_edit.textChanged.connect(self.group_filter_changed)

        self.custom_layout.addWidget(self.included_edit)
        self.custom_layout.addWidget(self.excluded_edit)
        self.custom_layout.addWidget(self.group_edit)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(0)
        self.custom_layout.setContentsMargins(0, 0, 0, 1)

        self.hide()

    def set_edit_style(self, edit, render_cfg):
        edit.setStyleSheet(f"""#{edit.objectName()}
        {{
                font-family: '{render_cfg.get("font_family")}'; 
                font-size: {render_cfg.get("font_size")}; 
                font-weight: {render_cfg.get("font_weight")}; 
                color: {render_cfg.get("text_color")};
                border-top: {render_cfg.get("border_width")} {render_cfg.get("border_style")} {render_cfg.get("border_color")}; 
                border-left: {render_cfg.get("border_width")} {render_cfg.get("border_style")} {render_cfg.get("background_color")}; 
                border-right: {render_cfg.get("border_width")} {render_cfg.get("border_style")} {render_cfg.get("background_color")}; 
                border-bottom: {render_cfg.get("border_width")} {render_cfg.get("border_style")} {render_cfg.get("border_color")}; 
                background-color: {render_cfg.get("background_color")}
        }}        
        """)

    def included_filter_changed(self, text):
        f = self.evaluate_filter(text)
        if f is not None:
            notification = notificator.Notification(notificator.Messages.new_included_filter)
            notification.obj = f
            self.notifier.notify(notification)

    def excluded_filter_changed(self, text):
        f = self.evaluate_filter(text)
        if f is not None:
            notification = notificator.Notification(notificator.Messages.new_excluded_filter)
            notification.obj = f
            self.notifier.notify(notification)

    def group_filter_changed(self, text):
        f = text
        notification = notificator.Notification(notificator.Messages.new_group_filter)
        notification.obj = f
        self.notifier.notify(notification)

    def evaluate_filter(self, text):
        try:
            result = eval(text)
            if isinstance(result, list) and all(isinstance(sublist, list) and all(isinstance(item, str) for item in sublist) for sublist in result):
                return result
            else:
                return None
        except Exception as e:
            return None

    def focus_filter(self, notification):
        self.included_edit.setFocus()
        self.show()

    def hide_filter_frame(self, notification):
        self.hide()

    def sub_filter_focus_changed(self, notification):
        if not (self.included_edit.hasFocus() or self.excluded_edit.hasFocus() or self.group_edit.hasFocus()):
            self.hide()


class ViewFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        notifier = core.container.notifier()
        notifier.subscribe(notificator.Messages.refreshed, self.refresh_handler)

        self.custom_layout = QVBoxLayout(self)
        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

        self.setObjectName("ViewFrame")
        self.setStyleSheet("#ViewFrame {border: 0px solid black}")

        self.update_view()

    def refresh_handler(self, notification):
        self.update_view()

    # def update_view(self):
    #     clear_layout(self.custom_layout)
    #     index = core.container.tagger_directories_index()
    #
    #     for _, item in index.items():
    #         tagged_directory_item = TaggedDirectoryItem(self)
    #         tagged_directory_item.set_item(item)
    #         self.custom_layout.addWidget(tagged_directory_item)
    #
    #     self.custom_layout.addStretch()
    #     self.setLayout(self.custom_layout)

    def update_view(self):
        clear_layout(self.custom_layout)
        group_index = core.container.group_index()

        for group_name, group in group_index.items():
            # self.custom_layout.addWidget(QLabel(group_name))
            group_item = GroupItem()
            group_item.set_text(group_name)
            self.custom_layout.addWidget(group_item)
            for item in group:
                tagged_directory_item = TaggedDirectoryItem(self)
                tagged_directory_item.set_tagged_directory(item)
                self.custom_layout.addWidget(tagged_directory_item)

        self.custom_layout.addStretch()
        self.setLayout(self.custom_layout)


class GroupItem(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group_render_cfg = core.container.cfg.render.group

        self.custom_layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setStyleSheet(f"""
            QLabel {{
                font-family: '{self.group_render_cfg.font_family()}'; 
                font-size: {self.group_render_cfg.font_size()}; 
                font-weight: {self.group_render_cfg.font_weight()}; 
                color: {self.group_render_cfg.text_color()};
            }}
        """)
        # font = QFont('Consolas')
        # font.setStyleHint(QFont.StyleHint.Monospace)
        # font.setPixelSize(11)
        # label.setFont(font)

        self.custom_layout.addWidget(self.label)
        self.custom_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.custom_layout)

        self.setObjectName("GroupItem")

        self.setStyleSheet(f"#GroupItem {{border: {self.group_render_cfg.border_width()}px {self.group_render_cfg.border_style()} {self.group_render_cfg.border_color()}; background-color: {self.group_render_cfg.background_color()}}}")
        # self.setStyleSheet(f"#GroupItem {{border: 1px solid red}}")

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 10, 1, 1)

    def set_text(self, text):
        self.label.setText(text)


class TaggedDirectoryItem(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.item = None
        self.selected_flag = False

        self.tag_parser = tag.TagParser()
        self.render_cfg = core.container.cfg.render
        self.notifier = core.container.notifier()

        self.custom_layout = QHBoxLayout(self)
        self.custom_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # self.left_frame = QFrame(self)
        # self.left_frame.setLayout(QHBoxLayout(self.left_frame))
        #
        # self.right_frame = QFrame(self)
        # self.right_frame.setLayout(QHBoxLayout(self.right_frame))

        self.left_layout = QHBoxLayout()
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.left_layout.setSpacing(4)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.right_layout = QHBoxLayout()
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.right_layout.setSpacing(1)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # self.custom_layout.addWidget(self.left_frame)
        self.custom_layout.addLayout(self.left_layout)
        self.custom_layout.addStretch(1)
        # self.custom_layout.addWidget(self.right_frame)
        self.custom_layout.addLayout(self.right_layout)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(10)
        self.custom_layout.setContentsMargins(4, 4, 4, 4)

        self.setObjectName("TaggedDirectoryItem")
        self.deselected()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # def set_tagged_directory(self, tagged_directory):
    #     # self.clear_layout(self.left_frame.layout())
    #     # self.clear_layout(self.right_frame.layout())
    #     self.clear_layout(self.left_layout)
    #     self.clear_layout(self.right_layout)
    #
    #     self.item = tagged_directory
    #
    #     for tag_text in tagged_directory.tags:
    #         parsed_tag = self.tag_parser.parse(tag_text)
    #         tag_render_cfg = self.render_cfg.tag().get(parsed_tag.name)
    #
    #         if self.render_cfg.render_all_tags() == "yes":
    #             self.add_tag_to_layout(parsed_tag, tag_text, tag_render_cfg)
    #         else:
    #             self.add_tag_to_layout(parsed_tag, tag_text, tag_render_cfg)
    def set_tagged_directory(self, tagged_directory):
        self.clear_layout(self.left_layout)
        self.clear_layout(self.right_layout)

        self.item = tagged_directory

        tags_builder = builder.TagsBuilder()
        res = tags_builder.build(tagged_directory)

        for left_widget in res[0]:
            self.left_layout.addWidget(left_widget)

        for right_widget in res[1]:
            self.right_layout.addWidget(right_widget)


    # def add_tag_to_layout(self, parsed_tag, tag_render_cfg):
    def add_tag_to_layout(self, parsed_tag, tag_text, tag_render_cfg):
        if tag_render_cfg:
            # tag_item = TagItem(self)
            # tag_item.set_tag(parsed_tag)

            tag_widget_builder_params = builder.TagWidgetBuilderParams()
            tag_widget_builder_params.tag = tag_text
            tag_widget_builder_params.parsed_tag = parsed_tag
            tag_widget_builder_params.tag_item = self.item

            tag_widget_builder = builder.TagWidgetBuilder()
            widget = tag_widget_builder.build(tag_widget_builder_params)
            widget.setParent(self)

            alignment = tag_render_cfg.get("alignment")
            if alignment is None or alignment != "right":
                # self.left_layout.addWidget(tag_item)
                self.left_layout.addWidget(widget)
            else:
                # self.right_layout.addWidget(tag_item)
                self.right_layout.addWidget(widget)

    def mousePressEvent(self, event):
        notification = notificator.Notification(notificator.Messages.selected, self)
        self.notifier.notify(notification)
        self.selected()

    def selected(self):
        self.selected_flag = True
        # print(f"Selected: {self.item.mag}")
        render_cfg = core.container.cfg.render.selected
        self.setStyleSheet(f"""#TaggedDirectoryItem {{
            border: {render_cfg.border_width()} {render_cfg.border_style()} {render_cfg.border_color()};
            background-color: {render_cfg.background_color()}
        }}""")

    def deselected(self):
        self.selected_flag = False
        # print(f"Deselected: {self.item.mag}")
        render_cfg = core.container.cfg.render.deselected
        self.setStyleSheet(f"""#TaggedDirectoryItem {{
            border: {render_cfg.border_width()} {render_cfg.border_style()} {render_cfg.border_color()};
            background-color: {render_cfg.background_color()}
        }}""")


