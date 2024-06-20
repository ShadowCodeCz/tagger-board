import json
import os
import ctypes
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *

# import app_core
import qdarktheme
import datetime

from . import core
from . import gui
from . import notificator


class ApplicationCLI:
    @staticmethod
    def run(arguments):
        cfg = core.container.cfg
        cfg.from_json(arguments.configuration)
        app = Application(arguments.configuration)
        app.run()


class Controller:
    def __init__(self):
        self.selected_items = []
        self.filter_focused = {
            "included": False,
            "excluded": False
        }
        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.new_included_filter, self.new_included_filter)
        self.notifier.subscribe(notificator.Messages.new_excluded_filter, self.new_excluded_filter)
        self.notifier.subscribe(notificator.Messages.new_group_filter, self.new_group_filter)
        self.notifier.subscribe(notificator.Messages.selected, self.selected)
        self.notifier.subscribe(notificator.Messages.key_event, self.key_event)
        # self.notifier.subscribe(notificator.Messages.filter_focus_out, self.filter_focus_out)
        # self.notifier.subscribe(notificator.Messages.filter_focus_changed, self.filter_focus_changed)
        self.refresher = core.TaggedDirectoriesIndexRefresher()
        self.key_press_handler = core.KeyPressHandler()

    def refresh(self):
        self.refresher.refresh()
        notification = notificator.Notification(notificator.Messages.refreshed)
        self.notifier.notify(notification)

    def new_included_filter(self, notification):
        cfg = core.container.cfg
        cfg.filter.from_dict({"included": notification.obj})
        self.refresh()

    def new_excluded_filter(self, notification):
        cfg = core.container.cfg
        cfg.filter.from_dict({"excluded": notification.obj})
        # print(cfg.filter())
        self.refresh()

    def new_group_filter(self, notification):
        cfg = core.container.cfg
        cfg.filter.from_dict({"group": notification.obj})
        self.refresh()

    def selected(self, notification):
        for item in self.selected_items:
            try:
                item.deselected()
            except Exception as e:
                continue
        self.selected_items = [notification.publisher]

    def key_event(self, notification):
        if notification.key == "Ctrl+Key_F":
            notification = notificator.Notification(notificator.Messages.focus_filter)
            self.notifier.notify(notification)
        elif notification.key == "Ctrl+Key_R":
            self.refresh()
        else:
            params = core.KeyPressHandlerParams()
            params.key = notification.key
            params.mags = [i.item.mag for i in self.selected_items]
            status = self.key_press_handler.handle(params)
            if status is not None:
                new_status_notification = notificator.Notification(notificator.Messages.new_status)
                new_status_notification.status = status
                self.notifier.notify(new_status_notification)

                if status.refresh:
                    self.refresh()

    def filter_focus_changed(self, notification):
        self.filter_focused[notification.obj.filter_type] = notification.obj.focused

        if not any(self.filter_focused.values()):
            hide_notification = notificator.Notification(notificator.Messages.hide_filter_frame)
            self.notifier.notify(hide_notification)


class Application:
    def __init__(self, cfg_path, logger=core.container.logger()):
        self.app = None
        self.cfg_path = os.path.abspath(cfg_path)
        self.logger = logger
        self.window = None
        self.arguments = None
        self.controller = Controller()

    def run(self):
        refresher = core.TaggedDirectoriesIndexRefresher()
        refresher.refresh()

        self.app = QApplication([])
        qdarktheme.setup_theme(corner_shape="sharp")
        self.window = gui.MainWindow()
        self.window.setWindowTitle(f"Board: {self.cfg_path}")
        self.set_logo()
        # self.startup()
        # self.window.showMaximized()

        # self.window.show()
        self.window.showMaximized()
        self.app.exec()

    def set_logo(self):
        my_app_id = f'shadowcode.{core.container.app_description().name}.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        path = os.path.join(core.container.package_paths().image_directory(), 'logo.png')
        self.window.setWindowIcon(QIcon(path))
        self.app.setWindowIcon(QIcon(path))



