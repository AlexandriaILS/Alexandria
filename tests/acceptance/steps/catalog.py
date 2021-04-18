# noinspection PyUnresolvedReferences
import behave
from behave_webdriver.steps import *


@given("I start at the homepage")
def step_impl(context):
    context.browser.get(context.get_url())


@when('I type "{text}" in the search box')
def step_impl(context, text):
    context.browser.find_element_by_id("mainSearchBar").send_keys(text)


@when("I submit the search box")
def step_impl(context):
    context.browser.find_element_by_id("searchForm").submit()


@when('I search for "{text}"')
def step_impl(context, text):
    context.execute_steps(
        u"""
        when I type "{}" in the search box
         and I submit the search box
    """.format(
            text
        )
    )


@when("I get {count} results")
@when("I get {count} result")
@then("I get {count} results")
@then("I get {count} result")
def step_impl(context, count):
    assert int(context.browser.find_element_by_id("resultCount").text) == int(count)
