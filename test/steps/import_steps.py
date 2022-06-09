# try:
# API DEFAULT STEPS
from arc.contrib.steps.api import api_keywords  # import all default api keyword steps of TalosBDD
from arc.contrib.steps.general import datas_keywords  # import default datas steps of TalosBDD
from arc.contrib.steps.general import funcional_keywords  # import default funcional steps of TalosBDD
from arc.contrib.steps.general import ftp_keywords  # import default FTP steps of TalosBDD
from arc.contrib.steps.host import host_keywords  # import default FTP steps of TalosBDD

# USER STEPS
from test.steps.examples.web import web_demo
# except Exception as ex:
#     print(ex)
