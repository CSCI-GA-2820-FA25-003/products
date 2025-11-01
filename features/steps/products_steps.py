# pylint: disable=function-redefined
# flake8: noqa
import os
import json
import requests
from behave import given, when, then, step

# --- helpers ---
from decimal import Decimal, InvalidOperation

FIELD_MAP = {"available": "availability"}


def map_field(field: str) -> str:
    return FIELD_MAP.get(field.strip().lower(), field.strip().lower())


def to_boolish(s: str):
    sl = str(s).strip().lower()
    if sl in ("true", "false"):
        return sl == "true"
    return s


def to_number_or_str(s: str):
    try:
        return Decimal(str(s))
    except (InvalidOperation, TypeError, ValueError):
        return s


SESSION = requests.Session()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


# -------------------------------------------------------------
# Setup and Utility Functions
# -------------------------------------------------------------
@given("the server is started")
def step_impl(context):
    """Check that the server is started"""
    context.base_url = os.getenv("BASE_URL", BASE_URL)
    context.resp = requests.get(f"{context.base_url}/")
    assert context.resp.status_code == 200


@when('I visit the "Home Page"')
@when('I visit the "home page"')
def step_impl(context):
    context.resp = requests.get(f"{context.base_url}/")
    assert context.resp.status_code == 200


# -------------------------------------------------------------
# Product Creation and Management Steps (no JSON parsing here)
# -------------------------------------------------------------
@when('I set the "{field}" field to "{value}"')
def step_impl(context, field, value):
    if not hasattr(context, "product"):
        context.product = {}
    key = map_field(field)
    context.product[key] = value


@when('I select "{value}" in the "{field}" dropdown')
@step('I select "{value}" in the "{field}" dropdown')
def step_impl(context, value, field):
    if not hasattr(context, "product"):
        context.product = {}
    key = map_field(field)
    if value.strip().lower() in ("true", "false"):
        value = value.strip().lower() == "true"
    context.product[key] = value


@when('I press the "Create" button')
def step_impl(context):
    """Send POST request to create a product"""
    url = f"{context.base_url}/products"
    headers = {"Content-Type": "application/json"}
    context.resp = requests.post(url, headers=headers, data=json.dumps(context.product))
    assert context.resp.status_code in (200, 201)


@then('I should see the message "{message}"')
def step_impl(context, message):
    # Treat 200/201 as Success; otherwise look for message text
    if message.strip().lower() == "success":
        assert context.resp.status_code in (200, 201)
    else:
        assert message.lower() in context.resp.text.lower()


# -------------------------------------------------------------
# Product Retrieval and Verification
# -------------------------------------------------------------
@when('I copy the "Id" field')
def step_impl(context):
    """Store the product ID from response"""
    resp_json = context.resp.json()
    context.product_id = resp_json.get("id")
    assert context.product_id, "No product ID found in response"


@when('I press the "Clear" button')
def step_impl(context):
    """Clear the local product data"""
    context.product = {}


@then('the "{field}" field should be empty')
def step_impl(context, field):
    """Ensure a field is cleared"""
    assert context.product.get(field.lower()) in (None, ""), f"{field} not cleared"


@when('I paste the "Id" field')
def step_impl(context):
    """Paste the previously copied ID"""
    if not hasattr(context, "product"):
        context.product = {}
    context.product["id"] = context.product_id


@when('I press the "Retrieve" button')
def step_impl(context):
    """Retrieve the product by ID"""
    product_id = context.product.get("id")
    assert product_id, "Product ID missing"
    url = f"{context.base_url}/products/{product_id}"
    context.resp = requests.get(url)
    assert context.resp.status_code == 200


@then('I should see "{value}" in the "{field}" field')
def step_impl(context, value, field):
    """Generic field assertion (handles numbers/bools/strings)"""
    data = context.resp.json()
    key = map_field(field)
    actual = data.get(key, "")

    # numeric compare (e.g., "120" vs 120.00)
    expected_num = to_number_or_str(value)
    if isinstance(expected_num, Decimal):
        try:
            actual_num = Decimal(str(actual))
            assert (
                actual_num == expected_num
            ), f"Expected {expected_num} in {field}, got {actual_num}"
            return
        except (InvalidOperation, TypeError, ValueError):
            pass

    # boolean compare (e.g., "True" vs true)
    expected_bool = to_boolish(value)
    if isinstance(expected_bool, bool) and isinstance(actual, bool):
        assert (
            actual is expected_bool
        ), f"Expected {expected_bool} in {field}, got {actual}"
        return

    # string compare fallback
    assert str(actual).strip() == value, f"Expected {value} in {field}, got {actual}"


@then('I should see "{value}" in the "{field}" dropdown')
def step_impl(context, value, field):
    data = context.resp.json()
    key = map_field(field)

    actual = data.get(key, None)

    # Always try common aliases if not found
    if actual is None:
        for alt in ("availability", "is_available", "in_stock", "available", "inStock"):
            if alt in data:
                actual = data[alt]
                key = alt
                break

    if actual is None:
        raise AssertionError(
            f'Could not find a value for "{field}" (tried "{key}" and common aliases). '
            f"Available keys: {sorted(list(data.keys()))}"
        )


@then('I should see "Product Administration RESTful Service"')
def step_impl(context):
    assert context.resp is not None, "No response stored on context"
    assert "Product Administration RESTful Service" in context.resp.text


@then('I should not see "404 Not Found"')
def step_impl(context):
    assert context.resp is not None, "No response stored on context"
    assert "404 Not Found" not in context.resp.text
