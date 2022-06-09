@host
Feature: host
  Demo Host Example

  Scenario: host automation
    Given open host emulator
    And wait for value 'Teclee' in row '23', column '2' and length '6'
    And put the value 'S' in row '24' and column '2' in emulator
    And press 'enter' key in emulator
    And wait for value 'KLGLGON1' in row '1', column '2' and length '8'
    And put the value 'user' in row '6' and column '30' in emulator
    And put the value 'pass' in row '7' and column '30' in emulator
    And press 'enter' key in emulator
    And wait for value 'Command' in row '23', column '2' and length '7'
    When put the value 'S TSOD' in row '23' and column '5' in emulator
    And press multiple keys in emulator
      | key   | interval |
      | enter | 0.5      |
      | enter | 0.5      |
      | enter | 0.5      |
    And put the value '2' in row '6' and column '38' in emulator
    And press 'enter' key in emulator
    And perform the following actions in the emulator
      | command | params     |
      | put     | =3.2;2;14  |
      | key     | enter      |
      | put     | A;4;14     |
      | put     | test;17;25 |
      | key     | enter      |
      | key     | enter      |
      | key     | pf3        |
      | key     | pf3        |
    And press 'pf3' key in emulator
    And put the value '2' in row '5' and column '25' in emulator
    And press 'enter' key in emulator

  Scenario: SAT Log
    Given open host emulator
    And wait for value 'Teclee' in row '23', column '2' and length '6'
    And put the value 'S' in row '24' and column '2' in emulator
    And press 'enter' key in emulator
    And put the value 'user' in row '6' and column '30' in emulator
    And put the value 'pass' in row '7' and column '30' in emulator