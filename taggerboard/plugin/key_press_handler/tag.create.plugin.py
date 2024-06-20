import os
import datetime
import logging
import yapsy.IPlugin
import subprocess


class Response:
    def __init__(self):
        self.success = True
        self.short_msg = ""
        self.handler = ""
        self.refresh = True


class CreateHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        cmd = f'tagger-creator app'
        print(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.wait()
        response = Response()
        response.handler = self.plugin_id()
        response.short_msg = "Tags edited"
        return response

    def plugin_id(self):
        return "create"
