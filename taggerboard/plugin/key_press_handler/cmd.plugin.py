import logging
import os.path

import yapsy.IPlugin
import subprocess


class Response:
    def __init__(self):
        self.success = True
        self.short_msg = ""
        self.handler = ""
        self.refresh = False


class CmdHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        cmd = f'start cmd /K cd /d {params.directory}'
        subprocess.Popen(cmd, shell=True)

    def plugin_id(self):
        return "cmd"
