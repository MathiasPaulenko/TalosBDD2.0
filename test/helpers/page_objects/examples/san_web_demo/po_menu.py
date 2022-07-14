from selenium.webdriver.common.by import By

from arc.page_objects.page_object import PageObject
from arc.page_elements import *


class MenuPageObject(PageObject):
    btn__menu: Button
    lnk__shareholders_and_investors: Link
    lnk__santander_share: Link
    lnk__closing_markets: Link
    lnk__price: Link
    lnk__dividends: Link

    def init_page_elements(self):
        self.btn__menu = Button(By.XPATH, "//div[@class='hamburger']")
        self.lnk__shareholders_and_investors = Link(By.XPATH, "//a[@title='Shareholders and Investors']")
        self.lnk__santander_share = Link(By.XPATH, "//a[@title='Santander Share']")
        self.lnk__closing_markets = Link(By.XPATH, "//a[@title='Closing Markets']")
        self.lnk__price = Link(By.XPATH, "//a[@title='Price']")
        self.lnk__dividends = Link(By.XPATH, "//a[@title='Dividends']")

    def go_to_page(self, page, context):
        self.btn__menu.wait_until_clickable()
        self.btn__menu.click()
        self.lnk__shareholders_and_investors.wait_until_clickable()
        self.lnk__shareholders_and_investors.click()
        context.driver.implicitly_wait(3)
        self.lnk__santander_share.wait_until_visible()

        self.lnk__santander_share.click()

        if page == 'Closing Markets':
            self.lnk__closing_markets.wait_until_clickable()
            self.lnk__closing_markets.click()
        elif page == 'Price':
            self.lnk__price.wait_until_clickable()
            self.lnk__price.click()
        elif page == 'Dividends':
            self.lnk__dividends.wait_until_clickable()
            self.lnk__dividends.click()
