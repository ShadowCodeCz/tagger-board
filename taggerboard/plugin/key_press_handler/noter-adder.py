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
        self.refresh = False


class NoterAdderHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        tags = " ".join(params.tags)
        noter_path = os.path.join(params.directory, ".noter.json")
        cmd = f'tagger-adder app -p {noter_path} -t {tags}'
        print(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        response = Response()
        response.handler = self.plugin_id()
        response.short_msg = "Tagged note added"
        return response

    def plugin_id(self):
        return "noter.adder"
