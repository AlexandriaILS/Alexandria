Feature: Checking the homepage

  Scenario: Verify search functionality
    Given I start at the homepage
    When I type "e" in the search box
    And I press enter
    And I pause for 100ms
    Then I get 3 results

  Scenario: Search for something that isn't in the catalog
    Given I start at the homepage
    When I type "asdfasdfasdf" in the search box
    And I press enter
    And I pause for 100ms
    Then I get 0 results

  Scenario: Search for something specific in the catalog
    Given I start at the homepage
    When I type "ender's game" in the search box
    And I press enter
    And I pause for 100ms
    Then I get 1 result

