Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

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
    And I set the "Name" to "Fidget Spinner"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fidget Spinner" in the "Name" field
    And I should see "Toys" in the "Category" field
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
