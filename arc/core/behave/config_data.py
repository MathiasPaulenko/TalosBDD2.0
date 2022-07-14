import json
import os.path
from copy import deepcopy
from os import listdir
from arc.contrib.tools import files, excel, csv
from settings import settings


def get_datas(context):
    """Load and update userdata from JSON configuration file."""
    current_files = None
    try:
        json_total = {}
        env = settings.PYTALOS_PROFILES['environment']
        userdata = context.config.userdata
        list_files = [f for f in listdir(os.path.abspath("settings/profiles") + os.sep + env)
                      if os.path.isfile(os.path.join(os.path.abspath("settings/profiles") + os.sep + env, f))]

        for file in list_files:
            index = file.rfind('.')
            key_name = file[:index]
            if key_name in userdata:
                del userdata[key_name]

        assert list_files is not None

        for file in list_files:
            index = file.rfind('.')
            current_files = deepcopy(file)
            configfile = userdata.get(file[:index], os.path.abspath("settings/profiles") + os.sep + env + os.sep + file)
            if configfile.endswith(".json"):
                json_total[file[:index]] = json.load(open(configfile, encoding="utf8"))
            elif configfile.endswith(".yaml"):
                json_total[file[:index]] = files.yaml_to_dict(configfile)
            elif configfile.endswith(".xlsx"):
                excel_wrapper = excel.ExcelWrapper(configfile)
                excel_wrapper.set_all_sheets_header(1)
                json_total[file[:index]] = excel_wrapper.all_sheets_to_dict()
            elif configfile.endswith(".csv"):
                csv_wrapper = csv.CSVWrapper(configfile)
                csv_wrapper.set_sheet_header(1)
                json_total[file[:index]] = csv_wrapper.current_sheet_to_dict()
            else:
                pass
        context.config.update_userdata(json_total)

    except Exception as ex:
        print(f"Error in {current_files}: Data could not be imported.")
        print(f'Cause: {ex}')
        raise
