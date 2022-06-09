@san_web
Feature: demo
  demo of santander.com home

  Background:
    Given access the web application '{{web}}'
    And accept all cookies

  @san_web1
  Scenario:  Closing Markets
    And go to the 'Closing Markets' page
    When filter for the year '2019' in Closing Markets
    And filter for the month 'October' in Closing Markets
    Then open the first PDF

  @san_web2
  Scenario:  Navigation
    Given go to the 'Price' page
    Then check if the title is 'Price'
    When choose the link from the top menu 'Press Room'
    And filter press by date
    And go to Home
    Given go to the 'Dividends' page
    And filter for the year '2018' in Dividens