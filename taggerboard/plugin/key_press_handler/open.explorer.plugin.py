import logging
import yapsy.IPlugin
import subprocess


class OpenExplorerHandler(yapsy.IPlugin.IPlugin):

    def handle(self, params):
        subprocess.Popen([f"explorer", f"{params.directory}"])

    def plugin_id(self):
        return "open.explorer"
