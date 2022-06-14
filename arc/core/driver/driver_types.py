# -*- coding: utf-8 -*-

import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from arc.core.driver.driver_capabilities import (
    add_firefox_arguments,
    create_firefox_profile,
    create_chrome_options
)
from arc.core.driver.driver_manager import DriverManager
from arc.settings import settings


class DriverTypes:

    def __init__(self, base_config, logger):
        self.logger = logger
        self.base_config = base_config

    @staticmethod
    def safari(capabilities):
        return webdriver.Safari(desired_capabilities=capabilities)

    def opera(self, capabilities):
        opera_driver = self.base_config.config.get('Driver', 'opera_driver_path')
        self.logger.debug(f"Opera driver path: {opera_driver}")
        return webdriver.Opera(executable_path=opera_driver, desired_capabilities=capabilities)

    def explorer(self, capabilities):
        explorer_driver = self.base_config.config.get('Driver', 'explorer_driver_path')
        self.logger.debug(f"Explorer driver path: {explorer_driver}")

        return webdriver.Ie(explorer_driver, capabilities=capabilities)

    def edge(self, capabilities):
        edge_driver = self.base_config.config.get('Driver', 'edge_driver_path')
        self.logger.debug(f"Edge driver path: {edge_driver}")

        return webdriver.Edge(edge_driver, capabilities=capabilities)

    def phantomjs(self, capabilities):
        phantomjs_driver = self.base_config.config.get('Driver', 'phantomjs_driver_path')
        self.logger.debug(f"Phantom driver path: {phantomjs_driver}")

        return webdriver.PhantomJS(executable_path=phantomjs_driver, desired_capabilities=capabilities)

    def firefox(self, capabilities):
        gecko_driver = self.base_config.config.get('Driver', 'gecko_driver_path')
        self.logger.debug(f"Gecko driver path: {gecko_driver}")

        firefox_binary = self.base_config.config.get_optional('Firefox', 'binary')

        options = Options()

        if self.base_config.config.getboolean_optional('Driver', 'headless'):
            self.logger.debug("Running Firefox in headless mode")
            options.add_argument('-headless')

        add_firefox_arguments(options, self.base_config)

        if firefox_binary:
            options.binary = firefox_binary

        log_path = os.path.join(DriverManager.output_directory, 'geckodriver.log')

        try:
            return webdriver.Firefox(
                firefox_profile=create_firefox_profile(self.base_config),
                capabilities=capabilities,
                executable_path=gecko_driver,
                options=options,
                log_path=log_path,
                service_log_path=log_path
            )
        except TypeError:
            return webdriver.Firefox(
                firefox_profile=create_firefox_profile(self.base_config),
                capabilities=capabilities,
                executable_path=gecko_driver,
                options=options,
            )

    def chrome(self, capabilities):
        chrome_driver = self.base_config.config.get('Driver', 'chrome_driver_path')
        self.logger.debug(f"Chrome driver path: {chrome_driver}")
        # TODO: ver si funciona en windows
        chrome_path = os.path.join(settings.DRIVERS_HOME, chrome_driver)
        return webdriver.Chrome(
            chrome_path,
            chrome_options=create_chrome_options(self.base_config),
            desired_capabilities=capabilities
        )
