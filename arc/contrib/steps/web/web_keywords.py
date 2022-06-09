from behave import use_step_matcher, step
from arc.page_elements import Button
from selenium.webdriver.common.by import By

use_step_matcher("re")


#######################################################################################################################
#                                            Verifications Steps                                                      #
#######################################################################################################################
@step(u"verify the button with text '(?P<button_text>.+)' is visible")
def step_impl(context, button_text):
    """
    This step verifies that a button with the name given as a parameter is visible
    :example
        Then verify the button with text 'submit' is visible
    :
    :tag Web Verifications Steps:
    :param context:
    :param button_text:
    :return:
    """
    button = Button(By.XPATH, "//button[contains(text(),'" + button_text + "')]")
    button.wait_until_clickable()
    assert button.is_visible()
