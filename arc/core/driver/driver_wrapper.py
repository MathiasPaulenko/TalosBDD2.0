# -*- coding: utf-8 -*-

import os
import logging.config
import screeninfo

from arc.core.config_manager import CustomConfigParser
from arc.core.driver.driver_manager import DriverManager
from arc.core.driver.driver_setup import SetupDriver
from arc.contrib.utilities import get_valid_filename, Utils


class DriverWrapper(object):
    driver = None
    config = CustomConfigParser()
    utils = None
    app_strings = None
    session_id = None
    server_type = None
    remote_node = None
    remote_node_video_enabled = False
    logger = None

    config_properties_filenames = None
    config_log_filename = None
    output_log_filename = None
    visual_baseline_directory = None
    baseline_name = None

    def __init__(self):
        if not DriverManager.is_empty():
            default_wrapper = DriverManager.get_default_wrapper()
            self.config = default_wrapper.config.deepcopy()
            self.logger = default_wrapper.logger
            self.config_properties_filenames = default_wrapper.config_properties_filenames
            self.config_log_filename = default_wrapper.config_log_filename
            self.output_log_filename = default_wrapper.output_log_filename
            self.visual_baseline_directory = default_wrapper.visual_baseline_directory
            self.baseline_name = default_wrapper.baseline_name

        self.utils = Utils(self)
        DriverManager.add_wrapper(self)

    def configure_logger(self, tc_config_log_filename=None, tc_output_log_filename=None):
        config_log_filename = DriverManager.get_configured_value('Config_log_filename', tc_config_log_filename,
                                                                 'logging.conf')
        config_log_filename = os.path.join(DriverManager.config_directory, config_log_filename)

        if self.config_log_filename != config_log_filename:
            output_log_filename = DriverManager.get_configured_value('Output_log_filename', tc_output_log_filename,
                                                                     'pytalos.log')
            output_log_filename = os.path.join(DriverManager.output_directory, output_log_filename)
            output_log_filename = output_log_filename.replace('\\', '\\\\')

            try:
                logging.config.fileConfig(config_log_filename, {'logfilename': output_log_filename}, False)
            except Exception as exc:
                print("[WARN] Error reading logging config file '{}': {}".format(config_log_filename, exc))
            self.config_log_filename = config_log_filename
            self.output_log_filename = output_log_filename
            self.logger = logging.getLogger(__name__)

    def configure_properties(self, tc_config_prop_filenames=None, behave_properties=None):
        prop_filenames = DriverManager.get_configured_value('Config_prop_filenames', tc_config_prop_filenames,
                                                            'properties.cfg;local-properties.cfg')
        prop_filenames = [os.path.join(DriverManager.config_directory, filename) for filename in
                          prop_filenames.split(';')]
        prop_filenames = ';'.join(prop_filenames)

        if self.config_properties_filenames != prop_filenames:
            self.config = CustomConfigParser.get_config_from_file(prop_filenames)
            self.config_properties_filenames = prop_filenames

        self.config.update_properties(os.environ)

        if behave_properties:
            self.config.update_properties(behave_properties)

    def configure_visual_baseline(self):
        baseline_name = self.config.get_optional('VisualTests', 'baseline_name', '{Driver_type}')
        for section in self.config.sections():
            for option in self.config.options(section):
                option_value = self.config.get(section, option)
                baseline_name = baseline_name.replace('{{{0}_{1}}}'.format(section, option), option_value)

        if self.baseline_name != baseline_name:
            self.baseline_name = baseline_name
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          get_valid_filename(baseline_name))

    def update_visual_baseline(self):
        if '{PlatformVersion}' in self.baseline_name:
            try:
                platform_version = self.driver.desired_capabilities['platformVersion']
            except KeyError:
                platform_version = None
            self.baseline_name = self.baseline_name.replace('{PlatformVersion}', str(platform_version))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

        if '{Version}' in self.baseline_name:
            try:
                splitted_version = self.driver.desired_capabilities['version'].split('.')
                version = '.'.join(splitted_version[:2])
            except KeyError:
                version = None
            self.baseline_name = self.baseline_name.replace('{Version}', str(version))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

        if '{RemoteNode}' in self.baseline_name:
            self.baseline_name = self.baseline_name.replace('{RemoteNode}', str(self.remote_node))
            self.visual_baseline_directory = os.path.join(DriverManager.visual_baseline_directory,
                                                          self.baseline_name)

    def configure(self, tc_config_files, is_selenium_test=True, behave_properties=None):
        DriverManager.configure_common_directories(tc_config_files)
        self.configure_logger(tc_config_files.config_log_filename, tc_config_files.output_log_filename)
        self.configure_properties(tc_config_files.config_properties_filenames, behave_properties)

        if is_selenium_test:
            driver_info = self.config.get('Driver', 'type')
            DriverManager.configure_visual_directories(driver_info)
            self.configure_visual_baseline()

    def connect(self, maximize=True):
        if not self.config.get('Driver', 'type') or self.config.get('Driver', 'type') in ['api', 'no_driver', 'host']:
            return None

        self.driver = SetupDriver(self.config, self.utils).create_driver()
        self.session_id = self.driver.session_id
        self.server_type, self.remote_node = self.utils.get_remote_node()
        if self.server_type == 'grid':
            self.remote_node_video_enabled = self.utils.is_remote_video_enabled(self.remote_node)
        else:
            self.remote_node_video_enabled = True if self.server_type in ['ggr', 'selenoid'] else False

        if self.is_mobile_test() and not self.is_web_test() and self.config.getboolean_optional('Driver',
                                                                                                'appium_app_strings'):
            self.app_strings = self.driver.app_strings()

        if self.is_maximizable():
            bounds_x, bounds_y = self.get_config_window_bounds()
            self.driver.set_window_position(bounds_x, bounds_y)
            self.logger.debug('Window bounds: %s x %s', bounds_x, bounds_y)

            if maximize:
                window_width = self.config.get_optional('Driver', 'window_width')
                window_height = self.config.get_optional('Driver', 'window_height')
                if window_width and window_height:
                    self.driver.set_window_size(window_width, window_height)
                else:
                    self.driver.maximize_window()

        window_size = self.utils.get_window_size()
        self.logger.debug('Window size: %s x %s', window_size['width'], window_size['height'])

        self.update_visual_baseline()
        self.utils.discard_logcat_logs()
        self.utils.set_implicitly_wait()

        return self.driver

    def get_config_window_bounds(self):
        bounds_x = int(self.config.get_optional('Driver', 'bounds_x') or 0)
        bounds_y = int(self.config.get_optional('Driver', 'bounds_y') or 0)

        monitor_index = int(self.config.get_optional('Driver', 'monitor') or -1)
        if monitor_index > -1:
            try:
                monitor = screeninfo.get_monitors()[monitor_index]
                bounds_x += monitor.x
                bounds_y += monitor.y
            except NotImplementedError:
                self.logger.warn('Current environment doesn\'t support get_monitors')

        return bounds_x, bounds_y

    def is_android_test(self):
        driver_name = self.config.get('Driver', 'type').split('-')[0]
        return driver_name == 'android'

    def is_ios_test(self):
        driver_name = self.config.get('Driver', 'type').split('-')[0]
        return driver_name in ('ios', 'iphone')

    def is_mobile_test(self):
        return self.is_android_test() or self.is_ios_test()

    def is_web_test(self):
        appium_browser_name = self.config.get_optional('AppiumCapabilities', 'browserName')
        return not self.is_mobile_test() or appium_browser_name not in (None, '')

    def is_android_web_test(self):
        return self.is_android_test() and self.is_web_test()

    def is_ios_web_test(self):
        return self.is_ios_test() and self.is_web_test()

    def is_maximizable(self):
        return not self.is_mobile_test()

    def should_reuse_driver(self, scope, test_passed, context=None):
        reuse_driver = self.config.getboolean_optional('Driver', 'reuse_driver')
        reuse_driver_session = self.config.getboolean_optional('Driver', 'reuse_driver_session')
        restart_driver_after_failure = (self.config.getboolean_optional('Driver', 'restart_driver_after_failure') or
                                        self.config.getboolean_optional('Driver', 'restart_driver_fail'))
        if context and scope == 'function':
            reuse_driver = reuse_driver or (hasattr(context, 'reuse_driver_from_tags')
                                            and context.pytalos.reuse_driver_from_tags)
        return (((reuse_driver and scope == 'function') or (reuse_driver_session and scope != 'session'))
                and (test_passed or not restart_driver_after_failure))

    def get_driver_platform(self):
        platform = ''
        if 'platform' in self.driver.desired_capabilities:
            platform = self.driver.desired_capabilities['platform']
        elif 'platformName' in self.driver.desired_capabilities:
            platform = self.driver.desired_capabilities['platformName']
        return platform
