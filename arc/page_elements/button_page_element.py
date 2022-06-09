# -*- coding: utf-8 -*-

from selenium.common.exceptions import StaleElementReferenceException
from arc.page_elements.page_element import PageElement


class Button(PageElement):
    @property
    def text(self):
        try:
            return self.web_element.text
        except StaleElementReferenceException:
            # Retry if element has changed
            return self.web_element.text

    def click(self):
        try:
            self.wait_until_clickable().web_element.click()
        except StaleElementReferenceException:
            # Retry if element has changed
            self.web_element.click()
        return self
