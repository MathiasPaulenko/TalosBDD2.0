# -*- coding: utf-8 -*-

import logging
from appium import webdriver as appium_driver
from selenium import webdriver
from selenium.webdriver import Proxy
from selenium.webdriver.common.proxy import ProxyType

from arc.core import constants
from arc.core.config_manager import BaseConfig
from arc.core.driver.driver_capabilities import (
    get_driver_capabilities,
    add_driver_capabilities,
    create_firefox_profile,
    create_chrome_options
)
from arc.core.driver.driver_types import DriverTypes
from arc.contrib.utilities import get_message_exception


class SetupDriver(object):
    utilities = None
    driver_types = None
    base_config = BaseConfig()

    def __init__(self, config, utilities=None):
        self.base_config.logger = logging.getLogger(__name__)
        self.base_config.config = config
        self.utilities = utilities
        self.driver_types = DriverTypes(self.base_config, self.base_config.logger)

    def create_driver(self):
        driver = self.base_config.config.get('Driver', 'type')
        try:
            if self.base_config.config.getboolean_optional('Server', 'enabled'):
                self.base_config.logger.info(f"Creating remote driver: {driver}")
                driver = self._set_remote_driver()
            else:
                self.base_config.logger.info(f"Creating local driver: {driver}")
                driver = self._set_local_driver()

        except Exception as ex:
            error_message = get_message_exception(ex)
            self.base_config.logger.error(f"{driver.capitalize()} driver can not be launched: {error_message}")
            raise ex

        return driver

    def _set_remote_driver(self):
        server_url = f"{self.utilities.get_server_url()}/wd/hub"

        driver = self.base_config.config.get('Driver', 'type')
        driver_name = driver.split('-')[0]
        capabilities = get_driver_capabilities(driver_name)

        try:
            capabilities['version'] = driver.split('-')[1]
        except IndexError:
            pass

        try:
            platforms_list = {'xp': constants.XP,
                              'windows_7': constants.W7,
                              'windows_8': constants.W8,
                              'windows_10': constants.W10,
                              'linux': constants.LINUX,
                              'android': constants.ANDROID.upper(),
                              'mac': constants.MAC}
            capabilities['platform'] = platforms_list.get(driver.split('-')[3], driver.split('-')[3])
        except IndexError:
            pass

        if driver_name == constants.OPERA:
            capabilities['opera.autostart'] = True
            capabilities['opera.arguments'] = '-fullscreen'
        elif driver_name == constants.FIREFOX:
            capabilities['firefox_profile'] = create_firefox_profile(self.base_config).encoded
        elif driver_name == constants.CHROME:
            chrome_capabilities = create_chrome_options(self.base_config).to_capabilities()
            try:
                capabilities['goog:chromeOptions'] = chrome_capabilities["goog:chromeOptions"]
            except KeyError:
                capabilities['chromeOptions'] = chrome_capabilities["chromeOptions"]

        add_driver_capabilities(capabilities, 'Capabilities', self.base_config)

        if driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):

            add_driver_capabilities(capabilities, 'AppiumCapabilities', self.base_config)
            return appium_driver.Remote(command_executor=server_url, desired_capabilities=capabilities)
        else:
            return webdriver.Remote(command_executor=server_url, desired_capabilities=capabilities)

    def _set_local_driver(self):
        driver_type = self.base_config.config.get('Driver', 'type')
        driver_name = driver_type.split('-')[0]

        if driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
            driver = self._setup_appium()

        else:
            driver_setup = {
                'firefox': self.driver_types.firefox,
                'chrome': self.driver_types.chrome,
                'safari': self.driver_types.safari,
                'opera': self.driver_types.opera,
                'iexplore': self.driver_types.explorer,
                'edge': self.driver_types.edge,
                'phantomjs': self.driver_types.phantomjs
            }

            driver_setup_method = driver_setup.get(driver_name)

            if not driver_setup_method:
                raise Exception(f"Unknown driver {driver_name}")

            capabilities = get_driver_capabilities(driver_name)
            add_driver_capabilities(capabilities, 'Capabilities', self.base_config)

            try:
                if self.base_config.config.getboolean_optional('Driver', 'proxy'):
                    proxy_url = "http://proxyapps.gsnet.corp:80"
                    proxy = Proxy()
                    proxy.proxy_type = ProxyType.MANUAL
                    proxy.http_proxy = proxy_url
                    proxy.ssl_proxy = proxy_url
                    proxy.add_to_capabilities(capabilities)

            except (Exception,):
                pass

            driver = driver_setup_method(capabilities)

        return driver

    def _setup_appium(self):
        self.base_config.config.set('Server', 'host', '127.0.0.1')
        self.base_config.config.set('Server', 'port', '4723')
        return self._set_remote_driver()
