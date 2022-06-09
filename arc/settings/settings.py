import os
from pathlib import Path

# Automation resources settings and paths
BASE_PATH = Path(__file__).absolute().parent.parent.parent
SETTINGS_PATH = os.path.join(BASE_PATH, 'settings')
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')
TEST_PATH = os.path.join(BASE_PATH, 'test')
REPORTS_PATH = os.path.join(OUTPUT_PATH, 'reports')
DRIVERS_HOME = os.path.join(SETTINGS_PATH, 'drivers')

VS_MIDDLEWARE = 'pytalos/resources/talos-pcom.vbs'


""" Behave configurations """
# BEHAVE configuration
BEHAVE = {
    'color': True,
    'junit': False,
    'junit_directory': 'output/reports/html',
    'default_format': 'pretty',
    'format': [
        'pretty',
        'plain',
        'progress3',
        'json.pretty',
        'json',
        'rerun',
        'sphinx.steps',
        'steps',
        'steps.doc',
        'steps.usage',
        'tags',
        'tags.location',
    ],
    'show_skipped': False,
    'show_multiline': True,
    'stdout_capture': False,
    'stderr_capture': False,
    'log_capture': True,
    'logging_level': 'INFO',
    'logging_clear_handlers': True,
    'summary': True,
    'outfiles': [
        'output/logs/features_pretty.txt',
        'output/logs/features_plain.txt',
        'output/logs/features_progress.txt',
        'output/reports/report_json_pretty.json',
        'output/reports/report_json.json',
        'output/reports/scenario_failed.txt',
        'output/info/steps_rst',
        'output/info/steps_list.txt',
        'output/info/steps_definition.txt',
        'output/info/steps_usage.txt',
        'output/info/tags_usage.txt',
        'output/info/tags_location.txt',

    ],
    'show_source': True,
    'show_timings': True,
    'verbose': False,
    'more_formatters': {},
    'userdata': {}
}