from behave_webdriver.steps import *
import behave_webdriver


def before_all(context):
    context.browser = behave_webdriver.Firefox()
    # compatibility with some of the built-in steps from Behave
    context.behave_driver = context.browser


def before_scenario(context, scenario):
    # NOTE: If you ever change or update the fixtures, manually update
    # the contenttypes pk fields to id per https://stackoverflow.com/a/61407486
    # will also need to modify all of the auth.permission pk fields
    context.fixtures = ['tests/acceptance/data.json']


def after_all(context):
    # cleanup after tests run
    context.browser.quit()
