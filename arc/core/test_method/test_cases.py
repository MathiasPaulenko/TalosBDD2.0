# -*- coding: utf-8 -*-

import logging
import sys
import unittest

from arc.core.config_manager import ConfigFiles
from arc.core.driver.driver_manager import DriverManager
from arc.page_elements import PageElement
from arc.core.test_method.visual_test import VisualTest
from arc.contrib.utilities import get_message_exception


class BasicTestCase(unittest.TestCase):
    config_files = ConfigFiles()
    driver_wrapper = None

    def __init__(self, method_name: str = ...):
        super().__init__(method_name)
        self._outcomeForDoCleanups = None
        self._outcome = None

    @classmethod
    def get_subclass_name(cls):
        return cls.__name__

    def get_method_name(self):
        # Split remove the test suffix added by ddt library
        return self._testMethodName.split('___')[0]

    def get_subclassmethod_name(self):
        return self.__class__.__name__ + "." + self.get_method_name()

    @classmethod
    def tearDownClass(cls):
        pass
        # change_all_jira_status()

    def setUp(self):
        # Configure logger and properties
        if not isinstance(self, SeleniumTestCase):
            # By default config directory is located in test path
            if not self.config_files.config_directory:
                self.config_files.set_config_directory(DriverManager.get_default_config_directory())

            self.driver_wrapper = DriverManager.get_default_wrapper()
            self.config_files = DriverManager.initialize_config_files(self.config_files)
            self.driver_wrapper.configure(self.config_files, is_selenium_test=False)
        # Get config and logger instances
        self.config = self.driver_wrapper.config
        self.logger = logging.getLogger(__name__)
        self.logger.info("Running new test: %s", self.get_subclassmethod_name())

    def tearDown(self):
        py2_exception = sys.exc_info()[1]
        try:
            # Python 3.4+
            exception_info = self._outcome.errors[-1][1] if len(self._outcome.errors) > 0 else None
            exception = exception_info[1] if exception_info else None
        except AttributeError:
            try:
                # Python 3.3
                exceptions_list = self._outcomeForDoCleanups.failures + self._outcomeForDoCleanups.errors
                exception = exceptions_list[0][1] if exceptions_list else None
            except AttributeError:
                # Python 2.7
                exception = py2_exception

        if not exception:
            self._test_passed = True
            self.logger.info("The test '%s' has passed", self.get_subclassmethod_name())
        else:
            self._test_passed = False
            error_message = get_message_exception(exception)
            self.logger.error("The test '%s' has failed: %s", self.get_subclassmethod_name(), error_message)


class SeleniumTestCase(BasicTestCase):
    driver = None
    utils = None

    @classmethod
    def tearDownClass(cls):
        super(SeleniumTestCase, cls).tearDownClass()
        DriverManager.close_drivers(scope='class', test_name=cls.get_subclass_name())

    def setUp(self):
        if not self.config_files.config_directory:
            self.config_files.set_config_directory(DriverManager.get_default_config_directory())

        self.driver_wrapper = DriverManager.connect_default_driver_wrapper(config_files=self.config_files)
        SeleniumTestCase.driver = self.driver_wrapper.driver
        self.utils = self.driver_wrapper.utils

        file_suffix = self.get_method_name()

        def assert_screenshot_page_element(self, filename, threshold=0, exclude_elements=None, force=False):
            if exclude_elements is None:
                exclude_elements = []
            VisualTest(self.driver_wrapper, force).assert_screenshot(self.web_element, filename, file_suffix,
                                                                     threshold, exclude_elements)

        PageElement.assert_screenshot = assert_screenshot_page_element

        # Call BasicTestCase setUp
        super(SeleniumTestCase, self).setUp()

    def tearDown(self):
        # Call BasicTestCase tearDown
        super(SeleniumTestCase, self).tearDown()
        # Close drivers
        DriverManager.close_drivers(scope='function', test_name=self.get_subclassmethod_name(),
                                    test_passed=self._test_passed)

    def assert_screenshot(self, element, filename, threshold=0, exclude_elements=None, driver_wrapper=None,
                          force=False):
        if exclude_elements is None:
            exclude_elements = []
        file_suffix = self.get_method_name()
        VisualTest(driver_wrapper, force).assert_screenshot(element, filename, file_suffix, threshold, exclude_elements)

    def assert_full_screenshot(self, filename, threshold=0, exclude_elements=None, driver_wrapper=None, force=False):
        if exclude_elements is None:
            exclude_elements = []
        file_suffix = self.get_method_name()
        VisualTest(driver_wrapper, force).assert_screenshot(None, filename, file_suffix, threshold, exclude_elements)


class AppiumTestCase(SeleniumTestCase):
    app_strings = None

    @property
    def driver(self):
        return SeleniumTestCase.driver

    def setUp(self):
        self.driver_wrapper = DriverManager.get_default_wrapper()
        if not self.driver_wrapper.driver and not self.config_files.config_directory:
            # By default config directory is located in test path
            self.config_files.set_config_directory(DriverManager.get_default_config_directory())

        super(AppiumTestCase, self).setUp()
        AppiumTestCase.app_strings = self.driver_wrapper.app_strings
