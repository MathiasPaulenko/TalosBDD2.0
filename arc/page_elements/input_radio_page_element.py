# -*- coding: utf-8 -*-

from arc.page_elements.button_page_element import Button


class InputRadio(Button):
    @property
    def text(self):
        return self.web_element.get_attribute("value")

    def is_selected(self):
        return self.web_element.is_selected()

    def check(self):
        return self.click()
