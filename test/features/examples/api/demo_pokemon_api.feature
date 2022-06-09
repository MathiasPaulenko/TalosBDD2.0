@pokemon
Feature: api
  Demo Api Example

  @all_pokemons @JIRA-SGTQSTOOL-203
  Scenario Outline: request pokemon <pokemon>
  """
  Description of <pokemon> with ability <ability> and id <id>
  """
    Given prepare the uri 'https://pokeapi.co/api/v2/pokemon' request with path '<pokemon>'
    And prepare the method 'GET' request
    When send request
    Then verify simple value '<id>' of type 'integer' in key 'id'
    And verify value '<ability>' of type 'string' in path key 'abilities.0.ability.name'
    And verify status code is '200'
    And verify type value 'str' in path key 'abilities.0.ability.name'
    And verify status code is one of '200, 201, 202'
    And verify response time is between '0.01' and '10.503'

    @first_generation
    Examples: Pokemons first generation
      | pokemon | ability   | id  |
      | ditto   | limber    | 132 |
      | onix    | rock-head | 95  |

    @second_generation
    Examples: Pokemons second generation
      | pokemon   | ability  | id  |
      | chikorita | overgrow | 152 |
      | aipom     | run-away | 190 |

    @third_generation
    Examples: Pokemons third generation
      | pokemon  | ability  | id  |
      | sceptile | overgrow | 254 |
      | duskull  | levitate | 355 |

