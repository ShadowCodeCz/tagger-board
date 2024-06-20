import logging
import yapsy.IPlugin
import os
import subprocess
import datetime


class Response:
    def __init__(self):
        self.success = True
        self.short_msg = ""
        self.handler = ""
        self.refresh = False


class PrintScreenHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        file_template = os.path.join(params.directory, "print.screens", "%Y.%m.%d_%H-%M-%S.png")
        cmd = f'ihl ps -o {file_template} -m -1'
        print(cmd)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        response = Response()
        response.handler = self.plugin_id()
        response.short_msg = datetime.datetime.now().strftime(file_template)
        return response

    def plugin_id(self):
        return "print.screen"
