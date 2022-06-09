import json
import os.path
from copy import deepcopy
from os import listdir
from arc.contrib.tools import files
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
            key_name = file[:-5]
            if key_name in userdata:
                del userdata[key_name]

        assert list_files is not None

        for file in list_files:
            current_files = deepcopy(file)
            configfile = userdata.get(file[:-5], os.path.abspath("settings/profiles") + os.sep + env + os.sep + file)
            if configfile.endswith(".json"):
                json_total[file[:-5]] = json.load(open(configfile, encoding="utf8"))
            elif configfile.endswith(".yaml"):
                json_total[file[:-5]] = files.yaml_to_dict(configfile)
            else:
                pass
        context.config.update_userdata(json_total)

    except Exception as ex:
        print(f"Error in {current_files}: Data could not be imported.")
        print(f'Cause: {ex}')
        raise
