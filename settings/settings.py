import os
from pathlib import Path

""" PyTalos configurations """
# Project configurations
BASE_PATH = Path(__file__).absolute().parent.parent
SETTINGS_PATH = os.path.join(BASE_PATH, 'settings')
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')

# Project and general configuration
PYTALOS_GENERAL = {
    'download_path': "path",
    'auto_generate_output_dir': True,
    'auto_generate_test_dir': True
}

# Run configuration
PYTALOS_RUN = {
    'delete_old_reports': True,
    'close_webdriver': True,
    'continue_after_failed_step': False,
    'close_host': True
}

# Reports configurations
PYTALOS_REPORTS = {
    'generate_html': True,
    'generate_docx': True,
    'generate_txt': True,
    'generate_screenshot': True,

}

# Profile datas configurations
PYTALOS_PROFILES = {
    'environment': 'cer',
    'master_file': 'master',
    'locale_fake_data': 'es_ES',
    'language': 'es'

}

# Step catalog configurations
PYTALOS_CATALOG = {
    'update_step_catalog': True,
    'excel_file_name': 'catalog',
    'steps': {
        'user_steps': False,
        'default_api': True,
        'default_web': True,
        'default_functional': True,
        'default_data': True,
        'default_ftp': True,
    }
}

""" Integrations """
# MF ALM integration configurations
PYTALOS_ALM = {
    'post_to_alm': False,
    'generate_json': True,
    'match_alm_execution': False,
    'alm3_properties': False,
}

# Jira integration configuration
PYTALOS_JIRA = {
    'post_to_jira': False,
    'username': 'user',
    'password': 'password',
    'base_url': 'https://jira.alm.europe.cloudcenter.corp',
    'report': {
        'comment_execution': True,
        'comment_scenarios': True,
        'upload_doc_evidence': True,
        'upload_txt_evidence': True,
        'upload_html_evidence': True,
    }
}

""" Behave configurations """
# BEHAVE configuration
BEHAVE = {
    'color': True,
    'junit': True,
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

}

""" BD Configurations"""
# SQLite configuration
SQLITE = {
    'enable': False,
    'sqlite_home': os.path.join(BASE_PATH, 'db.sqlite3')
}


# Behave init file path configuration
# BEHAVE_INIT_PATH = os.path.join(BASE_PATH, 'settings') + os.sep
