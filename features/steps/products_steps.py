# pylint: disable=function-redefined
# flake8: noqa
import os
import requests
from behave import given, when, then


@given("the server is started")
def step_impl(context):
    """Check that the server is started"""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.resp = requests.get(context.base_url + "/")
    assert context.resp.status_code == 200


@when('I visit the "home page"')
def step_impl(context):
    """Visit the Home Page"""
    context.resp = requests.get(context.base_url + "/")
    assert context.resp.status_code == 200


@then('I should see "{message}"')
def step_impl(context, message):
    """I should see a message"""
    assert message in str(context.resp.text)


@then('I should not see "{message}"')
def step_impl(context, message):
    """I should not see a message"""
    assert message not in str(context.resp.text)
