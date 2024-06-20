import logging
import os.path
import datetime

import yapsy.IPlugin
import subprocess


class Response:
    def __init__(self):
        self.success = True
        self.short_msg = ""
        self.handler = ""
        self.refresh = False


class RectangleHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        # TODO: Rectangle was not opened
        file_template = os.path.join(params.directory, "print.screens", "%Y.%m.%d_%H-%M-%S.png")
        cmd = f'ihl ps -r -o {file_template} -m -1'
        print(cmd)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        response = Response()
        response.handler = self.plugin_id()
        response.short_msg = datetime.datetime.now().strftime(file_template)
        return response

    def plugin_id(self):
        return "rectangle"
