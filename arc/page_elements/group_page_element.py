# -*- coding: utf-8 -*-

import logging

from arc.core.driver.driver_manager import DriverManager
from arc.page_elements.page_element import PageElement
from arc.page_objects.page_object import PageObject


class Group(PageObject, PageElement):

    def __init__(self, by, value, parent=None, driver_wrapper=None, order=None, wait=False):
        super().__init__(driver_wrapper, wait)
        self.logger = logging.getLogger(__name__)
        self.locator = (by, value)
        self.parent = parent
        self.order = order
        self.wait = wait
        self.shadowroot = None
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
        self.init_page_elements()
        self.reset_object(self.driver_wrapper)

    def reset_object(self, driver_wrapper=None):
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        self._web_element = None
        for element in self._get_page_elements():
            element.reset_object(driver_wrapper)
            from arc.page_elements import PageElements
            if isinstance(element, (PageElement, PageElements)):
                # If element is not a page object, update element parent
                element.parent = self
