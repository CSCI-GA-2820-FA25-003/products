Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name        | category | description         | price | image_url                 | availability | discontinued | favorited | sku     |
        | Sample Lamp | Home     | Adjustable LED lamp | 39.99 | https://img.example/lamp  | True         | False        | False     | LMP-001 |
        | Sample Mug  | Kitchen  | Ceramic coffee mug  | 12.99 |                           | False        | False        | False     | MUG-001 |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Product Administration RESTful Service"
    And  I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Fidget Spinner"
    And I set the "Category" to "Toys"
    And I set the "Description" to "LED light-up spinner"
    And I set the "Price" to "9.99"
    And I set the "SKU" to "FS-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "SKU" field should be empty
    And the "Available" dropdown should be reset
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Fidget Spinner" in the "Name" field
    And I should see "Toys" in the "Category" field
    And I should see "LED light-up spinner" in the "Description" field
    And I should see "9.99" in the "Price" field
    And I should see "FS-001" in the "SKU" field
    And I should see "True" in the "Available" dropdown

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "Sample Lamp"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Sample Lamp" in the "Name" field
    And I should see "Home" in the "Category" field
    When I change "Name" to "Fidget Pro"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Fidget Pro" in the "Name" field
    When I press the "Clear" button
    And I set the "Name" to "Fidget Pro"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fidget Pro" in the results
    And I should not see "Fidget Spinner" in the results

Scenario: Delete an existing product
    When I visit the "Home Page"
    And I set the "Name" to "iPhone 17"
    And I set the "Category" to "Electronics"
    And I set the "Description" to "Latest Apple smartphone"
    And I set the "Price" to "1299.99"
    And I set the "SKU" to "IP17-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "iPhone 17"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "iPhone 17" in the results

    When I press the "Delete" button
    Then I should see the message "Product has been Deleted!"

    When I press the "Clear" button
    And I set the "Name" to "iPhone 17"
    And I press the "Search" button
    Then I should see the message "No matching products found."


Scenario: List all products
    When I visit the "Home Page"
    And I set the "Name" to "Laptop"
    And I set the "Category" to "Electronics"
    And I set the "Description" to "High performance laptop"
    And I set the "Price" to "1299.99"
    And I set the "SKU" to "LAP-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Desk Chair"
    And I set the "Category" to "Furniture"
    And I set the "Description" to "Ergonomic office chair"
    And I set the "Price" to "249.99"
    And I set the "SKU" to "CHR-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Coffee Mug"
    And I set the "Category" to "Kitchen"
    And I set the "Description" to "Ceramic coffee mug"
    And I set the "Price" to "12.99"
    And I set the "SKU" to "MUG-001"
    And I select "False" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I press the "List All" button
    Then I should see the message "Success"
    And I should see "Laptop" in the results
    And I should see "Desk Chair" in the results
    And I should see "Coffee Mug" in the results
    And I should see "1299.99" in the results
    And I should see "249.99" in the results
    And I should see "12.99" in the results


Scenario: Favorite a product via Actions menu
    When I visit the "Home Page"
    And I set the "Name" to "Desk Lamp"
    And I set the "Category" to "Home"
    And I set the "Description" to "Adjustable LED lamp"
    And I set the "Price" to "39.99"
    And I set the "SKU" to "LMP-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Actions" button
    And I press the "Favorite" button
    Then I should see the message "Product has been marked as Favorite!"

Scenario: Unfavorite a product via Actions menu
    When I visit the "Home Page"
    And I set the "Name" to "Mouse Pad"
    And I set the "Category" to "Accessories"
    And I set the "Description" to "Non-slip mouse pad"
    And I set the "Price" to "7.99"
    And I set the "SKU" to "MSP-001"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Actions" button
    And I press the "Favorite" button
    Then I should see the message "Product has been marked as Favorite!"

    When I press the "Actions" button
    And I press the "Unfavorite" button
    Then I should see the message "Product has been un-favorited!"