import os
import shutil

from arc.settings import settings as pytalos_settings
from settings import settings

OUTPUT_BASEDIR = pytalos_settings.OUTPUT_PATH
SETTINGS_BASEDIR = pytalos_settings.SETTINGS_PATH
PROJECT_BASEDIR = pytalos_settings.BASE_PATH


def generate_needed_dir(current_driver):
    try:
        if settings.PYTALOS_GENERAL['auto_generate_output_dir']:
            dir_json = os.path.join(OUTPUT_BASEDIR, 'json')
            dir_logs = os.path.join(OUTPUT_BASEDIR, 'logs')
            dir_reports = os.path.join(OUTPUT_BASEDIR, 'reports')
            dir_screenshots = os.path.join(OUTPUT_BASEDIR, 'screenshots')
            dir_info = os.path.join(OUTPUT_BASEDIR, 'info')

            dir_json_input = os.path.join(dir_json, 'input')
            dir_json_output = os.path.join(dir_json, 'output')
            dir_reports_html = os.path.join(dir_reports, 'html')
            dir_reports_doc = os.path.join(dir_reports, 'doc')

            if not os.path.isdir(OUTPUT_BASEDIR):
                os.mkdir(OUTPUT_BASEDIR)
            if not os.path.isdir(dir_json):
                os.mkdir(dir_json)
            if not os.path.isdir(dir_logs):
                os.mkdir(dir_logs)
            if not os.path.isdir(dir_reports):
                os.mkdir(dir_reports)
            if not os.path.isdir(dir_screenshots):
                os.mkdir(dir_screenshots)
            if not os.path.isdir(dir_json_input):
                os.mkdir(dir_json_input)
            if not os.path.isdir(dir_info):
                os.mkdir(dir_info)
            if not os.path.isdir(dir_json_output):
                os.mkdir(dir_json_output)

            if not os.path.isdir(SETTINGS_BASEDIR):
                os.mkdir(SETTINGS_BASEDIR)
            if not os.path.isdir(dir_reports_html):
                os.mkdir(dir_reports_html)
            if not os.path.isdir(dir_reports_doc):
                os.mkdir(dir_reports_doc)

        if settings.PYTALOS_GENERAL['auto_generate_test_dir']:
            dir_test = pytalos_settings.TEST_PATH
            if not os.path.isdir(dir_test):
                os.mkdir(dir_test)

            dir_steps = os.path.join(pytalos_settings.TEST_PATH, 'steps')
            dir_features = os.path.join(pytalos_settings.TEST_PATH, 'features')
            dir_helpers = os.path.join(pytalos_settings.TEST_PATH, 'helpers')

            if not os.path.isdir(dir_steps):
                os.mkdir(dir_steps)
            if not os.path.isdir(dir_features):
                os.mkdir(dir_features)
            if not os.path.isdir(dir_helpers):
                os.mkdir(dir_helpers)

            if str(current_driver).lower() not in ['api', 'backend', 'service']:
                dir_helpers_page_objects = os.path.join(pytalos_settings.TEST_PATH, 'helpers/page_objects')
                if not os.path.isdir(dir_helpers_page_objects):
                    os.mkdir(dir_helpers_page_objects)

            if str(current_driver).lower() in ['api', 'backend', 'service']:
                dir_helpers_api_objects = os.path.join(pytalos_settings.TEST_PATH, 'helpers/api_objects')
                if not os.path.isdir(dir_helpers_api_objects):
                    os.mkdir(dir_helpers_api_objects)
    except (Exception,) as ex:
        print(ex)
        pass


def delete_old_reports():
    shutil.rmtree(OUTPUT_BASEDIR, ignore_errors=True)


def enable_delete_old_reports(activate):
    if activate:
        delete_old_reports()
