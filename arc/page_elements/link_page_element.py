# -*- coding: utf-8 -*-

from arc.page_elements.button_page_element import Button


class Link(Button):
    @property
    def href(self):
        return self.web_element.get_attribute("href")
