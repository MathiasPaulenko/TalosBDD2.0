Feature: test

  @mail
  Scenario: this is a mail demo
    Given login to the mail
      | param    | value              |
      | mail     | from_mail          |
      | password | pass               |
      | server   | smtp.office365.com |
    When get the last '1' emails
    When send new mail
      | param   | value                                     |
      | to      | to_mail                                   |
      | subject | Test                                      |
      | msg     | This is another one test <b>talosbdd!</b> |
    And logout mail