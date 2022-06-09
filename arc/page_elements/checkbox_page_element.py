# -*- coding: utf-8 -*-

from arc.page_elements.button_page_element import Button


class Checkbox(Button):
    @property
    def text(self):
        return self.web_element.get_attribute("value")

    def is_selected(self):
        return self.web_element.is_selected()

    def check(self):
        if not self.is_selected():
            self.web_element.click()
        return self

    def uncheck(self):
        if self.is_selected():
            self.web_element.click()
        return self
