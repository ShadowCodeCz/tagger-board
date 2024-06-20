import os
import datetime
import logging
import shutil

import yapsy.IPlugin
import subprocess


class Response:
    def __init__(self):
        self.success = True
        self.short_msg = ""
        self.handler = ""
        self.refresh = True


class DeleteHandler(yapsy.IPlugin.IPlugin):
    def handle(self, params):
        # file_template = os.path.join(params.directory, ".tagger.json")

        cmd = f'backuper -p {params.directory}'
        print(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.wait()


        response = Response()
        response.refresh = True
        response.handler = self.plugin_id()

        try:
            shutil.rmtree(params.directory)
            response.short_msg = f"Directory {params.directory} backuped and removed"
            return response
        except Exception as e:
            response.short_msg = f"Removing directory {params.directory} failed"
            return response

    def plugin_id(self):
        return "delete"
