from selenium.webdriver.common.by import By

from arc.page_objects.page_object import PageObject
from arc.page_elements import *


class SanPageObject(PageObject):
    # CLosingMarket
    btn__select_year: Button
    btn__select_month: Button
    lnk__first_pdf: Link
    # SearchPress
    btn__search_bar: Button
    btn__filter_by_date: Button
    sel__from_month: Select
    sel__from_year: Select
    sel__to_month: Select
    sel__to_year: Select
    btn__apply_filter: Button
    # Dividends
    btn__exercise: Button
    btn__execrise_year: Button

    def init_page_elements(self):
        # CLosingMarket
        self.btn__select_year = Button(By.XPATH, "//div[contains(@class, 'anio')]", wait=True)
        self.btn__select_month = Button(By.XPATH, "//div[contains(@class, 'mes')]", wait=True)
        self.lnk__first_pdf = Link(By.XPATH, "(//div[@class='demo-container']//following::a)[1]", wait=True)
        # SearchPress
        self.btn__search_bar = Button(By.ID, "tb-search-widget-button", wait=True)
        self.btn__filter_by_date = Button(By.XPATH, "//div[@class='fr-button']", wait=True)
        self.sel__from_month = Select(By.XPATH, "//label[text()='From']//following::select[1]", wait=True)
        self.sel__from_year = Select(By.XPATH, "//label[text()='From']//following::select[2]", wait=True)
        self.sel__to_month = Select(By.XPATH, "//label[text()='To']//following::select[1]", wait=True)
        self.sel__to_year = Select(By.XPATH, "//label[text()='To']//following::select[1]", wait=True)
        self.btn__apply_filter = Button(By.XPATH, "//button[text()='Apply']", wait=True)
        # Dividends
        self.btn__exercise = Button(By.XPATH, "(//div[contains(@class, 'dropdown__container--filter')])[2]", wait=True)

    def filter_by_year(self, year):
        self.btn__select_year.wait_until_clickable()
        self.btn__select_year.click()
        link_option = Link(By.XPATH, f"//div[contains(@class, 'anio')]//following::a[text()='{year}']", wait=True)
        link_option.wait_until_visible()
        link_option.click()

    def filter_by_month(self, month):
        self.btn__select_month.wait_until_clickable()
        self.btn__select_month.click()
        link_option = Link(By.XPATH, f"//div[contains(@class, 'mes')]//following::a[text()='{month}']", wait=True)
        link_option.wait_until_visible()
        link_option.click()

    def download_first_pdf(self):
        self.lnk__first_pdf.wait_until_clickable()
        self.lnk__first_pdf.click()

    def filter_by_date_in_press_room(self):
        self.btn__search_bar.wait_until_clickable()
        self.btn__search_bar.scroll_element_into_view()
        self.btn__search_bar.click()

        self.btn__filter_by_date.wait_until_clickable()
        self.btn__filter_by_date.scroll_element_into_view()
        self.btn__filter_by_date.click()

        self.sel__from_month.selenium_select.select_by_index(3)
        self.sel__from_year.selenium_select.select_by_index(3)
        self.sel__to_month.selenium_select.select_by_index(3)
        self.sel__to_year.selenium_select.select_by_index(3)

        self.btn__apply_filter.click()

    def filter_by_year_dividends(self, year):
        self.btn__exercise.wait_until_clickable()
        self.btn__exercise.scroll_element_into_view()
        self.btn__exercise.click()

        btn__excersise = Button(By.XPATH, f"//a[text()='{year}' and @id='{year}']", wait=True)
        btn__excersise.click()
