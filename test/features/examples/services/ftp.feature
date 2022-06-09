Feature: test

  @ftp
  Scenario: this is a ftp demo
    Given connect to FTP host with data table
      | param    | value                     |
      | host     | ftp.dlptest.com           |
      | username | dlpuser                   |
      | password | rNrKYTX9g7z3RgJRmxWuGHbeu |
      | secure   | False                     |
    When create directory '/test4/'
    Then close FTP connection

