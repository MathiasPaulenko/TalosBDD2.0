# -*- coding: utf-8 -*-

from arc.page_elements.page_element import PageElement


class Text(PageElement):
    @property
    def text(self):
        return self.web_element.text
