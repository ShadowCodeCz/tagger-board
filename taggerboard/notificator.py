import re


class Messages:
    refreshed = "refreshed"
    new_included_filter = "new_included_filter"
    new_excluded_filter = "new_excluded_filter"
    new_group_filter = "new_group_filter"
    selected = "selected"
    deselected = "deselected"
    key_event = "key_event"
    focus_filter = "focus_filter"
    filter_focus_out = "filter_focus_out"
    hide_filter_frame = "hide_filter_frame"
    sub_filter_focus_changed = "sub_filter_focus_changed"
    new_status = "new.status"


class Notification(object):
    def __init__(self, message, publisher=None):
        self.message = message
        self.publisher = publisher
        self.obj = None


class SingletonNotificationProvider:
    subscription = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonNotificationProvider, cls).__new__(cls)
        return cls.instance

    def subscribe(self, message, subscriber):
        self.subscription.setdefault(message, []).append(subscriber)

    def unsubscribe(self, message, subscriber):
        self.subscription[message].remove(subscriber)

    def notify(self, notification):
        for subscriber in self.subscription.setdefault(notification.message, []):
            subscriber(notification)