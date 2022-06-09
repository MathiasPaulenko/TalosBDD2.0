# -*- coding: utf-8 -*-

from arc.page_elements.page_element import PageElement


class InputText(PageElement):
    @property
    def text(self):
        return self.web_element.get_attribute("value")

    @text.setter
    def text(self, value):
        if self.driver_wrapper.is_ios_test() and not self.driver_wrapper.is_web_test():
            self.web_element.set_value(value)
        elif self.shadowroot:
            self.driver.execute_script('return document.querySelector("%s")'
                                       '.shadowRoot.querySelector("%s")'
                                       '.value = "%s"' % (self.shadowroot, self.locator[1], value))
        else:
            self.web_element.send_keys(value)

    def clear(self):
        self.web_element.clear()
        return self
