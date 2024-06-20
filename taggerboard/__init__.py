import os.path
import argparse

from . import core
from . import app

import apphelpers


def main():
    logger_helper = core.container.logger_helper()
    logger_helper.prepare_output_directory()
    logger_helper.configure()

    help = core.container.help()
    help.create_empty_help("app")
    help.read()
    app_help_text = help.get_help("app")

    locale_paths = core.container.locale_paths()
    cfg_helper = core.container.locale_cfg_helper()
    cfg_helper.create_cfg("default.board",
                          {})

    description = app_help_text

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    app_parser = subparsers.add_parser('app')
    app_parser.add_argument("-c", "--configuration", default=locale_paths.configuration_file("default.board"), help=str(locale_paths.configuration_file("default.board")))
    app_parser.set_defaults(func=app.ApplicationCLI.run)

    arguments = parser.parse_args()
    arguments.func(arguments)