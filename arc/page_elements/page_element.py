# -*- coding: utf-8 -*-

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from arc.core.driver.driver_manager import DriverManager
from arc.page_objects.common_object import CommonObject
from arc.core.test_method.visual_test import VisualTest


class PageElement(CommonObject):
    _web_element = None

    def __init__(self, by, value, parent=None, order=None, wait=False, shadowroot=None):
        super(PageElement, self).__init__()
        self.locator = (by, value)
        self.parent = parent
        self.order = order
        self.wait = wait
        self.shadowroot = shadowroot
        self.driver_wrapper = DriverManager.get_default_wrapper()
        self.reset_object(self.driver_wrapper)

    def reset_object(self, driver_wrapper=None):
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        self._web_element = None

    @property
    def web_element(self):
        try:
            self._find_web_element()
        except NoSuchElementException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s not found"
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg))
            raise exception
        return self._web_element

    def _find_web_element(self):
        if not self._web_element or not self.config.getboolean_optional('Driver', 'save_web_element'):
            # If the element is encapsulated we use the shadowroot tag in yaml (eg. Shadowroot: root_element_name)
            if self.shadowroot:
                if self.locator[0] != By.CSS_SELECTOR:
                    raise Exception('Locator type should be CSS_SELECTOR using shadowroot but found: '
                                    '%s'.format(self.locator[0]))
                # querySelector only support CSS SELECTOR locator
                self._web_element = self.driver.execute_script('return document.querySelector("%s").shadowRoot.'
                                                               'querySelector("%s")' % (self.shadowroot,
                                                                                        self.locator[1]))
            else:
                # Element will be finded from parent element or from driver
                base = self.utils.get_web_element(self.parent) if self.parent else self.driver
                # Find elements and get the correct index or find a single element
                self._web_element = base.find_elements(*self.locator)[self.order] if self.order else base.find_element(
                    *self.locator)

    def scroll_element_into_view(self):
        x = self.web_element.location['x']
        y = self.web_element.location['y']
        self.driver.execute_script('window.scrollTo({0}, {1})'.format(x, y))
        return self

    def is_present(self):
        try:
            self._web_element = None
            self._find_web_element()
            return True
        except NoSuchElementException:
            return False

    def is_visible(self):
        return self.is_present() and self.web_element.is_displayed()

    def wait_until_visible(self, timeout=None):
        try:
            self.utils.wait_until_element_visible(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s not found or is not visible after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            raise exception
        return self

    def wait_until_not_visible(self, timeout=None):
        try:
            self.utils.wait_until_element_not_visible(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s is still visible after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            raise exception
        return self

    def wait_until_clickable(self, timeout=None):
        try:
            self.utils.wait_until_element_clickable(self, timeout)
        except TimeoutException as exception:
            parent_msg = " and parent locator '{}'".format(self.parent) if self.parent else ''
            msg = "Page element of type '%s' with locator %s%s not found or is not clickable after %s seconds"
            timeout = timeout if timeout else self.utils.get_explicitly_wait()
            self.logger.error(msg, type(self).__name__, self.locator, parent_msg, timeout)
            exception.msg += "\n  {}".format(msg % (type(self).__name__, self.locator, parent_msg, timeout))
            raise exception
        return self

    def assert_screenshot(self, filename, threshold=0, exclude_elements=None, force=False):
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(self.driver_wrapper, force).assert_screenshot(self.web_element, filename, self.__class__.__name__,
                                                                 threshold, exclude_elements)

    def get_attribute(self, name):
        """Get the given attribute or property of the element

        :param name: name of the attribute/property to retrieve
        :returns: attribute value
        """
        return self.web_element.get_attribute(name)
