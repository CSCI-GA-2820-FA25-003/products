######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import re
import logging
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

# For the products UI, input ids are prefixed with "product_"
ID_PREFIX = "product_"

# Common aliases for feature field names vs. HTML element IDs
ALIASES = {
    "Available": "Availability",
}

def normalize_field_name(name: str) -> str:
    """Normalize field names and apply alias mapping"""
    actual = ALIASES.get(name, name)
    return actual.lower().replace(" ", "_")

def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation"""
    filename = re.sub(r"[^\w\s]", "", filename)
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "{_page}"')
def step_impl(context, _page):
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    """Check the page body for specific text"""
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string in element.text, f'Expected to see "{text_string}" in page body'


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two functions simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# Button logic
##################################################################
@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# Field value checks
##################################################################
@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


##################################################################
# Dropdown reset check
##################################################################
@then('the "{element_name}" dropdown should be reset')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + normalize_field_name(element_name)
    select = Select(context.driver.find_element(By.ID, element_id))
    assert select.options[0].is_selected(), (
        f'Expected "{element_name}" dropdown to be reset (first option selected), '
        f'but selected="{select.first_selected_option.text.strip()}"'
    )

##################################################################
# Additional steps for Filter Scenarios
##################################################################

@then('I should not see "{text}" in the "{field}" field')
def step_impl(context, text, field):
    """Verify a text is not present in a specific input field"""
    element_id = ID_PREFIX + normalize_field_name(field)
    try:
        element = context.driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        raise AssertionError(f'Could not find field "{field}" (id={element_id})')

    value = element.get_attribute("value") or element.text or ""
    assert text not in value, (
        f'Expected NOT to see "{text}" in field "{field}", but saw: "{value}"'
    )


@then('I should not see "{value}" for "{column}" in any result')
def step_impl(context, value, column):
    """Ensure a given value does not appear in any search result table row for a specific column"""
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Find the header index first (if headers exist)
    header_index = None
    try:
        headers = rows[0].find_elements(By.TAG_NAME, "th")
        for idx, th in enumerate(headers):
            if th.text.strip().lower() == column.strip().lower():
                header_index = idx
                break
    except Exception:
        pass  # Table may not have header row

    for row in rows[1:]:  # skip header if present
        cells = row.find_elements(By.TAG_NAME, "td")
        if header_index is not None and header_index < len(cells):
            cell_text = cells[header_index].text.strip()
            assert value not in cell_text, (
                f'Found "{value}" in column "{column}" for row: "{cell_text}"'
            )
        else:
            # fallback: search whole row text
            assert value not in row.text, (
                f'Found "{value}" in result row: "{row.text}"'
            )


@then('I should see an empty results table')
def step_impl(context):
    """Verify that search results have no data rows"""
    table = context.driver.find_element(By.ID, "search_results")

    # Prefer only rows inside <tbody> if present (avoids header rows in <thead>)
    bodies = table.find_elements(By.TAG_NAME, "tbody")
    if bodies:
        data_rows = []
        for tbody in bodies:
            data_rows.extend(tbody.find_elements(By.TAG_NAME, "tr"))
    else:
        # Fallback: all <tr>, but skip the first if it's a header row
        all_rows = table.find_elements(By.TAG_NAME, "tr")
        # Detect a header row by presence of <th> cells in the first row
        if all_rows and all_rows[0].find_elements(By.TAG_NAME, "th"):
            data_rows = all_rows[1:]
        else:
            data_rows = all_rows

    def is_visible_data_row(row):
        # Skip rows explicitly hidden
        if not row.is_displayed():
            return False
        # If the row has only <th>, treat it as a header
        if row.find_elements(By.TAG_NAME, "th") and not row.find_elements(By.TAG_NAME, "td"):
            return False
        # Consider a row "visible" only if any TD has non-empty text
        tds = row.find_elements(By.TAG_NAME, "td")
        cell_text = " ".join(td.text.replace("\u00a0", " ").strip() for td in tds)
        return bool(cell_text.strip())

    visible_data_rows = [r for r in data_rows if is_visible_data_row(r)]

    assert len(visible_data_rows) == 0, (
        f"Expected empty results table, but found {len(visible_data_rows)} row(s): "
        f"{[r.text for r in visible_data_rows]}"
    )


##################################################################
# Precise table checking for Filter results
##################################################################

def _get_result_rows(context):
    table = context.driver.find_element(By.ID, "search_results")
    return table.find_elements(By.CSS_SELECTOR, "tr")

def _get_name_column_index(context):
    table = context.driver.find_element(By.ID, "search_results")
    header_cells = table.find_elements(By.CSS_SELECTOR, "th")
    for idx, cell in enumerate(header_cells):
        if cell.text.strip().lower() == "name":
            return idx
    # fallback: assume first column is Name if no headers
    return 0

def _get_names_from_results(context):
    rows = _get_result_rows(context)
    if len(rows) <= 1:
        return []  # no data rows found
    name_idx = _get_name_column_index(context)
    names = []
    for row in rows[1:]:  # skip header row
        cells = row.find_elements(By.CSS_SELECTOR, "td")
        if cells:
            names.append(cells[name_idx].text.strip())
    return names

@then('I should not see "{name}" in the Name column of the results')
def step_impl(context, name):
    names = _get_names_from_results(context)
    assert name not in names, f'Expected NOT to see "{name}", but saw rows: {names}'

@then('I should see only "{name}" in the results')
def step_impl(context, name):
    names = _get_names_from_results(context)
    assert names == [name], f'Expected only "{name}" but saw: {names}'

@then('I should see exactly {count:d} result(s)')
def step_impl(context, count):
    names = _get_names_from_results(context)
    assert len(names) == count, f"Expected {count} result(s), but saw {len(names)}: {names}"
