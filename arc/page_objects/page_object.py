# -*- coding: utf-8 -*-

from arc.core.driver.driver_manager import DriverManager
from arc.page_objects.common_object import CommonObject


class PageObject(CommonObject):
    app_strings = None

    def __init__(self, driver_wrapper=None, wait=False):
        super(PageObject, self).__init__()
        self.wait = wait
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
        self.init_page_elements()
        self.reset_object(self.driver_wrapper)

    def reset_object(self, driver_wrapper=None):
        if driver_wrapper:
            self.driver_wrapper = driver_wrapper
        self.app_strings = self.driver_wrapper.app_strings
        for element in self._get_page_elements():
            element.reset_object()

    def init_page_elements(self):
        pass

    def _get_page_elements(self):
        page_elements = []
        for attribute, value in list(self.__dict__.items()) + list(self.__class__.__dict__.items()):
            if attribute != 'parent' and isinstance(value, CommonObject):
                page_elements.append(value)
        return page_elements

    def wait_until_loaded(self, timeout=None):
        for element in self._get_page_elements():
            if hasattr(element, 'wait') and element.wait:
                from arc.page_elements import PageElement
                if isinstance(element, PageElement):
                    element.wait_until_visible(timeout)
                if isinstance(element, PageObject):
                    element.wait_until_loaded(timeout)
        return self
