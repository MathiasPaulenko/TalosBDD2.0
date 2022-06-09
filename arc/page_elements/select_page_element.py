# -*- coding: utf-8 -*-

from selenium.webdriver.support.ui import Select as SeleniumSelect
from arc.page_elements import PageElement


class Select(PageElement):
    @property
    def option(self):
        return self.selenium_select.first_selected_option.text

    @option.setter
    def option(self, value):
        self.selenium_select.select_by_visible_text(value)

    @property
    def selenium_select(self):
        return SeleniumSelect(self.web_element)
