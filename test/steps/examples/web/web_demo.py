from allure_commons._allure import attach
from allure_commons.types import AttachmentType
from behave import use_step_matcher, step
from selenium.webdriver.common.by import By

from arc.page_elements import Button, Text, Link
from test.helpers.pageobjects.examples.san_web_demo.po_san import SanPageObject
from test.helpers.pageobjects.examples.san_web_demo.po_menu import MenuPageObject

use_step_matcher("re")


@step("access the web application '(?P<url>.+)'")
def test(context, url):
    url = context.func.get_template_var_value(url, 'datas')
    context.driver.get(url)


@step("accept all cookies")
def test(context):
    try:
        btn__accept_cookies = Button(By.ID, 'consent_prompt_submit')
        btn__accept_cookies.wait_until_visible()
        btn__accept_cookies.click()
    except (Exception,):
        pass

    attach(
        context.driver.get_screenshot_as_png(),
        name="Screenshot",
        attachment_type=AttachmentType.PNG
    )


@step("go to the '(?P<page>.+)' page")
def test(context, page):
    po_menu = MenuPageObject()
    po_menu.go_to_page(page, context)


@step("filter for the year '(?P<option>.+)' in Closing Markets")
def test(context, option):
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_year(option)


@step("filter for the month '(?P<option>.+)' in Closing Markets")
def test(context, option):
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_month(option)


@step("open the first PDF")
def test(context):
    po_closing_market = SanPageObject()
    po_closing_market.download_first_pdf()


@step("check if the title is '(?P<value>.+)'")
def test(context, value):
    title = Text(By.XPATH, f"//h1[text()='{value}']")
    title.wait_until_visible()
    title.scroll_element_into_view()
    assert title.text == value


@step("choose the link from the top menu '(?P<value>.+)'")
def test(context, value):
    menu_link = Link(By.XPATH, f"//ul[@class='header__quicklinks-container']//child::a[contains(text(), '{value}')]")
    menu_link.wait_until_clickable()
    menu_link.scroll_element_into_view()
    menu_link.click()


@step("filter press by date")
def test(context):
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_date_in_press_room()


@step("filter for the year '(?P<year>.+)' in Dividens")
def test(context, year):
    po_closing_market = SanPageObject()
    po_closing_market.filter_by_year_dividends(year)


@step("go to Home")
def test(context):
    Link(By.XPATH, "//a[@class='header-logo__url']").click()