# -*- coding: utf-8 -*-

import os
import logging
from six import moves


class BaseConfig:

    def __init__(self):
        self.logger = None
        self.config = None


class ConfigFiles:

    def __init__(self):
        self.config_directory = None
        self.output_directory = os.path.abspath("output") + os.sep + "logs"
        self.visual_baseline_directory = None
        self.config_properties_filenames = None
        self.config_log_filename = None
        self.output_log_filename = None

    def set_config_directory(self, config_directory):
        self.config_directory = config_directory

    def set_output_directory(self, output_directory):
        self.output_directory = output_directory

    def set_visual_baseline_directory(self, visual_baseline_directory):
        self.visual_baseline_directory = visual_baseline_directory

    def set_config_properties_filenames(self, *filenames):
        self.config_properties_filenames = ';'.join(filenames)

    def set_config_log_filename(self, filename):
        self.config_log_filename = filename

    def set_output_log_filename(self, filename):
        self.output_log_filename = filename


class CustomConfigParser(moves.configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def get_optional(self, section, option, default=None):
        try:
            return self.get(section, option)
        except (moves.configparser.NoSectionError, moves.configparser.NoOptionError):
            return default

    def getboolean_optional(self, section, option, default=False):
        try:
            return self.getboolean(section, option)
        except (moves.configparser.NoSectionError, moves.configparser.NoOptionError):
            return default

    def deepcopy(self):
        config_string = moves.StringIO()
        self.write(config_string)

        config_string.seek(0)

        config_copy = CustomConfigParser()
        config_copy.read_file(config_string)

        return config_copy

    def update_properties(self, new_properties):
        [self._update_property_from_dict(section, option, new_properties) for section in self.sections() for option in
         self.options(section)]

    def _update_property_from_dict(self, section, option, new_properties):
        try:
            property_name = f"{section}_{option}"
            self.set(section, option, new_properties[property_name])
        except KeyError:
            pass

    @staticmethod
    def get_config_from_file(conf_properties_files):
        config = CustomConfigParser()
        logger = logging.getLogger(__name__)

        found = False
        files_list = conf_properties_files.split(';')
        for conf_properties_file in files_list:
            result = config.read(conf_properties_file, encoding='utf8')
            if len(result) == 0:
                message = f"Properties config file not found: {conf_properties_file}"
                if len(files_list) == 1:
                    logger.error(message)
                    raise Exception(message)
                else:
                    logger.debug(message)

            else:
                logger.debug(f"Reading properties from file: {conf_properties_file}")

                found = True
        if not found:
            message = 'Any of the properties config files has been found'
            logger.error(message)
            raise Exception(message)

        return config
