# noinspection PyUnresolvedReferences
# the behave import needs to be here otherwise pycharm won't recognize this
# as a valid step file :(
import time

import behave
from behave_webdriver.steps import *
from selenium.webdriver.common.keys import Keys


@when("I press enter")
def step_impl(context):
    context.browser.switch_to_active_element().send_keys(Keys.ENTER)


@then("I add a breakpoint")
@when("I add a breakpoint")
def step_impl(context):
    # NOTE: Remember to use --no-capture flag on behave when using this step!
    breakpoint()


@when("I win")
@then("I win")
def step_impl(context):
    # for stubbing out tests in progress
    ...
