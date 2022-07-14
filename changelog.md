### v2.0.2-BETA

- Added module to work with SFTP services.
  - SFTP Default Keywords added.
- Added functionality to update web drivers automatically.
  - You can tell it in the settings.py file if you want to update the drivers automatically or not.
  - Proxy update support.
- New reports added.
  - HTML execution report added.
    - Global report, by feature and by scenario.
  - JSON report with all the execution information.
  - Reports and logs of behave and others.
  - Automatic catalog of the steps in RST format.
  - The previous html unit reports are maintained.
- Added new types of drivers: services, backend, edgeie. API is no longer valid as driver type.
- Added new arguments for command execution:
  - Argument to proxy by putting --proxy http....
  - Argument to change environment of profiles files by putting --env cer
- Another little implementations:
  - The configuration of execution through proxy for api, services and web executions through the settings.py file has been improved.
- Bugs fixed.
  - Path to ALM connect resources jar fixed.
  - Path to VBS host middleware fixed.

### v2.0.1-BETA

- Added edge functionality for internet explore compatibility.
  - New valid driver types: edgeie in order to activate edge in ie explore compatibility.
  - IE and EDGE driver added
- Integration was added in the excel and csv profile files to make use of these formats to obtain data in the steps
- Bugs fixed

### v2.0.0-BETA

- The folder system has been restructured. The folders related to the test cases, such as features, steps, helpers, were unified in the Test folder.
- The core was optimized, increasing its speed and better managing the type of execution.
- The embedded virtual environment has been removed, now any version of python higher than 3.6 can be used. The library list is left free in the requirements.txt file.
- The versions of the most important libraries were increased, Selenium to version 4, Appium, requests, among others.
- Improved performance on Linux and Mac.
- New functionalities:

    - SQL Wrappers.
    - Writing and reading of Excel and CSV files.
    - Proxy settings for executions.
    - The default apis execution steps were improved.
    - More reports enabled.
    - Integration with Allure.
  
- Bugs fixed