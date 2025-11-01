Feature: The pet store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Product Administration RESTful Service"
    And  I should not see "404 Not Found"

Scenario: Create a New Product
  When I visit the "Home Page"
  And I set the "Name" field to "Sneakers"
  And I set the "Category" field to "FOOTWEAR"
  And I set the "Description" field to "High-performance running shoes"
  And I set the "Price" field to "120"
  And I select "True" in the "Available" dropdown
  And I set the "image_url" field to "sneakers.sample.url"
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

  When I paste the "Id" field
  And I press the "Retrieve" button
  Then I should see the message "Success"
  And I should see "Sneakers" in the "Name" field
  And I should see "FOOTWEAR" in the "Category" field
  And I should see "High-performance running shoes" in the "Description" field
  And I should see "120" in the "Price" field
  And I should see "True" in the "Available" dropdown
  And I should see "sneakers.sample.url" in the "image_url" field