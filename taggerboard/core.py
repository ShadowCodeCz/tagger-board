import hashlib
import re
import json
import logging.config
import os
import glob
import apphelpers as app_helpers
import collections

from dependency_injector import containers, providers
from . import notificator
from . import tag
from . import plugin


class Container(containers.DeclarativeContainer):
    app_description = providers.Singleton(app_helpers.AppDescription, "tagger.board")
    locale_paths = providers.Singleton(app_helpers.LocalePaths, app_description)
    package_paths = providers.Singleton(app_helpers.PackagePaths, app_description(), os.path.dirname(__file__))
    logger_helper = providers.Singleton(app_helpers.LoggerHelper, app_description, locale_paths)
    logger = providers.Factory(logging.getLogger, name=logger_helper().logger_name())
    help = providers.Singleton(app_helpers.Help, locale_paths, logger)
    locale_cfg_helper = providers.Singleton(app_helpers.Configuration, locale_paths, logger)
    cfg = providers.Configuration()
    tagger_directories_index = providers.Singleton(dict)
    notifier = providers.Singleton(notificator.SingletonNotificationProvider)
    group_index = providers.Singleton(dict)


container = Container()


class ReFilterRule:
    def __init__(self):
        self.included = [[]]
        self.excluded = [[]]


class StatusResponse:
    def __init__(self):
        self.success = True
        self.short_msg = ""

class RecursiveTaggedDirectoriesLocator:
    def locate(self, root_directory):
        template = os.path.join(root_directory, "**", ".tagger.json")
        return [os.path.abspath(os.path.dirname(t)) for t in glob.glob(template, recursive=True)]


class TaggedItem:
    def __init__(self, path, tags):
        self.path = path
        self.tags = tags

        self.parsed_tags = []

    @property
    def mag(self):
        for t in self.tags:
            if "mag@" in t:
                return t

    @property
    def timestamp(self):
        for t in self.tags:
            if "timestamp@" in t:
                return t


class TaggedDirectoriesIndexBuilder:
    def __init__(self, filter):
        self.filter = filter
        self.tags_parser = tag.TagsParser()
        self.tags_sorter = TagSorter()

    def build(self, directories):
        index = {}
        items = self.tagged_items(directories)
        for item in self.filter.filter(items):
            index[item.mag] = item
        return index

    def tagged_items(self, directories):
        result = []
        for directory in directories:
            # TODO: Slow when filter change
            item = TaggedItem(directory, [])
            self.load_tags(item)
            item.parsed_tags = self.tags_parser.parse(item.tags)
            result.append(item)
        return result

    def load_tags(self, item):
        tagger_file = os.path.join(item.path, ".tagger.json")
        with open(tagger_file, "r") as f:
            item.tags = json.load(f)
            item.tags = self.tags_sorter.sort(item.tags)


class NoFilter:
    def filter(self, items):
        return items


class ReFilter:
    def __init__(self, rules):
        self.rules = rules

    def filter(self, items):
        included = self.include(items)
        excluded = self.exclude(included)
        return excluded

    def include(self, items):
        result = []
        for item in items:
            for re_tags_and_group in self.rules.included:
                if all([self.match(tag_expression, item.tags) for tag_expression in re_tags_and_group]):
                    if not item in result:
                        result.append(item)
                        continue
        return result

    def exclude(self, items):
        if self.rules.excluded == [[]]:
            return items

        result = []
        for item in items:
            exclude = False
            for re_tags_and_group in self.rules.excluded:
                if all([self.match(tag_expression, item.tags) for tag_expression in re_tags_and_group]):
                    exclude = True
                    break
            if not exclude:
                if not item in result:
                    result.append(item)
        return result

    def match(self, tag_expression, tags):
        for tag in tags:
            if re.search(tag_expression, tag):
                return True
        return False


class TaggedDirectoriesIndexRefresher:
    def refresh(self):
        index = container.tagger_directories_index()
        group_index = container.group_index()

        working_directory = container.cfg.working_directory()
        locator = RecursiveTaggedDirectoriesLocator()
        directories = locator.locate(working_directory)
        re_filter = ReFilter(self.re_rules())
        index_builder = TaggedDirectoriesIndexBuilder(re_filter)
        new_index = index_builder.build(directories)

        index.clear()
        index.update(**new_index)

        grouper = Grouper()

        sorted_groups = grouper.sorted_groups(new_index, container.cfg.filter.group())
        group_index.clear()
        group_index.update(**sorted_groups)

    def re_rules(self):
        rules = ReFilterRule()
        rules.included = container.cfg.filter.included()
        rules.excluded = container.cfg.filter.excluded()
        return rules


