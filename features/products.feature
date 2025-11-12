Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name        | category | description         | price | image_url                 | availability | discontinued | favorited |
        | Sample Lamp | Home     | Adjustable LED lamp | 39.99 | https://img.example/lamp  | True         | False        | False     |
        | Sample Mug  | Kitchen  | Ceramic coffee mug  | 12.99 |                           | False        | False        | False     |

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
    And the "image_url" field should be empty
    And the "Available" dropdown should be reset
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Fidget Spinner" in the "Name" field
    And I should see "Toys" in the "Category" field
    And I should see "LED light-up spinner" in the "Description" field
    And I should see "9.99" in the "Price" field
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
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Desk Chair"
    And I set the "Category" to "Furniture"
    And I set the "Description" to "Ergonomic office chair"
    And I set the "Price" to "249.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Coffee Mug"
    And I set the "Category" to "Kitchen"
    And I set the "Description" to "Ceramic coffee mug"
    And I set the "Price" to "12.99"
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
    And I set the "Name" to "Sample Lamp"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Sample Lamp" in the results

    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Actions" button
    And I press the "Favorite" button
    Then I should see the message "Product has been marked as Favorite!"

Scenario: Unfavorite a product via Actions menu
    When I visit the "Home Page"
    And I set the "Name" to "Sample Lamp"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Sample Lamp" in the results

    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Actions" button
    And I press the "Favorite" button
    Then I should see the message "Product has been marked as Favorite!"

    When I press the "Actions" button
    And I press the "Unfavorite" button
    Then I should see the message "Product has been un-favorited!"

Scenario: Discontinue a product via Actions menu
    When I visit the "Home Page"
    And I set the "Name" to "Sample Mug"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Sample Mug" in the results

    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Actions" button
    And I press the "Discontinue" button
    Then I should see the message "Product has been Discontinued!"


Scenario: Filter by Name (exact match)
    When I visit the "Home Page"
    And I set the "Name" to "Fidget Spinner"
    And I set the "Category" to "Toys"
    And I set the "Description" to "LED light-up spinner"
    And I set the "Price" to "9.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Fidget Spinner"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fidget Spinner" in the results
    And I should not see "LED light-up spinner" for "Description" in any result
    And I should not see "Fidget Pro" in the results

Scenario: Filter by Category
    When I visit the "Home Page"
    And I set the "Name" to "Laptop"
    And I set the "Category" to "Electronics"
    And I set the "Description" to "High performance laptop"
    And I set the "Price" to "1299.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Desk Chair"
    And I set the "Category" to "Furniture"
    And I set the "Description" to "Ergonomic office chair"
    And I set the "Price" to "249.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Category" to "Electronics"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Laptop" in the results
    And I should not see "Desk Chair" in the results

Scenario: Filter by Availability
    When I visit the "Home Page"
    And I set the "Name" to "Coffee Mug"
    And I set the "Category" to "Kitchen"
    And I set the "Description" to "Ceramic coffee mug"
    And I set the "Price" to "12.99"
    And I select "False" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Coffee Mug" in the results
    And I should not see "True" for "Available" in any result
    And I should see exactly 2 result(s)

Scenario: Filter with multiple fields combined
    When I visit the "Home Page"
    And I set the "Name" to "Gaming Laptop"
    And I set the "Category" to "Electronics"
    And I set the "Description" to "RTX graphics"
    And I set the "Price" to "1899.00"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Gaming Laptop"
    And I set the "Category" to "Electronics"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Gaming Laptop" in the results
    And I should not see "Laptop" in the Name column of the results
    And I should not see "Desk Chair" in the results

Scenario: No matches found
    When I visit the "Home Page"
    And I set the "Name" to "Nonexistent Product"
    And I press the "Search" button
    Then I should see the message "No matching products found"

 Scenario: Read a Product by ID
    When I visit the "Home Page"
    And I set the "Name" to "Sample Lamp"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Sample Lamp" in the results
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Sample Lamp" in the "Name" field
    And I should see "Home" in the "Category" field
    And I should see "Adjustable LED lamp" in the "Description" field
    And I should see "39.99" in the "Price" field
    And I should see "https://img.example/lamp" in the "Image Url" field
    And I should see "True" in the "Available" dropdown

Scenario: Read a Non-existent Product
    When I visit the "Home Page"
    And I set the "Id" to "999999"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Reset pagination controls
    When I visit the "Home Page"
    And I set the "Page Number" to "5"
    And I set the "Items per Page" to "25"
    And I press the "Reset" button
    Then I should see the message "Pagination reset"
    And I should see "1" in the "Pagination page" field
    And I should see "10" in the "Pagination limit" field

Scenario: Pagination with no results on high page number
    When I visit the "Home Page"
    And I set the "Page Number" to "999"
    And I set the "Items per Page" to "10"
    And I press the "List All (Paginated)" button
    Then I should see the message "No products found on page 999"
    And I should see "No products available." in the results

Scenario: Paginate through products with page 1
    When I visit the "Home Page"
    And I set the "Name" to "Wireless Mouse"
    And I set the "Category" to "Electronics"
    And I set the "Price" to "29.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "USB Cable"
    And I set the "Category" to "Electronics"
    And I set the "Price" to "12.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Keyboard"
    And I set the "Category" to "Electronics"
    And I set the "Price" to "79.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Page Number" to "1"
    And I set the "Items per Page" to "2"
    And I press the "List All (Paginated)" button
    Then I should see the message "Success - Showing page 1 (2 items)"
    And I should see exactly 2 result(s)

Scenario: Paginate through products with page 2
    When I visit the "Home Page"
    And I set the "Name" to "Monitor Stand"
    And I set the "Category" to "Furniture"
    And I set the "Price" to "45.00"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Desk Organizer"
    And I set the "Category" to "Furniture"
    And I set the "Price" to "18.50"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Table Lamp"
    And I set the "Category" to "Home"
    And I set the "Price" to "35.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Wall Clock"
    And I set the "Category" to "Home"
    And I set the "Price" to "22.00"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Name" to "Picture Frame"
    And I set the "Category" to "Home"
    And I set the "Price" to "15.99"
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"

    When I press the "Clear" button
    And I set the "Page Number" to "2"
    And I set the "Items per Page" to "2"
    And I press the "List All (Paginated)" button
    Then I should see the message "Success - Showing page 2 (2 items)"
    And I should see exactly 2 result(s)