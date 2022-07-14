import os
import shutil
from subprocess import call

from settings import settings

ALM3_PROP_PATH = os.path.abspath("resources")
JSON_INPUT_PATH = os.path.abspath("output") + os.sep + 'json' + os.sep + 'input' + os.sep


def alm3_properties(flag):
    alm_file = 'alm.properties'
    if flag:
        alm_prop = os.path.join(ALM3_PROP_PATH, alm_file)
        shutil.copy(alm_prop, JSON_INPUT_PATH)
    else:
        alm_json_path = os.path.join(JSON_INPUT_PATH, alm_file)
        if os.path.isfile(alm_json_path):
            os.remove(alm_json_path)


def run_alm_connect():
    if settings.PYTALOS_ALM['post_to_alm']:
        jar_path = 'arc/resources/'
        json_path = 'output/json/'
        alm3_properties(settings.PYTALOS_ALM['alm3_properties'])
        call(['java', '-jar', jar_path + 'talos-alm-connect-5.01.jar', json_path])