class Grouper:
    def __init__(self):
        pass

    def sorted_groups(self, index, group_tag):
        groups = collections.defaultdict(list)

        for _, item in index.items():
            tags_reader = tag.TagsReader(item.parsed_tags)
            group = tags_reader.read_tag_value(group_tag, "@unknow")
            groups[group].append(item)

        for key in groups:
            groups[key] = sorted(groups[key], key=lambda i: i.timestamp) # TODO: Add to config or gui

        return groups


class ProxyPlugin:
    # TODO: Create new tagged directory
    # TODO: Change working directory

    # TODO: Remove tagged directory
    # TODO: Edit tags
    # TODO: Run noter
    # TODO: [nice to have] Backup directory
    # TODO: [nice to have] Recursive unpacker
    # TODO: [nice to have] Export (zip)
    # TODO: [nice to have] Files reorg
    # TODO: Make print screen to tagged directory (& with specific name drive by variables - dialog)(& open Rectangle)
    # TODO: [nice to have] Hash lock
    # TODO: Encrypt
    # TODO: Decrypt
    # TODO: [nice to have] Help

    def __init__(self, plugin_directories, plugin_reg_exp, logger=container.logger()):
        self.logger = logger
        collector = plugin.YapsyRegExPluginCollector(plugin_directories, plugin_reg_exp)
        plugs = collector.collect()
        self.plugins_index = plugin.build_plugin_index(plugs, lambda p: p.plugin_id())

    def handle(self, params):
        handler = self.plugins_index.get(params.handler_id)
        if handler is None:
            self.logger.warning(f"ProxyPlugin: Handler '{params.handler_id}' does not exists")
        else:
            return handler.handle(params)


class KeyPressSpecificHandlerParams:
    def __init__(self):
        self.handler_id = None
        self.directory = None
        self.tags = []


class KeyPressHandlerParams:
    def __init__(self):
        self.key = None
        self.mags = []


class KeyPressHandler:
    def __init__(self, plugin_subdirectory="key_press_handler", plugin_reg_exp=".+.py$", logger=container.logger()):
        self.logger = logger
        self.plugin_subdirectory = plugin_subdirectory
        self.plugin_reg_exp = plugin_reg_exp
        self.key_mapping = container.cfg.key_mapping()
        self.tagger_directories_index = container.tagger_directories_index()

        locale_paths = container.locale_paths()
        package_paths = container.package_paths()

        plugin_directories = [
            os.path.join(locale_paths.plugin_directory(), self.plugin_subdirectory),
            os.path.join(package_paths.plugin_directory(), self.plugin_subdirectory)
        ]

        self.key_press_plugin_proxy = ProxyPlugin(plugin_directories, self.plugin_reg_exp)

    def handle(self, params):
        for mag in params.mags:
            tagger_directory = self.tagger_directories_index.get(mag)

            if tagger_directory is None:
                self.logger.warning(f"KeyPressHandler: Record of mag '{mag}' does not exists.")
                continue

            handler_id = self.key_mapping.get(self.remove_key_prefix(params.key))

            if handler_id is not None:
                try:
                    specific_handler_params = KeyPressSpecificHandlerParams()
                    specific_handler_params.handler_id = handler_id
                    specific_handler_params.directory = tagger_directory.path
                    specific_handler_params.tags = tagger_directory.tags
                    return self.key_press_plugin_proxy.handle(specific_handler_params)
                except Exception as e:
                    error_msg = f"Key handler {handler_id} failed"
                    self.logger.warning(error_msg)
                    error_status = StatusResponse()
                    error_status.short_msg = error_msg
                    error_status.success = False
                    return error_status

    def remove_key_prefix(self, key):
        return key.replace("Key_", "")

class TagSorter:
    def __init__(self):
        self.tags_order = container.cfg.tags_order()

    def sort(self, tags):
        sorted_tags = []
        remaining_strings = tags.copy()

        for pattern in self.tags_order:
            matched_indices = []
            for i, string in enumerate(remaining_strings):
                if re.search(pattern, string):
                    sorted_tags.append(string)
                    matched_indices.append(i)

            for i in sorted(matched_indices, reverse=True):
                del remaining_strings[i]

        sorted_tags.extend(remaining_strings)

        return sorted_tags
